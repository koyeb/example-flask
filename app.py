from flask import Flask, jsonify, request, abort
import os

app = Flask(__name__)

# Read API Key from environment variable
VALID_API_KEYS = {os.getenv('API_KEY')}  # Assuming there's only one key for simplicity

def require_api_key(f):
    def decorated(*args, **kwargs):
        api_key = request.headers.get('API-Key')
        if api_key not in VALID_API_KEYS:
            abort(401)  # Unauthorized access if the API key is not valid
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@require_api_key
def hello_world():
    return jsonify(message="Hello, Happy Flasking!")

if __name__ == '__main__':
    app.run(debug=True)
