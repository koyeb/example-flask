from datetime import datetime, timedelta
import requests

def calculate_start_time(num_hours, api_key):
    """
    Calculate the start time from now given the number of hours.

    :param num_hours: int - Number of hours to add to the current time
    :return: str - The start time formatted as 'YYYY-MM-DD HH:MM:SS'
    """

    api_url = 'https://api.octopus.energy/v1/electricity-meter-points/1200036570277/meters/18L2047503/consumption/'

    print(api_url)
    response = requests.get(api_url, auth=(api_key, ''))
    print(response)

    current_time = datetime.now()
    start_time = current_time + timedelta(hours=num_hours)
    return start_time.strftime('%Y-%m-%d %H:%M:%S')
