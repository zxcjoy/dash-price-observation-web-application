# utils.py
from typing import Optional, Union
import datetime

def sqlize(v: Union[str, int, float, bool, datetime.date, datetime.date]) -> str:
    """
    Convert an input value to a string that matches the data type used in an SQL statement
    """
    if isinstance(v, str):
        v = v.replace("'", "''")
    elif isinstance(v, datetime.datetime):
        v = v.strftime('%Y-%m-%d %H:%M:%S.%f')
    elif isinstance(v, datetime.date):
        v = v.strftime('%Y-%m-%d')
    elif isinstance(v, bool):
        v = int(v)
    return f"'{v}'" if isinstance(v, str) else str(v)

def custom_rounding(row):
    """
    Pandas dataframe function.
    Round the price based on the item, considering the real-world senario of each item
    """
    if row['Item'] in ['USDA Grade-A eggs (Dozen)', 'Wool Socks (Pair)']:
        return round(row['Price'], 2)
    elif row['Item'] == 'Regular Gasoline (Gallon)':
        return round(row['Price'], 3)
    else:
        return row['Price']