from datetime import timedelta
from data import extract_data
import pandas as pd

def format_revenue(n):
    if n is None:
        return "0"
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

def get_previous_date(selected_date, connection_string):
    query = f"""
        select
            date
        from
            dim_date
        where
            date < '{selected_date}'
        order by
            date desc
        limit 1       
    """
    result = extract_data(query, connection_string).iloc[0].date
    return result

