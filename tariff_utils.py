from datetime import datetime, timedelta
import requests
from dateutil import parser 

def calculate_start_time(num_hours, api_key):
    """
    Calculate the start time from now given the number of hours.

    :param num_hours: int - Number of hours to add to the current time
    :return: str - The start time formatted as 'YYYY-MM-DD HH:MM:SS'
    """

    api_url = 'https://api.octopus.energy/v1/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-C/standard-unit-rates/'

    print(api_url)
    response = requests.get(api_url, auth=(api_key, ''))
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        tariff_data = response.json()['results']
        for slot in tariff_data:
            # Parse the date strings assuming they are in UTC
            valid_from = datetime.fromisoformat(slot['valid_from'].replace('Z', '+00:00'))
            valid_to = datetime.fromisoformat(slot['valid_to'].replace('Z', '+00:00'))

            print ('---------------')
            print(f'from datetime{valid_from}')
            print(f'to datetime{valid_to}')

    else:
        print(f'Error: {response.status_code} - {response.reason}')

    current_time = datetime.now()
    start_time = current_time + timedelta(hours=num_hours)
    return start_time.strftime('%Y-%m-%d %H:%M:%S')
