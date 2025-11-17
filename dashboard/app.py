import streamlit as st

from data import *
from graphs import *
from filters import *
from utils import *

from sidebar import *
from tabs.customers_tab import *
from tabs.sales_tab import *

from metrics.customer_metrics import *
from metrics.sales_metrics import *

st.set_page_config(
    page_title="Virtual Online Book Store Dashboard",
    layout="wide",
    initial_sidebar_state="auto"
    )

st.markdown(
    """
    <style>
    .stApp {
        background-color: #2F3030;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Virtual Online Book Store Dashboard")
with st.sidebar:
    selected_date = display_sidebar(connection_string)

with st.container():    
    tab1, tab2, tab3 = st.tabs(["Sales", "Customers", "Products"])

    with tab1:
        sales_tab(selected_date, connection_string)

    with tab2:
        customer_tab()
