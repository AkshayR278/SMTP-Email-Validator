import pytest

import validator
from validator import validate_email_address, validate_email


@pytest.mark.parametrize(
    "email",
    [
        "user@example.com",
        "first.last@example.co.uk",
        "name+tag@example.com",
        "\"quoted@local\"@example.com",
    ],
)
def test_valid_email_addresses(email):
    assert validate_email_address(email) is True


@pytest.mark.parametrize(
    "email",
    [
        "",
        "plainaddress",
        "user@.com",
        "user@example",
        "user@@example.com",
        None,
    ],
)
def test_invalid_email_addresses(email):
    assert validate_email_address(email) is False


def test_validate_email_without_smtp():
    result = validate_email("user@example.com", smtp_verify=False)
    assert result["syntax_valid"] is True
    assert result["domain"] == "example.com"
    assert result["smtp_result"] is None


def test_validate_email_with_smtp_success(monkeypatch):
    monkeypatch.setattr(validator, "resolve_mx", lambda domain, timeout=10: ["mx.example.com"])

    class DummySMTP:
        def __init__(self, host, port=25, timeout=10):
            self.host = host

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def ehlo_or_helo_if_needed(self):
            pass

        def mail(self, sender):
            return 250, b"OK"

        def rcpt(self, email):
            return 250, b"Accepted"

    monkeypatch.setattr(validator.smtplib, "SMTP", DummySMTP)
    result = validate_email("user@example.com", smtp_verify=True)
    smtp_result = result["smtp_result"]
    assert smtp_result["smtp_verified"] is True
    assert smtp_result["smtp_status"] == "accepted"
    assert smtp_result["mx_hosts"] == ["mx.example.com"]


def test_validate_email_with_smtp_no_mx(monkeypatch):
    monkeypatch.setattr(validator, "resolve_mx", lambda domain, timeout=10: [])
    result = validate_email("user@example.com", smtp_verify=True)
    smtp_result = result["smtp_result"]
    assert smtp_result["smtp_verified"] is False
    assert smtp_result["smtp_status"] == "no_mx"


def test_bulk_validate_csv(tmp_path, monkeypatch):
    csv_file = tmp_path / "emails.csv"
    csv_file.write_text("email\nuser@example.com\ninvalid-email\n", encoding="utf-8")

    monkeypatch.setattr(validator, "resolve_mx", lambda domain, timeout=10: ["mx.example.com"])

    class DummySMTP:
        def __init__(self, host, port=25, timeout=10):
            self.host = host

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def ehlo_or_helo_if_needed(self):
            pass

        def mail(self, sender):
            return 250, b"OK"

        def rcpt(self, email):
            if email == "user@example.com":
                return 250, b"Accepted"
            return 550, b"Rejected"

    monkeypatch.setattr(validator.smtplib, "SMTP", DummySMTP)
    results = validator.bulk_validate_csv(
        str(csv_file),
        output_path=None,
        email_column="email",
        smtp_verify=True,
    )

    assert len(results) == 2
    assert results[0]["syntax_valid"] is True
    assert results[0]["smtp_verified"] is True
    assert results[1]["syntax_valid"] is False
    assert results[1]["smtp_verified"] is None
