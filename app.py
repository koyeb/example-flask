from flask import Flask, jsonify, request, abort, send_from_directory, render_template
from tariff_utils import calculate_start_time, get_best_tariff_windows
import os
import json
from datetime import datetime, timedelta
import random

api_key = os.getenv("OCTOPUS_KEY")

app = Flask(__name__)

# Vocabulary quiz settings are kept here because both the HTML page and
# regenerate endpoint need the same source file and allowed count values.
VOCAB_QUESTION_PATH = os.path.join(
    app.root_path,
    'static',
    'English',
    'Vocabulary',
    'questions.json',
)
VOCAB_ALLOWED_COUNTS = [5, 10, 15, 20, 25, 30]
VOCAB_ALLOWED_TYPES = [
    'word_meaning',
    'reverse_meaning',
    'fill_in_blank',
    'alternative_word',
    'part_of_speech',
]


@app.route('/')
def hello_world():
    return jsonify(message="Hello, Happy Flasking!")

@app.route('/api/spec')
def api_spec():
    return send_from_directory('static', 'api_spec.yaml')


@app.route('/xml/<path:filename>')
def serve_xml(filename: str):
    """Serve XML files from the /static/xml directory via /xml/<filename>.xml.

    If the requested file does not exist, return a JSON 404 with a clear message.
    Only .xml files are allowed (anything else 404s).
    """
    if not filename.lower().endswith('.xml'):
        abort(404)

    # Resolve from the intended static subdirectory and reject missing files.
    xml_dir = os.path.join(app.root_path, 'static', 'xml')
    file_path = os.path.join(xml_dir, filename)

    if not os.path.isfile(file_path):
        return jsonify(error="File not found"), 404

    return send_from_directory(xml_dir, filename, mimetype='application/xml')


@app.route('/html/<path:filename>')
def serve_html(filename: str):
    """Serve HTML files from the /static/html directory via /html/<filename>.html.

    If the requested file does not exist, return a JSON 404 with a clear message.
    Only .html files are allowed (anything else 404s).
    """
    if not filename.lower().endswith('.html'):
        abort(404)

    # Mirror the XML route, but restrict this endpoint to static HTML files.
    html_dir = os.path.join(app.root_path, 'static', 'html')
    file_path = os.path.join(html_dir, filename)

    if not os.path.isfile(file_path):
        return jsonify(error="File not found"), 404

    return send_from_directory(html_dir, filename, mimetype='text/html')


@app.route('/tariff')
def tariff():
    num_hours_str = request.args.get('numHours', default=None)
    
    if num_hours_str is None:
        return jsonify(error="numHours parameter is required"), 400
    
    try:
        num_hours = float(num_hours_str)
    except ValueError:
        return jsonify(error="numHours must be a number"), 400

    try:
        start_time_str = calculate_start_time(num_hours, api_key)
    except ValueError as error:
        return jsonify(error=str(error)), 400
    except RuntimeError as error:
        return jsonify(error=str(error)), 502

    return jsonify(startTime=start_time_str)


@app.route('/octopus')
def octopus():
    # The Octopus page presents fixed appliance durations as a compact table.
    durations = [1, 1.5, 2, 2.5, 3, 3.5]
    page_error = None
    window_rows = []

    try:
        window_rows = get_best_tariff_windows(durations, api_key)
    except RuntimeError as error:
        page_error = str(error)

    for row in window_rows:
        # Convert tariff utility output into labels that the template can print.
        if row.get('error'):
            row['duration_label'] = f"{row['duration_hours']:g} hours"
            continue

        row['duration_label'] = f"{row['duration_hours']:g} hours"
        row['start_label'] = row['start_time'].strftime('%d %b %Y, %H:%M')
        row['end_label'] = row['end_time'].strftime('%d %b %Y, %H:%M')
        row['total_tariff_label'] = f"{row['total_tariff']:.2f} p/kWh"
        row['average_tariff_label'] = f"{row['average_tariff']:.2f} p/kWh"
        row['is_credit'] = row['total_tariff'] < 0
        row['slot_details'] = [
            {
                'start_label': slot['start_time'].strftime('%d %b %Y, %H:%M'),
                'end_label': slot['end_time'].strftime('%d %b %Y, %H:%M'),
                'tariff_label': f"{slot['tariff']:.2f} p/kWh",
            }
            for slot in row.get('slots', [])
        ]

    return render_template(
        'octopus.html',
        rows=window_rows,
        page_error=page_error,
    )


