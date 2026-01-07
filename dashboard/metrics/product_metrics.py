from dotenv import load_dotenv
import logging
from data import extract_data
from config.db_connection import get_connection_string
from utils import *
import streamlit as st

load_dotenv()
logging.basicConfig(level=logging.INFO)

connection_string = get_connection_string()

@st.cache_data
def get_products_summary(start_date, end_date, connection_string):
    query = f"""
        with book_sales as (
            select
                dd.date,
                oi.book_id,
                sum(oi.order_quantity) as total_quantity_sold,
                sum(oi.order_quantity * bi.retail_price_amount) as total_revenue
            from 
                orders_info oi
            join 
                book_info bi on oi.book_id = bi.book_id
            join 
                dim_date dd on oi.date_id = dd.date_id
            where 
                (dd.date >= '{start_date}' and dd.date <= '{end_date}')
            group by 
                dd.date, 
                oi.book_id
        )
        select
            bs.date,
            bs.book_id,
            bs.total_quantity_sold,
            bs.total_revenue,
            concat(bi.title, ' - ', coalesce(bi.subtitle, '')) as book_name,
            bi.publisher,
            dt.thickness,
            dc.category,
            dc.category_lv1,
            dc.category_lv2,
            dc.category_lv3
        from 
            book_sales bs
        join 
            book_info bi on bs.book_id = bi.book_id
        join 
            dim_thickness_type dt on bi.thickness_id = dt.thickness_id
        left join 
            bridge_book_category bbc on bi.book_id = bbc.book_id
        left join 
            dim_category dc on bbc.category_id = dc.category_id
    """
    result = extract_data(query, connection_string)
    return result

# @st.cache_data
# def get_repeat_products_purchase(start_date, end_date, connection_string):
#     query = f"""
#         with base_product_orders as (
#             select
#                 oi.book_id,
#                 oi.customer_phone,
#                 sum(oi.order_quantity) as total_quantity
#             from 
#                 orders_info oi
#             join 
#                 dim_date dd on oi.date_id = dd.date_id
#             where
#                 (dd.date >= '{start_date}' and dd.date <= '{end_date}')
#             group by 
#                 oi.book_id,
#                 oi.customer_phone
#         ),
#         product_repeat_purchases as (
#             select
#                 book_id,
#                 count(*) as total_customers,
#                 count(
#                     case when total_quantity >= 2 then 1 end
#                 ) as repeat_purchase_count
#             from 
#                 base_product_orders
#             group by 
#                 book_id
#         )
#         select
#             prp.book_id,
#             bi.title,
#             --concat(bi.title, ' - ', coalesce(bi.subtitle, '')) as book_name,
#             prp.total_customers,
#             prp.repeat_purchase_count,
#             round(
#                 (repeat_purchase_count::numeric 
#                 / nullif(total_customers, 0)), 2
#             ) as repeat_rate
#         from 
#             product_repeat_purchases prp
#         join 
#           book_info bi on prp.book_id = bi.book_id
#     """
#     result = extract_data(query, connection_string)
#     return result

@st.cache_data
def get_repeat_products_purchase(start_date, end_date, connection_string):
    query = f"""
    with base_product_orders as (
        select
            oi.book_id,
            oi.customer_phone,
            sum(oi.order_quantity) as total_quantity
        from 
            orders_info oi
        join 
            dim_date dd on oi.date_id = dd.date_id
        where 
            (dd.date >= '{start_date}' and dd.date <= '{end_date}')
        group by 
            oi.book_id, 
            oi.customer_phone
    ),
    product_repeat_purchases as (
        select
            book_id,
            count(*) as total_customers,
            count(case when total_quantity >= 2 then 1 end) as repeat_purchase_count
        from 
            base_product_orders
        group by 
            book_id
    )
    select
        prp.book_id,
        bi.title,
        dc.category,
        dc.category_lv1,
        dc.category_lv2,
        dc.category_lv3,
        bi.publisher,
        dt.thickness,
        prp.total_customers,
        prp.repeat_purchase_count,
        round(
            prp.repeat_purchase_count::numeric / nullif(prp.total_customers, 0),
            2
        ) as repeat_rate
    from 
        product_repeat_purchases prp
    join 
        book_info bi on prp.book_id = bi.book_id
    left join 
        bridge_book_category bbc on bi.book_id = bbc.book_id
    left join 
        dim_category dc on bbc.category_id = dc.category_id
    join 
        dim_thickness_type dt on bi.thickness_id = dt.thickness_id
    """
    result = extract_data(query, connection_string)
    return result