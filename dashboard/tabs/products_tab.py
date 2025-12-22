import streamlit as st

from data import *
from metrics.product_metrics import *
from graphs import *
from utils import *
from sidebar import *

import os
from dotenv import load_dotenv

load_dotenv()

def product_tab(selected_date, connection_string):
    curr_week_start_date, curr_week_end_date = get_current_week_range(selected_date)
    prev_week_start_date, prev_week_end_date = get_previous_week_range(selected_date)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            with st.container(
                horizontal_alignment="center",
                vertical_alignment="center"
            ):
                st.header("Weekly Products Overview")
        
        with col2:
            with st.container(
                horizontal=True,
                horizontal_alignment="center",
                vertical_alignment="bottom"
            ):
                st.text("Week Range:")
                st.badge(str(curr_week_start_date), color="yellow")
                st.text("to")
                st.badge(str(curr_week_end_date), color="yellow")

    curr_customers_df = get_products_summary(curr_week_start_date, curr_week_end_date, connection_string)
    prev_customers_df = get_products_summary(prev_week_start_date, prev_week_end_date, connection_string)

    columns = [
        "category",
        "category_lv1",
        "category_lv2",
        "category_lv3",
        "publisher",
        "thickness"
    ]

    key_label = "products"

    with st.sidebar:
        st.header("Filters")
        filters = build_filters(curr_customers_df, columns, key_label)

    curr_filtered_df = apply_filter(curr_customers_df, filters)
    prev_filtered_df = apply_filter(prev_customers_df, filters)

    curr_total_quantity_sold = curr_filtered_df["total_quantity_sold"].sum()
    prev_total_quantity_sold = prev_filtered_df["total_quantity_sold"].sum()

    curr_avg_revenue = safe_divide(curr_filtered_df["total_revenue"].sum(), curr_total_quantity_sold)
    prev_avg_revenue = safe_divide(prev_filtered_df["total_revenue"].sum(), prev_total_quantity_sold)

    total_quantity_sold_metric = create_data_metric(
                                            "Total Quantity Sold", 
                                            curr_total_quantity_sold, 
                                            prev_total_quantity_sold, 
                                        )

    avg_revenue_metric = create_data_metric(
                                    "Average Revenue per Unit Sold",
                                    curr_avg_revenue,
                                    prev_avg_revenue
                                )
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.plotly_chart(total_quantity_sold_metric, key = "products_quantity_sold")

        with col2:
            st.plotly_chart(avg_revenue_metric, key = "products_avg_revenue")