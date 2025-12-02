import re
import pandas as pd
from datetime import datetime
from dateutil import parser as dparser

def parse_timestamp(ts):
    if ts is None:
        return pd.NaT
    s = str(ts).strip()
    if s == '' or s.lower() in {'nan', 'none', 'null'}:
        return pd.NaT
    s = s.replace(';', ',')
    s = re.sub(r'\bA\.M\.|\bA\.M\b|\bAM\b', 'AM', s, flags=re.IGNORECASE)
    s = re.sub(r'\bP\.M\.|\bP\.M\b|\bPM\b', 'PM', s, flags=re.IGNORECASE)
    s = re.sub(r'([AP]M)\.?', r'\1', s, flags=re.IGNORECASE)
    s = s.replace('º', '')
    s = re.sub(r'(\d)(st|nd|rd|th)\b', r'\1', s, flags=re.IGNORECASE)
    s = s.replace(',', ' ')
    s = s.replace('/', '-')
    s = s.replace('T', ' ')
    s = s.strip()
    try:
        dt = dparser.parse(s, fuzzy=True, dayfirst=False)
        return pd.to_datetime(dt)
    except Exception:
        try:
            dt = dparser.parse(s, fuzzy=True, dayfirst=True)
            return pd.to_datetime(dt)
        except Exception:
            for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%d-%b-%Y %H:%M:%S", "%d-%b-%Y"):
                try:
                    return pd.to_datetime(datetime.strptime(s, fmt))
                except Exception:
                    continue
    return pd.NaT
