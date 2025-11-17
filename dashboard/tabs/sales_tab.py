import streamlit as st

from data import *
from metrics.sales_metrics import *
from graphs import *
from filters import *
from utils import *

def sales_tab(selected_date, connection_string  ):
    st.header("Sales Overview")
    total_revenue = get_total_revenue(selected_date, connection_string)
    f_total_revenue = format_revenue(total_revenue)

    total_orders = get_total_orders(selected_date, connection_string)
    
    avg_price_per_order = get_avg_price_per_order(selected_date, connection_string)
    f_avg_price_per_order = format_revenue(avg_price_per_order)

    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            create_data_metric("Total Revenue", f_total_revenue)

        with col2:
            create_data_metric("Total Orders", total_orders)

        with col3:
            create_data_metric("Avg. Price per Order", f_avg_price_per_order)
        