from datetime import datetime, timedelta
import requests
from dateutil import parser 

def calculate_start_time(num_hours, api_key):
    """
    Calculate the start time from now given the number of hours.

    :param num_hours: int - Number of hours to add to the current time
    :return: str - The start time formatted as 'YYYY-MM-DD HH:MM:SS'
    """

    api_url = 'https://api.octopus.energy/v1/electricity-meter-points/1200036570277/meters/18L2047503/consumption/'

    print(api_url)
    response = requests.get(api_url, auth=(api_key, ''))
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        tariff_data = response.json()['results']
        for slot in tariff_data:
            # Using `dateutil.parser.parse` to correctly handle timezone information
            valid_from = parser.isoparse(slot['interval_start'])  # Parses with timezone info
            valid_to = parser.isoparse(slot['interval_end'])  # Parses with timezone info
            
            # Convert both valid_from and valid_to to UTC
            valid_from_utc = valid_from.astimezone(tz=datetime.timezone.utc)
            valid_to_utc = valid_to.astimezone(tz=datetime.timezone.utc)

            print ('---------------')
            print(f'from datetime{valid_from}')
            print(f'to datetime{valid_to}')
            print(f'from utc{valid_from_utc}')
            print(f'to utc{valid_to_utc}')

    else:
        print(f'Error: {response.status_code} - {response.reason}')

    current_time = datetime.now()
    start_time = current_time + timedelta(hours=num_hours)
    return start_time.strftime('%Y-%m-%d %H:%M:%S')
