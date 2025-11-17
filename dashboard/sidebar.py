from utils import *
import streamlit as st

from dotenv import load_dotenv
import logging
from data import extract_data
from config.db_connection import get_connection_string

load_dotenv()
logging.basicConfig(level=logging.INFO)

connection_string = get_connection_string()

def display_sidebar(connection_string):
    st.title("Filters")

    max_date = get_max_date(connection_string)
    selected_date = st.date_input(
        "Select Date",
        value=max_date,          
        max_value=max_date       
    )
    return selected_date

