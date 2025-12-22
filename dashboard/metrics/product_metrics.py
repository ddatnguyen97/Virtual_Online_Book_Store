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
        select
            dd.date as date,
            sum(oi.order_quantity) as total_quantity_sold,
            sum(bi.retail_price_amount * oi.order_quantity) as total_revenue,
            concat(bi.title, ' - ', coalesce(bi.subtitle, '')) as book_name,
            bi.publisher as publisher,
            dt.thickness as thickness,
            dc.category as category,
            dc.category_lv1 as category_lv1,
            dc.category_lv2 as category_lv2,
            dc.category_lv3 as category_lv3
        from
            orders_info oi
        join
            book_info bi on oi.book_id = bi.book_id
        join 
            bridge_book_category bbc on bi.book_id = bbc.book_id
        join
            dim_category dc on bbc.category_id = dc.category_id
        join
            dim_thickness_type dt on bi.thickness_id = dt.thickness_id
        join
            dim_date dd on oi.date_id = dd.date_id
        where
            (dd.date >= '{start_date}' and dd.date <= '{end_date}')
        group by
            date,
            book_name,
            publisher,
            thickness,
            category,
            category_lv1,
            category_lv2,
            category_lv3
    """
    result = extract_data(query, connection_string)
    return result