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
    best_start_time = None
    best_tariff = float('inf')
    
    if response.status_code == 200:

        # Filter and sort the time slots within the next 12 hours
        now = datetime.now()  # Current time
        begin_time = now + timedelta(minutes=30)
        end_time = begin_time + timedelta(hours=scan_hours)  # Time 12 hours from now 

        # Parse the JSON response
        data = response.json()
        tariff_data = response.json()['results']
        available_slots = []

        for slot in tariff_data:
            # Parsing the datetime strings 
            valid_from = datetime.strptime(slot['valid_from'], "%Y-%m-%dT%H:%M:%SZ")
            valid_to = datetime.strptime(slot['valid_to'], "%Y-%m-%dT%H:%M:%SZ")
            
            if valid_from >= begin_time and valid_to <= end_time:
                available_slots.append({
                    'valid_from': valid_from,
                    'valid_to': valid_to,
                    'tariff': slot['value_inc_vat']
                })
                print ('---------------')
                print(f'from datetime{valid_from}')
                print(f'to datetime{valid_to}')

        
        available_slots.sort(key=lambda x: x['valid_from'])
        required_slots = num_hours * 2

        for i in range(len(available_slots) - required_slots + 1):
            consecutive_slots = available_slots[i:i + required_slots]
            
            # Check if all the slots are consecutive (i.e., exactly 30 minutes apart)
            is_consecutive = all(
                consecutive_slots[j]['valid_from'] == consecutive_slots[j-1]['valid_to']
                for j in range(1, required_slots)
            )
            
            if is_consecutive:
                total_tariff = sum(slot['tariff'] for slot in consecutive_slots)
                avg_tariff = round(total_tariff / required_slots, 0.01)
                print(f'At time {consecutive_slots[0]['valid_from']}, total tariff: {total_tariff}; avg tariff: {avg_tariff}')

                if total_tariff < best_tariff:
                    best_tariff = avg_tariff
                    best_start_time = consecutive_slots[0]['valid_from']
                    print(f'BEST TIMESLOT FOUND at [{best_start_time}] for [{best_tariff}].')
            else:
                print(f'Not consecutive: {consecutive_slots[0]['valid_from']}')

    else:
        print(f'Error: {response.status_code} - {response.reason}')

    if best_start_time:
        return best_start_time.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return None
    
    # current_time = datetime.now()
    # start_time = current_time + timedelta(hours=num_hours)
    # return start_time.strftime('%Y-%m-%d %H:%M:%S')
