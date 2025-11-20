import streamlit as st

from data import *
from metrics.sales_metrics import *
from graphs import *
from filters import *
from utils import *

import os
from dotenv import load_dotenv
import json

load_dotenv()

def sales_tab(selected_date, connection_string  ):
    st.header("Sales Overview")
    previous_date = get_previous_date(selected_date, connection_string)

    current_date_revenue = get_total_revenue(selected_date, connection_string)
    previous_date_revenue = get_total_revenue(previous_date, connection_string)

    current_date_orders = get_total_orders(selected_date, connection_string)
    previous_date_orders = get_total_orders(previous_date, connection_string)
    
    curr_avg_price_per_order = get_avg_price_per_order(selected_date, connection_string)
    prev_avg_price_per_order = get_avg_price_per_order(previous_date, connection_string)

    with st.container():
        # col1, col2, col3, col4, col5 = st.columns(5)
        col1, col3, col5 = st.columns(3)
        with col1:
            create_data_metric("Total Revenue", current_date_revenue, previous_date_revenue)

        with col3:
            create_data_metric("Total Orders", current_date_orders, previous_date_orders)

        with col5:
            create_data_metric("Avg Order Value", curr_avg_price_per_order, prev_avg_price_per_order)

    revenue_by_region = get_sales_by_region(selected_date, connection_string)
    value_columns=["city_province", "total_revenue"]
    tooltip_fields=["TinhThanh"]  
    key_on="feature.properties.TinhThanh"
    legend_name="Revenue by Province"
    provinces_json_path = os.getenv("GEO_JSON_PATH")
    with open(provinces_json_path, "r", encoding="utf-8") as f:
        provinces_json = json.load(f)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            create_folium_map(
                revenue_by_region,
                geo_data=provinces_json,
                value_columns=value_columns,
                tooltip_fields=tooltip_fields,
                key_on=key_on,
                legend_name=legend_name
            )