"""Sample script for calling the Flask email validator endpoint."""

import requests


def main():
    response = requests.post(
        "http://localhost:5000/validate",
        json={"email": "user@example.com"},
        timeout=10,
    )
    response.raise_for_status()
    print(response.json())


if __name__ == "__main__":
    main()
