import streamlit as st

from data import *
from metrics.customer_metrics import *
from graphs import *
from utils import *
from sidebar import *

import os
from dotenv import load_dotenv

load_dotenv()

def customer_tab(selected_date, connection_string):
    curr_week_start_date, curr_week_end_date = get_current_week_range(selected_date)
    prev_week_start_date, prev_week_end_date = get_previous_week_range(selected_date)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            with st.container(
                horizontal_alignment="center",
                vertical_alignment="center"
            ):
                st.header("Weekly Customers Overview")
        
        with col2:
            with st.container(
                horizontal=True,
                horizontal_alignment="center",
                vertical_alignment="bottom"
            ):
                st.text("Week Range:")
                st.badge(str(curr_week_start_date), color='yellow')
                st.text("to")
                st.badge(str(curr_week_end_date), color='yellow')

    curr_customers_df = get_customers_summary(curr_week_start_date, curr_week_end_date, connection_string)
    prev_customers_df = get_customers_summary(prev_week_start_date, prev_week_end_date, connection_string)

    columns = [
        "city_province",
        "region",
        "age_group"
    ]

    key_label = "customers"

    with st.sidebar:
        st.header("Filters")
        filters = build_filters(curr_customers_df, columns, key_label)

    curr_filtered_df = apply_filter(curr_customers_df, filters)
    prev_filtered_df = apply_filter(prev_customers_df, filters)

    curr_total_revenue = curr_filtered_df["total_revenue"].sum()
    curr_total_customers = curr_filtered_df["customers"].nunique()
    curr_avg_sales_per_customer = safe_divide(curr_total_revenue, curr_total_customers)

    prev_total_revenue = prev_filtered_df["total_revenue"].sum()
    prev_total_customers = prev_filtered_df["customers"].nunique()
    prev_avg_sales_per_customer = safe_divide(prev_total_revenue, prev_total_customers)

    total_revenue_metric = create_data_metric(
                                    "Total Revenue",
                                    curr_total_revenue,
                                    prev_total_revenue
                                )
    
    total_customers_metric = create_data_metric(
                                    "Total Customers",
                                    curr_total_customers,
                                    prev_total_customers
                                )

    avg_sales_per_cust_metric = create_data_metric(
                                    "Avg Sales per Customer",
                                    curr_avg_sales_per_customer,
                                    prev_avg_sales_per_customer
                                )
    
    with st.container():
        col1, col3, col5 = st.columns(3)
        with col1:
            st.plotly_chart(total_revenue_metric, key = "customers_revenue")

        with col3:
            st.plotly_chart(total_customers_metric, key = "customers_total")

        with col5:
            st.plotly_chart(avg_sales_per_cust_metric, key = "customers_avg_value")

    customers_by_date = curr_customers_df.groupby("date").agg(
        total_customers=("customers", "nunique")
    ).reset_index()
    customers_by_date_chart = create_bar_chart(
        customers_by_date,
        "date",
        "total_customers",
        height=400,
        orientation="v"
    )

    with st.container():
        st.subheader("Customers by Date")
        st.plotly_chart(customers_by_date_chart, key = "customers_count_by_date")