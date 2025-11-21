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
    curr_week_start_date = get_week_range(selected_date)[0]
    curr_week_end_date = get_week_range(selected_date)[1]
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header("Sales Overview")
        
        with col2:
            st.markdown(f"**Start date:** {curr_week_start_date}")
            st.markdown(f"**End date:** {curr_week_end_date}")

    previous_week_date = get_previous_week_range(selected_date)

    sales_df = get_sales_metrics(selected_date, connection_string)
    prev_sales_df = get_sales_metrics(previous_week_date, connection_string)

    summary_df = sales_df.query("region.isna() and city_province.isna()")
    if summary_df.empty:
        st.error("No grand total row returned. Check SQL or data.")
        st.stop()

    summary = summary_df.iloc[0]
    prev_summary = prev_sales_df.query("region.isna() and city_province.isna()").iloc[0]

    current_date_revenue = summary.total_revenue
    previous_date_revenue = prev_summary.total_revenue

    current_date_orders = summary.total_orders
    previous_date_orders = prev_summary.total_orders

    curr_avg_price_per_order = summary.avg_order_value
    prev_avg_price_per_order = prev_summary.avg_order_value

    with st.container():
        # col1, col2, col3, col4, col5 = st.columns(5)
        col1, col3, col5 = st.columns(3)
        with col1:
            create_data_metric("Total Revenue", current_date_revenue, previous_date_revenue)

        with col3:
            create_data_metric("Total Orders", current_date_orders, previous_date_orders)

        with col5:
            create_data_metric("Avg Order Value", curr_avg_price_per_order, prev_avg_price_per_order)

    region_sales_df = sales_df.query("region.notna() and city_province.isna()").copy()
    revenue_by_city = sales_df.query("city_province.notna()").copy()
    value_columns=["city_province", "total_revenue"]
    tooltip_fields=["TinhThanh"]  
    key_on="feature.properties.TinhThanh"
    legend_name="Revenue by Province"
    provinces_json_path = os.getenv("GEO_JSON_PATH")
    
    region_order = [
        "Northeast",
        "Northwest",
        "Red River Delta",
        "North Central Coast",
        "South Central Coast",
        "Southeast",
        "Mekong Delta"
    ]

    region_sales_df["region"] = pd.Categorical(
        region_sales_df["region"],
        categories=region_order,
        ordered=True
    )
    region_sales_df = region_sales_df.sort_values("region")

    with open(provinces_json_path, "r", encoding="utf-8") as f:
        provinces_json = json.load(f)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            create_folium_map(
                revenue_by_city,
                geo_data=provinces_json,
                value_columns=value_columns,
                tooltip_fields=tooltip_fields,
                key_on=key_on,
                legend_name=legend_name
            )

        with col2:
            create_bar_chart(
                region_sales_df,
                x="region",
                y="total_revenue",
                horizontal=True,
            )