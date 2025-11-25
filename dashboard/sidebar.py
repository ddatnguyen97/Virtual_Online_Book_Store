from utils import *
import streamlit as st
from config.db_connection import get_connection_string

connection_string = get_connection_string()

def display_date(connection_string):
    max_date = get_max_date(connection_string)
    selected_date = st.date_input(
        "Selected date",
        value=max_date,          
        max_value=max_date       
    )
    return selected_date

def build_filters(df, cols):
    filters = {}
    for col in cols:
        unique_values = df[col].dropna().unique().tolist()
        clean_column = clean_col_name(col)
        filters[col] = st.multiselect(clean_column,
                                       unique_values)
    return filters

def apply_filter(df, filters):
    for col, selected_values in filters.items():
        if selected_values:
            df = df[df[col].isin(selected_values)]
    return df