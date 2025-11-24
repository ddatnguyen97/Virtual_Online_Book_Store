import streamlit as st

from data import *
from metrics.sales_metrics import *
from graphs import *
from filters import *
from utils import *

import os
from dotenv import load_dotenv

load_dotenv()

def sales_tab(selected_date, connection_string  ):
    curr_week_start_date, curr_week_end_date = get_current_week_range(selected_date)
    prev_week_start_date, prev_week_end_date = get_previous_week_range(selected_date)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header("Sales Overview")
        
        with col2:
            with st.container():
                col1, col2 = st.columns([0.2, 0.8])
                with col1:
                    st.markdown(f"**Start date:** ")
                with col2:
                    st.badge(str(curr_week_start_date), color='violet')

            with st.container():
                col1, col2 = st.columns([0.2, 0.8])
                with col1:
                    st.markdown(f"**End date:** ")
                with col2:
                    st.badge(str(curr_week_end_date), color='violet')

    curr_sales_df = get_sales_summary(curr_week_start_date, curr_week_end_date, connection_string)
    prev_sales_df = get_sales_summary(prev_week_start_date, prev_week_end_date, connection_string)

    curr_total_revenue = curr_sales_df["total_revenue"].sum()
    curr_total_orders = curr_sales_df["total_orders"].sum()
    curr_avg_order_value = safe_divide(curr_total_revenue, curr_total_orders)

    prev_total_revenue = prev_sales_df["total_revenue"].sum()
    prev_total_orders = prev_sales_df["total_orders"].sum()
    prev_avg_order_value = safe_divide(prev_total_revenue, prev_total_orders)

    with st.container():
        col1, col3, col5 = st.columns(3)
        with col1:
            create_data_metric("Total Revenue",
                                curr_total_revenue,
                                prev_total_revenue)

        with col3:
            create_data_metric("Total Orders",
                                curr_total_orders,
                                prev_total_orders)

        with col5:
            create_data_metric("Avg Order Value",
                                curr_avg_order_value,
                                prev_avg_order_value)

    sales_by_date_df = curr_sales_df.copy()
    sales_by_date = sales_by_date_df.groupby("date")["total_revenue"].sum().reset_index()
    
    payment_df = curr_sales_df.copy()
    payment_df = (payment_df.groupby("payment_type")["total_revenue"]
                  .sum()
                  .reset_index()
                  .sort_index(ascending=False)
            )

    with st.container():
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            st.subheader("Sales by Date")
            create_line_chart(
                sales_by_date,
                "date",
                "total_revenue",
                height=400,
                x_label="Date",
                y_label="Revenue",
                markers=True
            )
        with col2:
            st.subheader("Payment Type")
            create_pie_chart(
                payment_df,
                names="payment_type",
                values="total_revenue",
                height=400
            )

    revenue_by_city_df = curr_sales_df.copy()
    revenue_by_city = revenue_by_city_df.groupby("city_province")["total_revenue"].sum().reset_index()
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

    revenue_by_region_df = curr_sales_df.copy()
    revenue_by_region = revenue_by_region_df.groupby("region")["total_revenue"].sum().reset_index()
    revenue_by_region["region"] = pd.Categorical(
        revenue_by_region["region"],
        categories=region_order,
        ordered=True
    )
    revenue_by_region = revenue_by_region.sort_values("region", ascending=False)

    provinces_json = load_json_file(provinces_json_path)

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
            create_bar_chart(
                revenue_by_region,
                y="region",
                x="total_revenue",
                orientation="h",
                height=400,
                x_label="Region",
                y_label="Revenue"
            )