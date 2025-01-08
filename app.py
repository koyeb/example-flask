from flask import Flask, jsonify, request, abort, send_from_directory
from tariff_utils import calculate_start_time
import os
from datetime import datetime, timedelta
import random

api_key = os.getenv("OCTOPUS_KEY")

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
    start_time_str = calculate_start_time(num_hours, api_key)
    return jsonify(startTime=start_time_str)

@app.route('/demo_status')
def demo_status():
    connection_type = request.args.get('type', default=None)

    if connection_type not in ["FIX", "MQ", "SFTP", "ALL"]:
        return jsonify(error="Invalid connection type. Allowed values are FIX, MQ, SFTP, ALL."), 400

    return jsonify(message="All your connections are up and running")

@app.route('/demo_details')
def demo_details():
    connection_id = request.args.get('id', default=None)

    if not connection_id:
        return jsonify(error="ID parameter is required"), 400

    current_time = datetime.utcnow()
    random_minutes = random.randint(1, 20)
    last_connection_time = current_time - timedelta(minutes=random_minutes)

    return jsonify(message=f"Connection {connection_id} is up", lastConnectionTime=last_connection_time.isoformat() + "Z")

if __name__ == '__main__':
    app.run(debug=True)
