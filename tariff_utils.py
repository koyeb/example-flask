from datetime import datetime, timedelta

import pytz
import requests

SCAN_HOURS = 12
OCTOPUS_TARIFF_URL = (
    "https://api.octopus.energy/v1/products/AGILE-24-10-01/"
    "electricity-tariffs/E-1R-AGILE-24-10-01-C/standard-unit-rates/"
)
LONDON_TZ = pytz.timezone("Europe/London")


def _parse_duration_slots(duration_hours):
    slot_count = int(duration_hours * 2)
    if slot_count <= 0 or slot_count != duration_hours * 2:
        raise ValueError("Duration must be a positive multiple of 0.5 hours")
    return slot_count


def _fetch_available_slots(api_key, scan_hours=SCAN_HOURS):
    if not api_key:
        raise RuntimeError("OCTOPUS_KEY is not configured")

    try:
        response = requests.get(OCTOPUS_TARIFF_URL, auth=(api_key, ""), timeout=10)
    except requests.RequestException as error:
        raise RuntimeError(f"Octopus API request failed: {error}") from error

    print(f"Returned status code: {response.status_code}")

    if response.status_code != 200:
        raise RuntimeError(f"Octopus API error: {response.status_code} - {response.reason}")

    now_utc = datetime.now(pytz.UTC)
    begin_time = now_utc + timedelta(minutes=30)
    end_time = begin_time + timedelta(hours=scan_hours)

    available_slots = []
    for slot in response.json().get("results", []):
        valid_from = datetime.fromisoformat(slot["valid_from"].replace("Z", "+00:00"))
        valid_to = datetime.fromisoformat(slot["valid_to"].replace("Z", "+00:00"))

        if valid_from >= begin_time and valid_to <= end_time:
            available_slots.append(
                {
                    "valid_from": valid_from,
                    "valid_to": valid_to,
                    "tariff": slot["value_inc_vat"],
                }
            )

    available_slots.sort(key=lambda slot: slot["valid_from"])
    return available_slots


def find_best_tariff_window(duration_hours, api_key, available_slots=None):
    required_slots = _parse_duration_slots(duration_hours)
    slots = available_slots if available_slots is not None else _fetch_available_slots(api_key)

    if len(slots) < required_slots:
        raise ValueError(f"Not enough tariff slots available for a {duration_hours}-hour window")

    best_window = None
    best_total_tariff = float("inf")

    for index in range(len(slots) - required_slots + 1):
        consecutive_slots = slots[index:index + required_slots]
        is_consecutive = all(
            consecutive_slots[position]["valid_from"] == consecutive_slots[position - 1]["valid_to"]
            for position in range(1, required_slots)
        )

        if not is_consecutive:
            print(f"Not consecutive: {consecutive_slots[0]['valid_from']}")
            continue

        total_tariff = sum(slot["tariff"] for slot in consecutive_slots)
        if total_tariff < best_total_tariff:
            best_total_tariff = total_tariff
            best_window = {
                "duration_hours": duration_hours,
                "start_time": consecutive_slots[0]["valid_from"],
                "end_time": consecutive_slots[-1]["valid_to"],
                "total_tariff": total_tariff,
                "average_tariff": total_tariff / required_slots,
            }
            print(
                "BEST TIMESLOT FOUND at "
                f"[{best_window['start_time']}] for [{best_window['total_tariff']}]."
            )

    if best_window is None:
        raise ValueError(f"No continuous tariff window found for {duration_hours} hours")

    return best_window


def get_best_tariff_windows(duration_hours_list, api_key):
    available_slots = _fetch_available_slots(api_key)
    results = []

    for duration_hours in duration_hours_list:
        try:
            results.append(find_best_tariff_window(duration_hours, api_key, available_slots))
        except ValueError as error:
            results.append(
                {
                    "duration_hours": duration_hours,
                    "error": str(error),
                }
            )

    return results


def calculate_start_time(num_hours, api_key):
    """
    Calculate the cheapest start time from now for a given duration.

    :param num_hours: int|float - Duration in hours, in 0.5-hour increments
    :return: str | None - Start time formatted as 'YYYY-MM-DD HH:MM:SS'
    """

    best_window = find_best_tariff_window(num_hours, api_key)
    best_start_time_uk = best_window["start_time"].astimezone(LONDON_TZ)
    return best_start_time_uk.strftime("%Y-%m-%d %H:%M:%S")
    