def _get_vocab_count(default=10):
    """Return a supported quiz size, falling back to the default for bad input."""
    count = request.args.get('count', default=default, type=int)
    if count not in VOCAB_ALLOWED_COUNTS:
        count = default
    return count


def _get_vocab_types():
    """Return supported question types parsed from a comma-separated query list."""
    raw_types = request.args.get('types', default='', type=str)

    if not raw_types:
        return list(VOCAB_ALLOWED_TYPES)

    requested_types = [question_type.strip() for question_type in raw_types.split(',') if question_type.strip()]
    filtered_types = [question_type for question_type in requested_types if question_type in VOCAB_ALLOWED_TYPES]

    if not filtered_types:
        return list(VOCAB_ALLOWED_TYPES)

    return filtered_types


def _load_vocab_questions():
    """Load the vocabulary question bank and ensure it keeps the expected shape."""
    with open(VOCAB_QUESTION_PATH, encoding='utf-8') as question_file:
        questions = json.load(question_file)

    if not isinstance(questions, list):
        raise ValueError('Vocabulary question bank must be a JSON array.')

    return questions


def _sample_vocab_questions(count, selected_types=None):
    """Pick random questions and shuffle each choice list before rendering."""
    questions = _load_vocab_questions()

    if selected_types:
        questions = [question for question in questions if question.get('type') in selected_types]

    selected_questions = random.sample(questions, min(count, len(questions))) if questions else []

    sampled_questions = []
    for question in selected_questions:
        question_copy = dict(question)
        choices = [dict(choice) for choice in question_copy.get('choices', [])]
        random.shuffle(choices)
        question_copy['choices'] = choices
        sampled_questions.append(question_copy)

    return sampled_questions


@app.route('/vocab')
def vocab():
    """Render the vocabulary quiz page with an initial random question set."""
    count = _get_vocab_count()

    selected_types = _get_vocab_types()

    try:
        questions = _sample_vocab_questions(count, selected_types)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        return render_template(
            'vocab.html',
            questions=[],
            selected_count=count,
            allowed_counts=VOCAB_ALLOWED_COUNTS,
            allowed_types=VOCAB_ALLOWED_TYPES,
            page_error=str(error),
        ), 500

    return render_template(
        'vocab.html',
        questions=questions,
        selected_count=count,
        allowed_counts=VOCAB_ALLOWED_COUNTS,
        allowed_types=VOCAB_ALLOWED_TYPES,
        page_error=None,
    )


@app.route('/vocab/questions')
def vocab_questions():
    """Return a fresh question set for no-refresh quiz regeneration."""
    count = _get_vocab_count()

    selected_types = _get_vocab_types()

    try:
        questions = _sample_vocab_questions(count, selected_types)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        return jsonify(error=str(error)), 500

    return jsonify(questions=questions, count=len(questions), selected_types=selected_types)


@app.route('/vocab/feedback', methods=['POST'])
def vocab_feedback():
    """Accept first-attempt misses; currently this is a dummy receiver."""
    data = request.get_json(silent=True) or {}
    missed_target_words = data.get('missed_target_words', [])

    if not isinstance(missed_target_words, list):
        return jsonify(error='missed_target_words must be a list'), 400

    return jsonify(
        status='received',
        missed_count=len(missed_target_words),
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
