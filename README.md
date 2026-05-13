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

## Local run

```bash
python app.py
```

Default Flask URL:
- `http://127.0.0.1:5000/tariff?numHours=2`
- `http://127.0.0.1:5000/octopus`

## Environment variable

Set the Octopus API key before running:

```bash
export OCTOPUS_KEY="your_octopus_api_key"
```
