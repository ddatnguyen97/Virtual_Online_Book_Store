from datetime import timedelta
from data import extract_data
import pandas as pd
import json
import streamlit as st

def safe_divide(a, b):
    return a / b if b not in [0, None] else 0

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

def get_current_week_range(selected_date):
    selected_date = pd.to_datetime(selected_date)
    start_of_week = selected_date - timedelta(days=selected_date.weekday())  
    end_of_week = start_of_week + timedelta(days=6) 
    return start_of_week.date(), end_of_week.date()

def get_previous_week_range(selected_date):
    curr_week_start, curr_week_end = get_current_week_range(selected_date)
    prev_week_end = curr_week_start - pd.Timedelta(days=1)
    prev_week_start = prev_week_end - pd.Timedelta(days=6)
    return prev_week_start, prev_week_end

@st.cache_data
def load_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def clean_col_name(col):
    col = col.replace("_", " ").replace("-", " ")
    return col.title()

def create_date_range(df, start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date)
    df = df.set_index("date").reindex(date_range)
    df.index.name = "date"
    df = df.fillna(0)
    return df.reset_index()