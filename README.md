# 📧 SMTP Email Validator

> A comprehensive Python-based email validation suite combining grammar-based syntax checking, DNS MX resolution, and SMTP mailbox verification with CLI, REST API, and web UI interfaces.

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## ✨ Features

### 🔍 Multi-Level Email Validation

| Feature | Description |
|---------|-------------|
| **Syntax Validation** | Grammar-based parsing using Lark parser for RFC-compliant email format checking |
| **DNS MX Resolution** | Resolves MX records for email domains with automatic fallback to A/AAAA records |
| **SMTP Verification** | Connects to mail servers using `RCPT TO` command to verify mailbox existence (without sending email) |
| **Bulk Processing** | Validate hundreds of emails at once from CSV files |
| **Flexible Interfaces** | CLI, REST API (Flask), and interactive web UI (Streamlit) |

### 🎯 Core Capabilities

- ✅ Real-time validation with configurable timeouts
- ✅ Structured JSON responses for programmatic use
- ✅ SMTP server lifecycle management for testing
- ✅ Comprehensive error handling and reporting
- ✅ Unit tests with mocked SMTP/DNS for CI/CD integration
- ✅ Type hints throughout for better IDE support

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/AkshayR278/SMTP-Email-Validator.git
cd SMTP-Email-Validator

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

**Single email validation:**
```bash
python main.py --email user@example.com
```

**With SMTP verification:**
```bash
python main.py --email user@example.com --smtp-verify
```

**JSON output:**
```bash
python main.py --email user@example.com --smtp-verify --json
```

**Bulk CSV validation:**
```bash
python main.py --csv emails.csv --output results.csv --smtp-verify
```

---

## 📖 Usage Guide

### Command-Line Interface (CLI)

#### Single Email Validation

```bash
# Basic validation
python main.py --email john.doe@example.com

# With SMTP mailbox verification
python main.py --email john.doe@example.com --smtp-verify

# With custom sender and timeout
python main.py --email john.doe@example.com --smtp-verify \
  --sender verify@company.com --timeout 15

# JSON output for programmatic use
python main.py --email john.doe@example.com --smtp-verify --json
```

#### Bulk CSV Validation

```bash
# Validate a CSV file (assumes 'email' column)
python main.py --csv customers.csv --output validated.csv --smtp-verify

# Specify a different email column
python main.py --csv contacts.csv --email-column contact_email \
  --output verified_contacts.csv --smtp-verify

# Print results to stdout instead of file
python main.py --csv emails.csv --smtp-verify --json
```

**CSV File Format:**
```csv
email,name
john@example.com,John Doe
jane@example.com,Jane Smith
invalid-email,Invalid User
```

**Output Format:**
```csv
email,name,syntax_valid,domain,smtp_verify,smtp_verified,smtp_status,smtp_error
john@example.com,John Doe,True,example.com,True,True,accepted,
jane@example.com,Jane Smith,True,example.com,True,True,accepted,
invalid-email,Invalid User,False,,True,,
```

### REST API (Flask)

```bash
# Start the Flask server
python web_validator.py
# Server runs on http://localhost:5000
```

**Validate a single email:**
```bash
curl -X POST http://localhost:5000/validate \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'
```

**With SMTP verification:**
```bash
curl -X POST http://localhost:5000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email":"user@example.com",
    "smtp_verify":true,
    "sender":"verify@company.com",
    "timeout":15
  }'
```

**Response Example:**
```json
{
  "email": "user@example.com",
  "syntax_valid": true,
  "domain": "example.com",
  "smtp_verify": true,
  "smtp_result": {
    "email": "user@example.com",
    "smtp_verified": true,
    "smtp_status": "accepted",
    "smtp_error": null,
    "mx_hosts": ["mx1.example.com", "mx2.example.com"]
  }
}
```

### Web UI (Streamlit)

```bash
streamlit run Validator-app.py
```

The interactive web interface includes:

- 🔍 **Single Email Tab**: Validate individual emails with real-time feedback
- 📊 **Bulk Validation Tab**: Upload CSV files for batch processing
- ⚙️ **Configuration Sidebar**: Set default SMTP settings, timeouts, and sender address
- 📈 **Results Dashboard**: View statistics and download validated results
- 📋 **Detailed Logging**: Expand sections to view full validation data

### SMTP Test Server

```bash
# Start a local SMTP server for testing
python smtp_server.py
# Server listens on 127.0.0.1:8025

# Connect with your SMTP client to test validation
```

---

## 🏗️ Project Structure

