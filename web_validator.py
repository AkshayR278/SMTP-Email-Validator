from flask import Flask, request, jsonify
from validator import validate_email

app = Flask(__name__)

@app.route('/validate', methods=['POST'])
def validate():
    data = request.get_json(silent=True)
    if not data or "email" not in data:
        return jsonify({
            "error": "Request JSON must include an 'email' field."
        }), 400

    email = data.get("email", "")
    smtp_verify = bool(data.get("smtp_verify", False))
    sender = data.get("sender", "postmaster@localhost")
    timeout = int(data.get("timeout", 10))

    result = validate_email(
        email,
        smtp_verify=smtp_verify,
        sender=sender,
        timeout=timeout,
    )
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)
