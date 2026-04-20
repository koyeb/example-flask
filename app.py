from flask import Flask, jsonify, request, abort, send_from_directory, render_template
from tariff_utils import calculate_start_time, get_best_tariff_windows
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

# --- New route: serve XML files from /static/xml ---
@app.route('/xml/<path:filename>')
def serve_xml(filename: str):
    """Serve XML files from the /static/xml directory via /xml/<filename>.xml.

    If the requested file does not exist, return a JSON 404 with a clear message.
    Only .xml files are allowed (anything else 404s).
    """
    if not filename.lower().endswith('.xml'):
        abort(404)

    xml_dir = os.path.join(app.root_path, 'static', 'xml')
    file_path = os.path.join(xml_dir, filename)

    # Ensure the file exists; if not, return a simple JSON 404 response
    if not os.path.isfile(file_path):
        return jsonify(error="File not found"), 404

    # send_from_directory safely serves files from a specific folder
    return send_from_directory(xml_dir, filename, mimetype='application/xml')

@app.route('/tariff')
def tariff():
    # Retrieve the numHours parameter from the request's query string
    num_hours_str = request.args.get('numHours', default=None)
    
    if num_hours_str is None:
        return jsonify(error="numHours parameter is required"), 400
    
    try:
        num_hours = float(num_hours_str)
    except ValueError:
        return jsonify(error="numHours must be a number"), 400

    try:
        # Use the external module to calculate the start time
        start_time_str = calculate_start_time(num_hours, api_key)
    except ValueError as error:
        return jsonify(error=str(error)), 400
    except RuntimeError as error:
        return jsonify(error=str(error)), 502

    return jsonify(startTime=start_time_str)


@app.route('/octopus')
def octopus():
    durations = [1, 1.5, 2, 2.5, 3, 3.5]
    page_error = None
    window_rows = []

    try:
        window_rows = get_best_tariff_windows(durations, api_key)
    except RuntimeError as error:
        page_error = str(error)

    for row in window_rows:
        if row.get('error'):
            row['duration_label'] = f"{row['duration_hours']:g} hours"
            continue

        row['duration_label'] = f"{row['duration_hours']:g} hours"
        row['start_label'] = row['start_time'].strftime('%d %b %Y, %H:%M')
        row['end_label'] = row['end_time'].strftime('%d %b %Y, %H:%M')
        row['total_tariff_label'] = f"{row['total_tariff']:.2f} p/kWh"
        row['average_tariff_label'] = f"{row['average_tariff']:.2f} p/kWh"
        row['is_credit'] = row['total_tariff'] < 0

    return render_template(
        'octopus.html',
        rows=window_rows,
        page_error=page_error,
    )

@app.route('/demo_status')
def demo_status():
    connection_type = request.args.get('type', default=None)

    if connection_type not in ["FIX", "MQ", "SFTP", "ALL"]:
        return jsonify(error="Invalid connection type. Allowed values are FIX, MQ, SFTP, ALL."), 400

    return jsonify(message=f'All your {"" if connection_type == "ALL" else connection_type} connections are up and running')

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
