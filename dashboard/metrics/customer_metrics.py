from dotenv import load_dotenv
import logging
from data import extract_data
from config.db_connection import get_connection_string, get_neon_db_connection_string
from utils import *
import streamlit as st

load_dotenv()
logging.basicConfig(level=logging.INFO)

# connection_string = get_connection_string()
connection_string = get_neon_db_connection_string()


@st.cache_data
def get_customers_summary(start_date, end_date, connection_string):
    query = f"""
        with return_customer as (
            select
                ci.customer_phone as customers,
                count(distinct oi.order_id) as order_count
            from
                orders_info oi
            join
                customer_info ci on oi.customer_phone = ci.customer_phone
            group by
                customers
            having
                count(distinct oi.order_id) >= 2
        )

        select
            dd.date as date,
            dr.name as region,
            dcp.name as city_province,
            sum(bi.retail_price_amount * oi.order_quantity) as total_revenue,
            ci.customer_phone as customers,
            (sum(bi.retail_price_amount * oi.order_quantity)) / count(distinct ci.customer_phone) as avg_sales_per_customer,
            ci.age_group as age_group,
            oi.order_id as order_id,
            count (distinct case when 
                        rc.customers is not null then ci.customer_phone end
            ) as return_customers
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
        left join
            return_customer rc on ci.customer_phone = rc.customers
        where
            (dd.date >= '{start_date}' and dd.date <= '{end_date}')
        group by
            dd.date,
		    dr.name,
		    dcp.name,
		    ci.age_group,
		    ci.customer_phone,
		    oi.order_id,
		    rc.customers;
    """
    result = extract_data(query, connection_string)
    return result

def calculate_rfm(df, date_col, customer_col, order_col, revenue_col):
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])

    rfm = df.groupby(customer_col).agg(
        last_order_date=(date_col, "max"),
        frequency=(order_col, "nunique"),
        monetary=(revenue_col, "sum")
    ).reset_index()

    rfm["recency"] = (pd.Timestamp.today() - rfm["last_order_date"]).dt.days
    
    rfm["r_score"] = safe_qcut(rfm["recency"], 5, labels=[5,4,3,2,1]).astype(int)
    rfm["f_score"] = safe_qcut(rfm["frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
    rfm["m_score"] = safe_qcut(rfm["monetary"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)

    rfm["rfm_score"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]

    return rfm