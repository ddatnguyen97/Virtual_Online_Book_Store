from utils import *
import streamlit as st
from config.db_connection import get_connection_string

connection_string = get_connection_string()

def display_date(connection_string):
    max_date = get_max_date(connection_string)
    selected_date = st.date_input(
        "Pick a date",
        value=max_date,          
        max_value=max_date       
    )
    return selected_date

def build_filters(df, cols, key_label):
    filters = {}

    for col in cols:
        unique_values = df[col].dropna().unique().tolist()
        filters[col] = st.multiselect(
            label=col.capitalize(),
            options=unique_values,
            key=f"filter_{key_label}_{col}"
        )

    return filters

def apply_filter(df, filters):
    for col, selected_values in filters.items():
        if selected_values:
            df = df[df[col].isin(selected_values)]
    return df