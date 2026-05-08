import csv
import smtplib
from pathlib import Path
from typing import Dict, Iterable, List, Optional, TextIO

import dns.resolver
from lark import Lark, exceptions

__all__ = [
    "validate_email_address",
    "validate_email",
    "resolve_mx",
    "smtp_verify_address",
    "bulk_validate_csv",
]

_GRAMMAR_PATH = Path(__file__).with_name("email_grammar.lark")

try:
    _GRAMMAR_TEXT = _GRAMMAR_PATH.read_text(encoding="utf-8")
except FileNotFoundError as exc:
    raise RuntimeError(
        f"Email grammar file not found at {_GRAMMAR_PATH}. "
        "Make sure email_grammar.lark is present in the project root."
    ) from exc

_EMAIL_PARSER = Lark(_GRAMMAR_TEXT, parser="lalr", start="start")


def validate_email_address(email: str) -> bool:
    """Return True when the given email matches the grammar."""
    if not isinstance(email, str):
        return False

    email = email.strip()
    if not email:
        return False

    try:
        _EMAIL_PARSER.parse(email)
        return True
    except exceptions.LarkError:
        return False


def _extract_domain(email: str) -> Optional[str]:
    if not isinstance(email, str) or "@" not in email:
        return None

    domain = email.rsplit("@", 1)[1].strip().lower()
    return domain if domain else None


def resolve_mx(domain: str, timeout: int = 10) -> List[str]:
    """Resolve MX records for a domain and return a list of hostnames."""
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=timeout)
        mx_hosts = [
            answer.exchange.to_text(omit_final_dot=True)
            for answer in sorted(answers, key=lambda record: record.preference)
        ]
        if mx_hosts:
            return mx_hosts
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        pass
    except dns.exception.DNSException:
        raise

    # Fallback to A/AAAA if no MX records exist
    hosts: List[str] = []
    for record_type in ("A", "AAAA"):
        try:
            answers = dns.resolver.resolve(domain, record_type, lifetime=timeout)
            hosts.extend([answer.to_text() for answer in answers])
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            continue
    return hosts


def smtp_verify_address(
    email: str,
    sender: str = "postmaster@localhost",
    timeout: int = 10,
) -> Dict[str, Optional[str]]:
    """Attempt SMTP verification of the email address using MX hosts."""
    domain = _extract_domain(email)
    result: Dict[str, Optional[str]] = {
        "email": email,
        "smtp_verified": None,
        "smtp_status": None,
        "smtp_error": None,
        "mx_hosts": None,
    }

    if not domain:
        result["smtp_verified"] = False
        result["smtp_status"] = "invalid_domain"
        result["smtp_error"] = "Unable to extract the email domain."
        return result

    try:
        mx_hosts = resolve_mx(domain, timeout=timeout)
    except dns.exception.DNSException as exc:
        result["smtp_verified"] = False
        result["smtp_status"] = "dns_error"
        result["smtp_error"] = str(exc)
        result["mx_hosts"] = []
        return result

    result["mx_hosts"] = mx_hosts
    if not mx_hosts:
        result["smtp_verified"] = False
        result["smtp_status"] = "no_mx"
        result["smtp_error"] = "No MX or A/AAAA records found for domain."
        return result

    last_error: Optional[str] = None
    temporary_failure = False

    for host in mx_hosts:
        try:
            with smtplib.SMTP(host, port=25, timeout=timeout) as smtp:
                smtp.ehlo_or_helo_if_needed()
                code, _ = smtp.mail(sender)
                if code >= 400:
                    last_error = f"MAIL FROM rejected with code {code}."
                    continue

                rcpt_code, _ = smtp.rcpt(email)
                if rcpt_code in (250, 251):
                    result["smtp_verified"] = True
                    result["smtp_status"] = "accepted"
                    return result
                if rcpt_code in (550, 551, 553):
                    result["smtp_verified"] = False
                    result["smtp_status"] = "rejected"
                    result["smtp_error"] = "The server rejected the recipient address."
                    return result
                if rcpt_code in (450, 451, 421):
                    temporary_failure = True
                    last_error = f"Temporary SMTP failure code {rcpt_code}."
                    continue
                last_error = f"Unexpected RCPT response code {rcpt_code}."
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, smtplib.SMTPRecipientsRefused,
                smtplib.SMTPHeloError, smtplib.SMTPDataError, OSError) as exc:
            last_error = str(exc)
            continue

    result["smtp_verified"] = False
    result["smtp_status"] = "temporary_failure" if temporary_failure else "connection_error"
    result["smtp_error"] = last_error or "SMTP verification failed."
    return result


def validate_email(
    email: str,
    smtp_verify: bool = False,
    sender: str = "postmaster@localhost",
    timeout: int = 10,
) -> Dict[str, Optional[object]]:
    """Validate an email address and optionally verify it with SMTP."""
    syntax_valid = validate_email_address(email)
    result: Dict[str, Optional[object]] = {
        "email": email,
        "syntax_valid": syntax_valid,
        "domain": _extract_domain(email),
        "smtp_verify": smtp_verify,
        "smtp_result": None,
    }

    if smtp_verify and syntax_valid:
        result["smtp_result"] = smtp_verify_address(
            email,
            sender=sender,
            timeout=timeout,
        )

    return result


def _write_bulk_rows(output_file: TextIO, fieldnames: List[str], rows: Iterable[Dict[str, object]]) -> None:
    writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)


def bulk_validate_csv(
    input_path: str,
    output_path: Optional[str] = None,
    email_column: str = "email",
    smtp_verify: bool = False,
    sender: str = "postmaster@localhost",
    timeout: int = 10,
) -> List[Dict[str, object]]:
    """Validate email addresses in a CSV file and optionally write output to a CSV file."""
    results: List[Dict[str, object]] = []

    with open(input_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if email_column not in reader.fieldnames:
            raise ValueError(f"CSV file does not contain the column '{email_column}'.")

        for row in reader:
            email = row.get(email_column, "")
            validation = validate_email(
                email,
                smtp_verify=smtp_verify,
                sender=sender,
                timeout=timeout,
            )
            output_row = {**row}
            output_row.update(
                {
                    "syntax_valid": validation["syntax_valid"],
                    "domain": validation["domain"],
                    "smtp_verify": smtp_verify,
                    "smtp_verified": (validation["smtp_result"] or {}).get("smtp_verified"),
                    "smtp_status": (validation["smtp_result"] or {}).get("smtp_status"),
                    "smtp_error": (validation["smtp_result"] or {}).get("smtp_error"),
                }
            )
            results.append(output_row)

    if output_path:
        fieldnames = list(results[0].keys()) if results else []
        with open(output_path, "w", newline="", encoding="utf-8") as output_handle:
            _write_bulk_rows(output_handle, fieldnames, results)

    return results
