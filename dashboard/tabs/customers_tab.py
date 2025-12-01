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
                st.badge(str(curr_week_start_date), color="yellow")
                st.text("to")
                st.badge(str(curr_week_end_date), color="yellow")

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

    curr_total_customers = curr_filtered_df["customers"].nunique()

    prev_total_customers = prev_filtered_df["customers"].nunique()

    rfm_base = calculate_rfm(curr_filtered_df,
                            "date",
                            "customers",
                            "order_id",
                            "total_revenue")
    rfm_base["customer_segment"] = rfm_base["rfm_score"].apply(customer_segmentation)
    avg_recency = rfm_base["recency"].mean()
    avg_frequency = rfm_base["frequency"].mean()
    avg_monetary = rfm_base["monetary"].mean()
    
    total_customers_metric = create_data_metric(
                                    "Total Customers",
                                    curr_total_customers,
                                    prev_total_customers
                                )

    avg_recency_metric = create_data_metric(
                                    "Avg Recency",
                                    avg_recency
                                )
    
    avg_frequency_metric = create_data_metric(
                                    "Avg Frequency",
                                    avg_frequency
                                )
    
    avg_monetary_metric = create_data_metric(
                                    "Avg Monetary",
                                    avg_monetary
                                )
    
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.plotly_chart(total_customers_metric, key = "customers_total") 

        with col2:
            st.plotly_chart(avg_recency_metric, key = "avg_recency") 

        with col3:
            st.plotly_chart(avg_frequency_metric, key = "avg_frequency")
        
        with col4:
            st.plotly_chart(avg_monetary_metric, key = "avg_monetary")
        

    customers_by_date = curr_filtered_df.groupby("date").agg(
        total_customers=("customers", "nunique")
    ).reset_index()

    customers_by_date_chart = create_bar_chart(
        customers_by_date,
        "date",
        "total_customers",
        height=400,
        orientation="v"
    )

    age_group_category_order = [
        "Under 18",
        "18 - 22",
        "23 - 30",
        "Over 30"
    ]
    revenue_by_age_group = curr_filtered_df.groupby("age_group").agg(
        total_revenue=("total_revenue", "sum"),
    ).reset_index()
    revenue_by_age_group = revenue_by_age_group.sort_values(
        by="age_group",
        key=lambda x: x.map({group: i for i, group in enumerate(age_group_category_order)}),
        ascending=False
    )

    revenue_by_age_group_chart = create_bar_chart(
        revenue_by_age_group,
        y="age_group",
        x="total_revenue",
        height=400,
        orientation="h"
    )

    customers_by_city = curr_filtered_df.groupby("city_province")["customers"].nunique().reset_index()
    value_columns=["city_province", "customers"]
    tooltip_fields=["ten_tinh"]  
    key_on="feature.properties.ten_tinh"
    legend_name="Customers by Province"
    provinces_json_path = os.getenv("GEO_JSON_PATH")
    provinces_json = load_json_file(provinces_json_path)

    with st.container():
        st.header("Customer Demographics")
        col1, col2, col3 = st.columns([0.4, 0.3, 0.3])
        with col1:
            st.subheader("Customers by Date")
            st.plotly_chart(customers_by_date_chart, key = "customers_count_by_date")
        
        with col2:
            st.subheader("Age Group")
            st.plotly_chart(revenue_by_age_group_chart, key = "revnue_by_age_group")
        
        with col3:
            st.subheader("City/Province")
            map_obj = create_folium_map_object(
                customers_by_city,
                provinces_json,
                value_columns,
                key_on,
                legend_name
            )
            render_folium_map(map_obj, provinces_json, tooltip_fields)

    st.divider()
    st.header("RFM Analysis")

    rfm_score_histogram_chart = create_histogram_chart(
                                    rfm_base,
                                    "rfm_score",
                                    nbins=20,
                                    height=250
                                )
    with st.container():
        st.subheader("RFM Score Distribution")
        st.plotly_chart(rfm_score_histogram_chart, key="rfm_score_histogram")

    segment_order = [
        "Champions",
        "Potential loyalists",
        "At risk",
        "Can't lose",
        "Lost"
    ]

    customers_grouped_by_segment = rfm_base.groupby("customer_segment").agg(
        customer_count=("customers", "nunique")
    ).reset_index()
    customers_grouped_by_segment = customers_grouped_by_segment.sort_values(
        by="customer_segment",
        key=lambda x: x.map({segment: i for i, segment in enumerate(segment_order)}),
        ascending=False
    )

    customers_segment_chart = create_treemap_chart(
        customers_grouped_by_segment,
        ["customer_segment"],
        "customer_count",
        height=400,
    )
    column_width = [80, 120, 60, 100, 60, 60, 60, 60, 140]
    rfm_detail_table = create_data_table(
        rfm_base,
        height=400,
        column_width=column_width
    )
    
    with st.container():
        col1, col2 = st.columns([0.35, 0.65])
        with col1:
            st.subheader("Customer Segmentation")
            st.plotly_chart(customers_segment_chart, key="customers_segment_bar_chart")

        with col2:
            st.subheader("Details")
            st.plotly_chart(rfm_detail_table, key="rfm_detail_table")