```
SMTP-Email-Validator/
├── 📄 README.md                    # This file
├── 📋 requirements.txt             # Python dependencies
├── 🔧 .gitignore                   # Git ignore rules
│
├── 🎯 main.py                      # CLI entry point
├── 🌐 web_validator.py             # Flask REST API
├── 🎨 Validator-app.py             # Streamlit web UI
├── 📬 smtp_server.py               # Local SMTP server for testing
│
├── 🔍 validator.py                 # Core validation logic
│   ├── validate_email_address()    # Syntax validation
│   ├── validate_email()            # Full validation (syntax + SMTP)
│   ├── resolve_mx()                # DNS MX resolution
│   ├── smtp_verify_address()       # SMTP mailbox verification
│   └── bulk_validate_csv()         # Bulk CSV processing
│
├── 📖 email_grammar.lark           # Lark grammar for email parsing
├── 🧪 trial.py                     # Example API client script
│
└── tests/
    └── test_validator.py           # Unit tests (14 test cases)
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
pytest                              # Run all tests
pytest -v                           # Verbose output
pytest tests/test_validator.py -v   # Specific test file
pytest --cov                        # With coverage report
```

**Test Coverage:**
- ✅ Syntax validation (valid and invalid emails)
- ✅ SMTP verification with success/failure scenarios
- ✅ DNS MX resolution and fallback
- ✅ Bulk CSV validation with mocked SMTP/DNS
- ✅ Error handling and edge cases

---

## 🛠️ Tech Stack

| Component | Purpose |
|-----------|---------|
| **lark-parser** | Grammar-based email syntax validation |
| **dnspython** | DNS MX record resolution |
| **smtplib** | SMTP protocol implementation (Python stdlib) |
| **Flask** | REST API framework |
| **Streamlit** | Interactive web UI |
| **aiosmtpd** | Async SMTP server for testing |
| **pytest** | Testing framework |

---

## ⚙️ Configuration

### CLI Arguments

```
main.py --help

  --email EMAIL              Email to validate (single mode)
  --csv FILE                 CSV file to validate (bulk mode)
  --output FILE              Output CSV file for bulk results
  --email-column COL         CSV column name containing emails (default: 'email')
  --smtp-verify              Enable SMTP mailbox verification
  --sender ADDRESS           SMTP sender address (default: postmaster@localhost)
  --timeout SECONDS          DNS/SMTP timeout (default: 10, max: 60)
  --json                     Output results as JSON
```

---

## ⚠️ Limitations

- **Network-Dependent**: SMTP verification depends on remote mail servers and may fail due to:
  - Network connectivity issues
  - Firewall/port restrictions (SMTP typically uses port 25)
  - Rate limiting or anti-spam measures
  - Authentication requirements (not implemented)

- **False Positives**: Some mail servers use catch-all policies that accept any recipient address

- **Non-Invasive**: This tool does not send actual email content—only tests with `RCPT TO` command

- **DNS Timeouts**: MX resolution may fail for domains with DNS issues or very slow responses

---

## 🚀 Future Roadmap

### Short Term
- [ ] Add catch-all detection heuristics to reduce false positives
- [ ] Support for SMTP authentication (for restricted mail servers)
- [ ] Enhanced logging with verbose/debug modes
- [ ] Configuration file support (`.env` or YAML)

### Medium Term
- [ ] Disposable email domain detection (integration with public lists)
- [ ] Validation caching for repeated addresses
- [ ] Rate limiting and throttling for API endpoints
- [ ] Support for internationalized domain names (IDN)

### Long Term
- [ ] Python package publishing on PyPI
- [ ] Docker containerization for easy deployment
- [ ] GitHub Actions CI/CD pipeline with automated testing
- [ ] Web API authentication and rate limiting (API keys)
- [ ] Database integration for result persistence
- [ ] Real-time monitoring dashboard

---

## 🤝 Contributing

Contributions are welcome! To get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run tests: `pytest`
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📝 License

This project is released under the MIT License. It is intended for educational and commercial use. See [LICENSE](LICENSE) file for details.

---

## 📧 Support & Issues

Found a bug or have a feature request? [Open an issue](https://github.com/AkshayR278/SMTP-Email-Validator/issues) on GitHub!

---

## 🙏 Acknowledgments

- Built with [Lark Parser](https://github.com/lark-parser/lark) for robust email grammar parsing
- DNS resolution powered by [dnspython](https://www.dnspython.org/)
- Web UI built with [Streamlit](https://streamlit.io/)
- API framework by [Flask](https://flask.palletsprojects.com/)

---

**Made with ❤️ for email validation**
