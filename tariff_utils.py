from datetime import datetime, timedelta
import requests

scan_hours = 4

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

        # Filter and sort the time slots within the next 12 hours
        now = datetime.now()  # Current time
        begin_time = now + timedelta(minutes=30)
        end_time = now + timedelta(hours=scan_hours)  # Time 12 hours from now 

        # Parse the JSON response
        data = response.json()
        tariff_data = response.json()['results']
        for slot in tariff_data:
            # Parsing the datetime strings 
            valid_from = datetime.strptime(slot['valid_from'], "%Y-%m-%dT%H:%M:%SZ")
            valid_to = datetime.strptime(slot['valid_to'], "%Y-%m-%dT%H:%M:%SZ")
            
            if valid_from >= begin_time and valid_to <= end_time:
                print ('---------------')
                print(f'from datetime{valid_from}')
                print(f'to datetime{valid_to}')

    else:
        print(f'Error: {response.status_code} - {response.reason}')

    current_time = datetime.now()
    start_time = current_time + timedelta(hours=num_hours)
    return start_time.strftime('%Y-%m-%d %H:%M:%S')
