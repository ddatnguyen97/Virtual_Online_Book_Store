from datetime import timedelta
from data import extract_data
import pandas as pd

def format_revenue(n):
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.2f}B"
    elif n >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    elif n >= 1_000:
        return f"{n/1_000:.2f}K"
    return str(n)

def get_max_date(connection_string):
    query = f"""
        select
            max(date_id) as max_date
        from
            orders_info
    """
    result = extract_data(query, connection_string).iloc[0].max_date

    return pd.to_datetime(result)

def get_min_date(connection_string):
    query = f"""
        select
            min(date_id) as min_date
        from
            orders_info
    """
    result = extract_data(query, connection_string).iloc[0].min_date
    return pd.to_datetime(result)

def get_time_interval(connection_string):
    max_date = get_max_date(connection_string)
    min_date = get_min_date(connection_string)
    if (max_date - min_date).days == 0:
        return max_date - timedelta(days=1)
    