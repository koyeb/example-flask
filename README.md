# Avon Flask API

A small Flask app focused on Octopus Agile tariff planning.

## Endpoints

### `GET /tariff`
Returns the cheapest start time for a device run based on the requested duration.

**Query parameters**
- `numHours` (required, number): how long the appliance will run.

**Success response**
- `200 OK`
```json
{
  "startTime": "2026-05-13 17:00:00"
}
```

**Error responses**
- `400 Bad Request` when `numHours` is missing or not numeric.
- `502 Bad Gateway` when upstream tariff data cannot be fetched.

### `GET /octopus`
Renders an HTML page showing best tariff windows for preset durations (`1` to `3.5` hours).

- Uses live Octopus tariff data.
- Displays start/end times, total tariff, and average tariff.
- Highlights cases where the total tariff is negative (credit periods).

### `GET /vocab`
Renders an HTML vocabulary practice quiz using `static/English/Vocabulary/questions.json`.

- Shows 10 random questions by default.
- Supports quiz sizes of `5`, `10`, `15`, `20`, `25`, and `30`.
- Shuffles the selected questions and each question's answer choices.
- Marks answers in the browser when `Submit` is clicked.
- Counts unanswered questions as wrong.
- Allows retries for wrong answers without immediately showing the correct answer.
- Sends missed `target_word` values from the first submit attempt to the dummy feedback endpoint.

**Query parameters**
- `count` (optional, number): requested quiz size. Invalid values fall back to `10`.

Example:

```text
http://127.0.0.1:5000/vocab?count=15
```

### `GET /vocab/questions`
Returns a fresh random vocabulary question set as JSON for the page's regenerate control.

**Query parameters**
- `count` (optional, number): requested quiz size. Allowed values are `5`, `10`, `15`, `20`, `25`, and `30`.

### `POST /vocab/feedback`
Dummy endpoint that accepts the vocabulary words missed on the first submit attempt.

**Request body**
```json
{
  "missed_target_words": ["reclusive", "wither"]
}
```

**Success response**
```json
{
  "missed_count": 2,
  "status": "received"
}
```

## Local run

```bash
python app.py
```

Default Flask URL:
- `http://127.0.0.1:5000/tariff?numHours=2`
- `http://127.0.0.1:5000/octopus`
- `http://127.0.0.1:5000/vocab`

## Environment variable

Set the Octopus API key before running:

```bash
export OCTOPUS_KEY="your_octopus_api_key"
```
