import pytz
from datetime import datetime

fortaleza_tz = pytz.timezone('America/Fortaleza')

def fortaleza_now():
    return datetime.now(fortaleza_tz)
