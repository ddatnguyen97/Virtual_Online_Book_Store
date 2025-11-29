import streamlit as st

from data import *
from graphs import *
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
    selected_date = display_date(connection_string)

selected_tab = st.session_state.get("selected_tab", "Sales")

selected_tab = st.radio(
                "Tabs:",
                ["Sales", "Customers", "Products"],
                horizontal=True,
                index=["Sales", "Customers", "Products"].index(selected_tab),
            )

st.session_state["selected_tab"] = selected_tab

if selected_tab == "Sales":
    sales_tab(selected_date, connection_string)

elif selected_tab == "Customers":
    customer_tab(selected_date, connection_string)

elif selected_tab == "Products":
    pass
    # product_tab(selected_date, connection_string)
