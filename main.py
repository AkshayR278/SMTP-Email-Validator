import argparse
import json
from validator import bulk_validate_csv, validate_email


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate an email address or a CSV file of email addresses."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--email",
        help="Email address to validate",
    )
    group.add_argument(
        "--csv",
        help="CSV file path containing email addresses to validate",
    )
    parser.add_argument(
        "--email-column",
        default="email",
        help="CSV column name for the email address",
    )
    parser.add_argument(
        "--output",
        help="Optional output CSV file path for bulk validation results",
    )
    parser.add_argument(
        "--smtp-verify",
        action="store_true",
        help="Attempt SMTP mailbox verification after syntax validation.",
    )
    parser.add_argument(
        "--sender",
        default="postmaster@localhost",
        help="Sender address to use during SMTP verification.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Timeout in seconds for DNS and SMTP operations.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print results in JSON format",
    )
    args = parser.parse_args()

    if args.csv:
        results = bulk_validate_csv(
            args.csv,
            output_path=args.output,
            email_column=args.email_column,
            smtp_verify=args.smtp_verify,
            sender=args.sender,
            timeout=args.timeout,
        )
        if args.output:
            print(f"Bulk validation completed. Results written to {args.output}")
        elif args.json:
            print(json.dumps(results, indent=2))
        else:
            valid_count = sum(
                1
                for row in results
                if row["syntax_valid"] and (not args.smtp_verify or row.get("smtp_verified") is True)
            )
            print(f"Processed {len(results)} records. {valid_count} valid.")

        valid_exit = all(
            row["syntax_valid"] and (not args.smtp_verify or row.get("smtp_verified") is True)
            for row in results
        )
        raise SystemExit(0 if valid_exit else 1)

    result = validate_email(
        args.email,
        smtp_verify=args.smtp_verify,
        sender=args.sender,
        timeout=args.timeout,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Email: {result['email']}")
        print(f"Syntax valid: {result['syntax_valid']}")
        if args.smtp_verify:
            smtp_result = result.get("smtp_result") or {}
            print(f"SMTP verification: {smtp_result.get('smtp_status')}")
            if smtp_result.get("smtp_error"):
                print(f"SMTP error: {smtp_result['smtp_error']}")

    valid_exit = result["syntax_valid"] and (
        not args.smtp_verify or (result.get("smtp_result") or {}).get("smtp_verified") is True
    )
    raise SystemExit(0 if valid_exit else 1)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
