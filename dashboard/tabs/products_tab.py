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
    prev_repeat_products_df = get_repeat_products_purchase(prev_week_start_date, prev_week_end_date, connection_string)
    
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
    prev_repeat_products_filtered_df = apply_filter(prev_repeat_products_df, filters)

    curr_repeat_rate = safe_divide(
        repeat_products_filtered_df["repeat_purchase_count"].sum(),
        repeat_products_filtered_df["total_customers"].sum()
    )
    
    prev_repeat_rate = safe_divide(
        prev_repeat_products_filtered_df["repeat_purchase_count"].sum(),
        prev_repeat_products_filtered_df["total_customers"].sum()
    )

    repeat_metric = create_data_metric(
                                    "Repeat Purchase Rate",
                                    curr_repeat_rate,
                                    prev_repeat_rate,
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

    revenue_quantity_book_df = (
        curr_filtered_df
        .drop_duplicates(subset=["date", "book_id"])
        .groupby("book_id", as_index=False)
        .agg({
            "total_quantity_sold": "sum",
            "total_revenue": "sum",
            "book_name": "first"
        })
    )

    revenue_quantity_book_plot = create_scatter_plot(
        revenue_quantity_book_df,
        x="total_quantity_sold",
        y="total_revenue",
        hover_data=["book_name"],
        x_label="Total Quantity Sold",
        y_label="Total Revenue",
        height=400,
        trendline=True,
        trendline_color_override="#2bb179"
    )

    revenue_quantity_category_df = (
        curr_filtered_df
        .drop_duplicates(subset=["date", "book_id"])
        .groupby(["category_lv1", "category_lv2", "category_lv3"], as_index=False)
        .agg({
            "total_quantity_sold": "sum",
            "total_revenue": "sum",
        })
    )

    revenue_quantity_category_df["avg_revenue_per_unit"] = (
        revenue_quantity_category_df["total_revenue"] /
        revenue_quantity_category_df["total_quantity_sold"]
    )

    revenue_quantity_category_plot = create_scatter_plot(
        revenue_quantity_category_df,
        x="total_quantity_sold",
        y="avg_revenue_per_unit",
        hover_data=["category_lv1", "category_lv2", "category_lv3"],
        color="category_lv1",
        size="total_revenue",
        x_label="Total Quantity Sold",
        y_label="AVG Revenue per Unit",
        height=400
    )

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Revenue vs Quantity Sold per Product")
            st.plotly_chart(revenue_quantity_book_plot, key="products_revenue_quantity_scatter")

        with col2:
            st.subheader("Revenue vs Quantity Sold per Category")
            st.plotly_chart(revenue_quantity_category_plot, key="categories_revenue_quantity_scatter")

    st.divider()
    st.header("Repeat Purchase Analysis")

    repeat_purchase_category = (
        repeat_products_filtered_df
        .groupby("category_lv1", as_index=False)
        .agg({
            "repeat_purchase_count": "sum",
            "total_customers": "sum",
        })
        .sort_values("repeat_purchase_count", ascending=False)
        .head(5)
    )

    repeat_purchase_category["repeat_purchase_rate"] = (
        repeat_purchase_category["repeat_purchase_count"] /
        repeat_purchase_category["total_customers"]
    )

    repeat_purchase_category = repeat_purchase_category.sort_values(
        "repeat_purchase_rate",
        ascending=False
    ).reset_index(drop=True)

    repeat_purchase_category_chart = create_bar_chart(
        repeat_purchase_category,
        x="category_lv1",
        y="repeat_purchase_rate",
        height=400,
        orientation="v",
        tickangle=90,
    )

    top_5_repeat_products = (
        repeat_products_filtered_df
        .groupby(["book_id", "title"], as_index=False)
        .agg({
            "repeat_purchase_count": "max"  
        })
        .sort_values("repeat_purchase_count", ascending=False)
        .head(5)
    )

    top_5_repeat_products["title_short"] = (
        top_5_repeat_products["title"]
        .str.slice(0, 30)
        + "..."
    )
    
    top_5_repeat_products = top_5_repeat_products.sort_values(
        "repeat_purchase_count",
        ascending=False
    ).reset_index(drop=True)

    top_5_repeat_products_chart = create_bar_chart(
        top_5_repeat_products,
        y="title_short",
        x="repeat_purchase_count",
        height=400,
        orientation="h",
    )

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Repeat Purchase Rate per Category")
            st.plotly_chart(repeat_purchase_category_chart, key="repeat_purchase_category")
            
        with col2:
            st.subheader("Top 5 Repeat Purchase Products")
            st.plotly_chart(top_5_repeat_products_chart, key="top_5_repeat_products")

    curr_repeat_detail = (
        repeat_products_filtered_df
        .groupby(["category_lv1"], as_index=False)
        .agg({
            "repeat_purchase_count": "sum",
            "total_customers": "sum"
        })
    )

    curr_repeat_detail["repeat_rate_curr"] = (
        curr_repeat_detail["repeat_purchase_count"] /
        curr_repeat_detail["total_customers"]
    )

    prev_repeat_detail = (
        prev_repeat_products_filtered_df
        .groupby(["category_lv1"], as_index=False)
        .agg({
            "repeat_purchase_count": "sum",
            "total_customers": "sum"
        })
    )

    prev_repeat_detail["repeat_rate_prev"] = (
        prev_repeat_detail["repeat_purchase_count"] /
        prev_repeat_detail["total_customers"]
    )

    repeat_rate_detail_df = (
        curr_repeat_detail
        .merge(
            prev_repeat_detail[["category_lv1", "repeat_rate_prev"]],
            on="category_lv1",
            how="left"
        )
    )

    repeat_rate_detail_df["repeat_rate_delta"] = (
        repeat_rate_detail_df["repeat_rate_curr"] -
        repeat_rate_detail_df["repeat_rate_prev"]
    )

    repeat_rate_detail_df["trend"] = repeat_rate_detail_df["repeat_rate_delta"].apply(
        lambda x: "⬆ Improving" if x > 0.01 else
                "⬇ Declining" if x < -0.01 else
                "→ Stable"
    )

    repeat_rate_detail_df = repeat_rate_detail_df.sort_values(
        "repeat_rate_delta",
        ascending=False
    ).reset_index(drop=True)

    styled_repeat_rate_detail_df = (
        repeat_rate_detail_df[[
            "category_lv1",
            "repeat_rate_curr",
            "repeat_rate_prev",
            "repeat_rate_delta",
            "trend"
        ]]
        .style
        .format({
            "repeat_rate_curr": "{:.2%}",
            "repeat_rate_prev": "{:.2%}",
            "repeat_rate_delta": "{:+.2%}"
        })
        .applymap(color_delta, subset=["repeat_rate_delta"])
    )

    st.subheader("Repeat Purchase Rate – Detailed View")
    st.dataframe(styled_repeat_rate_detail_df, width='stretch')
