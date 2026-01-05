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

    curr_products_df = get_products_summary(curr_week_start_date, curr_week_end_date, connection_string)
    prev_products_df = get_products_summary(prev_week_start_date, prev_week_end_date, connection_string)

    repeat_products_df = get_repeat_products_purchase(curr_week_start_date, curr_week_end_date, connection_string)

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
        filters = build_filters(curr_products_df, columns, key_label)

    curr_filtered_df = apply_filter(curr_products_df, filters)
    prev_filtered_df = apply_filter(prev_products_df, filters)

    curr_total_revenue = (
        curr_filtered_df
        .groupby(["date", "book_id"], as_index=False)["total_revenue"]
        .first()
        ["total_revenue"]
        .sum()
    )
    prev_total_revenue = (
        prev_filtered_df
        .groupby(["date", "book_id"], as_index=False)["total_revenue"]
        .first()
        ["total_revenue"]
        .sum()
    )

    curr_total_quantity_sold = (
        curr_filtered_df
        .groupby(["date", "book_id"], as_index=False)["total_quantity_sold"]
        .first()
        ["total_quantity_sold"]
        .sum()
    )
    
    prev_total_quantity_sold = (
        prev_filtered_df
        .groupby(["date", "book_id"], as_index=False)["total_quantity_sold"]
        .first()
        ["total_quantity_sold"]
        .sum()
    )

    curr_avg_revenue = safe_divide(curr_total_revenue, curr_total_quantity_sold)
    prev_avg_revenue = safe_divide(prev_total_revenue, prev_total_quantity_sold)

    total_revenue_metric = create_data_metric(
                                    "Total Revenue",
                                    curr_total_revenue,
                                    prev_total_revenue
                                )

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
    
    repeat_products_filtered_df = apply_filter(repeat_products_df, filters)
    curr_repeat_rate = safe_divide(
        repeat_products_filtered_df["repeat_purchase_count"].sum(),
        repeat_products_filtered_df["total_customers"].sum()
    )
    
    repeat_metric = create_data_metric(
                                    "Repeat Purchase Rate",
                                    curr_repeat_rate,
                                    previous_value=None,
                                    is_percentage=True
                                )

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.plotly_chart(total_revenue_metric, key = "products_total_revenue")

        with col2:
            st.plotly_chart(total_quantity_sold_metric, key = "products_quantity_sold")

        with col3:
            st.plotly_chart(avg_revenue_metric, key = "products_avg_revenue")

        with col4:
            st.plotly_chart(repeat_metric, key = "products_repeat_rate")

    revenue_quantity_scatter_df = (
        curr_filtered_df
        .drop_duplicates(subset=["date", "book_id"])
        .groupby("book_id", as_index=False)
        .agg({
            "total_quantity_sold": "sum",
            "total_revenue": "sum",
            "book_name": "first"
        })
    )

    revenue_quantity_scatter_plot = create_scatter_plot(
        revenue_quantity_scatter_df,
        x="total_quantity_sold",
        y="total_revenue",
        hover_data=["book_name"],
        x_label="Total Quantity Sold",
        y_label="Total Revenue",
        height=500
    )

    with st.container():
        st.plotly_chart(revenue_quantity_scatter_plot, key="products_revenue_quantity_scatter")