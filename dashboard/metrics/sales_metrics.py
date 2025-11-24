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
def get_sales_summary(start_date, end_date, connection_string):
    query = f"""
        select
            dd.date as date,
            dr.name as region,
            dcp.name as city_province,
            sum(bi.retail_price_amount * oi.order_quantity) as total_revenue,
            count(distinct oi.order_id) as total_orders,
            (sum(bi.retail_price_amount * oi.order_quantity)) / (count(distinct oi.order_id)) as avg_order_value,
            dpt.name as payment_type
        from
            orders_info oi
        join
            book_info bi on oi.book_id = bi.book_id
        join
            customer_info ci on oi.customer_phone = ci.customer_phone
        join
            dim_city_province dcp on ci.city_id = dcp.city_id
        join
            dim_region dr on dcp.region_id = dr.region_id
        join
        	dim_payment_type dpt on dpt.payment_id = oi.payment_type_id 
        join 
            dim_date dd on oi.date_id = dd.date_id
        where
            (dd.date >= '{start_date}' and dd.date <= '{end_date}')
        group by
            date,
            region,
            city_province,
            payment_type
    """
    result = extract_data(query, connection_string)
    return result

