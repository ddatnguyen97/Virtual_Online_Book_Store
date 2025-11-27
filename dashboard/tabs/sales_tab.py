import streamlit as st

from data import *
from metrics.sales_metrics import *
from graphs import *
from utils import *
from sidebar import *

import os
from dotenv import load_dotenv

load_dotenv()

def sales_tab(selected_date, connection_string):
    curr_week_start_date, curr_week_end_date = get_current_week_range(selected_date)
    prev_week_start_date, prev_week_end_date = get_previous_week_range(selected_date)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            with st.container(
                horizontal_alignment="center",
                vertical_alignment="center"
            ):
                st.header("Weekly Sales Overview")
        
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

    curr_sales_df = get_sales_summary(curr_week_start_date, curr_week_end_date, connection_string)
    prev_sales_df = get_sales_summary(prev_week_start_date, prev_week_end_date, connection_string)

    columns = [
        "city_province",
        "region",
        "payment_type"
    ]

    key_label = "sales"

    with st.sidebar:
        st.header("Filters")
        filters = build_filters(curr_sales_df, columns, key_label)

    curr_filtered_df = apply_filter(curr_sales_df, filters)
    prev_filtered_df = apply_filter(prev_sales_df, filters)

    curr_total_revenue = curr_filtered_df["total_revenue"].sum()
    curr_total_orders = curr_filtered_df["total_orders"].sum()
    curr_avg_order_value = safe_divide(curr_total_revenue, curr_total_orders)

    prev_total_revenue = prev_filtered_df["total_revenue"].sum()
    prev_total_orders = prev_filtered_df["total_orders"].sum()
    prev_avg_order_value = safe_divide(prev_total_revenue, prev_total_orders)

    total_revenue_metric = create_data_metric(
                                    "Total Revenue",
                                    curr_total_revenue,
                                    prev_total_revenue
                                )
    
    total_orders_metric = create_data_metric(
                                    "Total Orders",
                                    curr_total_orders,
                                    prev_total_orders
                                )
    
    avg_order_metric = create_data_metric(
                                    "Avg Order Value",
                                    curr_avg_order_value,
                                    prev_avg_order_value
                                )

    with st.container():
        col1, col3, col5 = st.columns(3)
        with col1:
            st.plotly_chart(total_revenue_metric, key = "sales_revenue")

        with col3:
            st.plotly_chart(total_orders_metric, key="sales_orders")

        with col5:
            st.plotly_chart(avg_order_metric, key="sales_avg_orders")

    # sales_by_date_df = curr_filtered_df.copy()
    sales_by_date = curr_filtered_df.groupby("date")["total_revenue"].sum().reset_index()
    sales_by_date = create_date_range(
        sales_by_date,
        start_date=sales_by_date["date"].min(),
        end_date=sales_by_date["date"].max()
    )
    sales_by_date['dod_growth'] = sales_by_date["total_revenue"].pct_change() * 100

    sales_by_date_chart = create_line_chart(
                sales_by_date,
                "date",
                "total_revenue",
                height=250,
                x_label="Date",
                y_label="Revenue",
                markers=True
            )

    dod_growth_chart = create_bar_chart(
                sales_by_date,
                "date",
                "dod_growth",
                height=400,
                orientation='v'
            )

    payment_df = curr_filtered_df.copy()
    payment_df = (payment_df.groupby("payment_type")["total_revenue"]
                  .sum()
                  .reset_index()
                  .sort_values("payment_type", ascending=True)
            )
    payment_type_chart = create_pie_chart(
                payment_df,
                names="payment_type",
                values="total_revenue",
                height=400,
                hole=0.4
            )

    with st.container():
        st.subheader("Sales by Date")
        st.plotly_chart(sales_by_date_chart, key = "sales_revenue_by_date")
    
    with st.container():
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            st.subheader("DoD Growth %")
            st.plotly_chart(dod_growth_chart, key = "sales_dod_growth")

        with col2:
            st.subheader("Payment Type")
            st.plotly_chart(payment_type_chart, key = "sales_payment")
        
    # revenue_by_city_df = curr_filtered_df.copy()
    revenue_by_city = curr_filtered_df.groupby("city_province")["total_revenue"].sum().reset_index()
    value_columns=["city_province", "total_revenue"]
    tooltip_fields=["ten_tinh"]  
    key_on="feature.properties.ten_tinh"
    legend_name="Revenue by Province"
    provinces_json_path = os.getenv("GEO_JSON_PATH")
    provinces_json = load_json_file(provinces_json_path)
    
    # revenue_by_region_df = curr_filtered_df.copy()
    revenue_by_region = curr_filtered_df.groupby("region")["total_revenue"].sum().reset_index()

    revenue_by_region_chart = create_bar_chart(
                revenue_by_region,
                y="region",
                x="total_revenue",
                orientation="h",
                height=400,
                x_label="Revenue",
                y_label="Region"
            )

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Sales by City/Province")
            map_obj = create_folium_map_object(
                revenue_by_city,
                provinces_json,
                value_columns,
                key_on,
                legend_name
            )
            render_folium_map(map_obj, provinces_json, tooltip_fields)

        with col2:
            st.subheader("Sales by Region")
            st.plotly_chart(revenue_by_region_chart, key = "sales_revenue_by_region")