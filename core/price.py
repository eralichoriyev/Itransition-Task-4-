import re

EUR_TO_USD = 1.2

def clean_price(value):
    if value is None:
        return None
    s = str(value).strip()
    if s == '' or s.lower() in {'nan', 'none', 'null'}:
        return None
    is_euro = '€' in s
    cents_matches = re.findall(r"(\d+)¢", s)
    cents_amount = float(cents_matches[0]) / 100 if cents_matches else 0.0
    nums = re.findall(r"\d+\.\d+|\d+", s)
    main_amount = float(nums[0]) if nums else 0.0
    total = main_amount + cents_amount
    if is_euro:
        total *= EUR_TO_USD
    return round(total, 2)

def normalize_string(s):
    if s is None:
        return ''
    ss = str(s).strip().lower()
    if ss in {'nan', 'none', 'null'}:
        return ''
    ss = re.sub(r"\s+", " ", ss)
    return ss

def normalize_phone(p):
    if p is None:
        return ''
    s = str(p).strip()
    if s.lower() in {'nan', 'none', 'null', ''}:
        return ''
    digits = re.sub(r"\D", "", s)
    return digits
