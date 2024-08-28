import re
import datetime

# Converting 'dhms' to dictionary format
def parse_time_duration(duration_str: str) -> dict:
    # Regex to match days, hours, minutes, and seconds
    pattern = re.compile(r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?')
    match = pattern.match(duration_str)

    if not match:
        return {}

    # Extracting matched groups, convert to int or set to 0 if None
    days = int(match.group(1) or 0)
    hours = int(match.group(2) or 0)
    minutes = int(match.group(3) or 0)
    seconds = int(match.group(4) or 0)

    # Normalize the time values
    if seconds >= 60:
        minutes += seconds // 60
        seconds = seconds % 60

    if minutes >= 60:
        hours += minutes // 60
        minutes = minutes % 60

    if hours >= 24:
        days += hours // 24
        hours = hours % 24

    # Return the result as a dictionary
    return {
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds
    }

# 'dhms'  tfor remaining
def parse_time_difference(future_time: str) -> dict:
    diff = datetime.datetime.strptime(future_time, f'%Y-%m-%d %H:%M:%S.%f') - datetime.datetime.now()

    pattern = re.compile(r'(?:(\d+) days?, )?(\d+):(\d+):(\d+)(?:\.\d+)?')
    match = pattern.match(str(diff))

    if not match:
        return {}

    # Extracting matched groups and convert to integers
    days = int(match.group(1) or 0)
    hours = int(match.group(2) or 0)
    minutes = int(match.group(3) or 0)
    seconds = int(match.group(4) or 0)

    # Return the result as a dictionary
    return {
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds
    }

#
def time_shortner( time: str, difference: bool = False) -> str:
    str_time = ''
    # difference = True for finding remaining time
    if difference:
        for key, value in parse_time_difference(time).items():
            if value:
                str_time = str_time + f'{value}{key[0]}'
        return str_time

    # just to convert DICT to - 0d0h0m0s format    
    for key, value in parse_time_duration(time).items():
        if value:
            str_time = str_time + f'{value}{key[0]}'
    
    return str_time

# tHESE 3 METHODS 
# 'DHMS' TIME TO 'DHMS' ADDITION AND REDUCTION
def parse_time(time_str):
    """Parse a time string like '1d2h3m4s' into total seconds."""
    time_units = {'d': 86400, 'h': 3600, 'm': 60, 's': 1}
    total_seconds = 0
    matches = re.findall(r'(\d+)([dhms])', time_str)
    for value, unit in matches:
        total_seconds += int(value) * time_units[unit]
    return total_seconds

def format_time(seconds):
    """Format a time duration given in seconds back into '1d2h3m4s' format."""
    time_units = [('d', 86400), ('h', 3600), ('m', 60), ('s', 1)]
    time_str = ''
    for unit, count in time_units:
        if seconds >= count:
            value, seconds = divmod(seconds, count)
            time_str += f'{value}{unit}'
    return time_str if time_str else '0s'

def time_modify_and_shortner(prev_time:str, time_to_add: str, mode: str) -> str:
    # passing strings to dict
    if mode == 'ADD':
        total_seconds = parse_time(prev_time) + parse_time(time_to_add)
        return format_time(total_seconds)
    if mode == 'REDUCE':
        total_seconds = parse_time(prev_time) - parse_time(time_to_add)
        total_seconds = max(total_seconds, 0)  # Avoid negative time
        return format_time(total_seconds)