from flask import Flask, request, jsonify
from validator import validate_email_address

app = Flask(__name__)

@app.route('/validate', methods=['POST'])
def validate():
    data = request.get_json(force=True)
    email = data.get('email', '')
    valid = validate_email_address(email)
    return jsonify({"email": email, "valid": valid})

if __name__ == '__main__':
    app.run(port=5000)
