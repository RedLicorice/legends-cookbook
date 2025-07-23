import re
import random
from datetime import datetime, timedelta
import hashlib
import pytz


def add_human_interval(dt, interval):
    match = re.match(r'(\d+)\s*(minutes|minute|hours|hour|days|day|weeks|week|months|month)', interval)
    if not match:
        raise ValueError(f"Invalid interval {interval}")

    value, unit = int(match.group(1)), match.group(2)

    if unit == 'minutes' or unit == 'minute':
        return dt + timedelta(minutes=value)
    elif unit == 'hours' or unit == 'hour':
        return dt + timedelta(hours=value)
    elif unit == 'days' or unit == 'day':
        return dt + timedelta(days=value)
    elif unit == 'weeks' or unit == 'week':
        return dt + timedelta(weeks=value)
    elif unit == 'months' or unit == 'month':
        return dt + timedelta(days=value*30)
    else:
        raise ValueError("Unsupported time unit")
    
    return dt

def generate_random_numeric_string(length: int) -> str:
    if length <= 0:
        raise ValueError("Length must be a positive integer")
    return ''.join(random.choices('0123456789', k=length))

def generate_random_alphanumeric_string(length: int) -> str:
    if length <= 0:
        raise ValueError("Length must be a positive integer")
    characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!?$-_.()'
    return ''.join(random.choices(characters, k=length))

def mysql_password_hash(password: str) -> str:
    hash1 = hashlib.sha1(password.encode('utf-8')).digest()
    hash2 = hashlib.sha1(hash1).hexdigest().upper()
    return f"*{hash2}"

def get_tst():
    tz = pytz.timezone('Europe/Rome')
    tst = datetime.now(tz)
    return tst

def get_str_tst():
    tst = get_tst()
    tst.strftime('%Y-%m-%d %H:%M:%S')

