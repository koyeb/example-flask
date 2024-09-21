from flask import Flask, jsonify, request, abort, send_from_directory
from tariff_utils import calculate_start_time
import os

api_user = os.getenv("octupus-key")

app = Flask(__name__)

# Read API Key from environment variable
# VALID_API_KEYS = {os.getenv('API_KEY')}  # Assuming there's only one key for simplicity

# def require_api_key(f):
#     def decorated(*args, **kwargs):
#         api_key = request.headers.get('API-Key')
#         if api_key not in VALID_API_KEYS:
#             abort(401)  # Unauthorized access if the API key is not valid
#         return f(*args, **kwargs)
#     return decorated

@app.route('/')
# @require_api_key
def hello_world():
    return jsonify(message="Hello, Happy Flasking!")

@app.route('/api/spec')
def api_spec():
    return send_from_directory('static', 'api_spec.yaml')

@app.route('/tariff')
def tariff():
    # Retrieve the numHours parameter from the request's query string
    num_hours_str = request.args.get('numHours', default=None)
    
    if num_hours_str is None:
        return jsonify(error="numHours parameter is required"), 400
    
    try:
        num_hours = int(num_hours_str)
    except ValueError:
        return jsonify(error="numHours must be an integer"), 400

    # Use the external module to calculate the start time
    start_time_str = calculate_start_time(num_hours, api_user)
    return jsonify(startTime=start_time_str)

if __name__ == '__main__':
    app.run(debug=True)
