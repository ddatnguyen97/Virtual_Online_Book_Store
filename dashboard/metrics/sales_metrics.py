from dotenv import load_dotenv
import logging
from data import extract_data
from config.db_connection import get_connection_string
from utils import get_week_range

load_dotenv()
logging.basicConfig(level=logging.INFO)

connection_string = get_connection_string()

def get_total_revenue(selected_date, connection_string):
    start_date, end_date = get_week_range(selected_date)
    query = f"""
        select
            sum(bf.retail_price_amount * oi.order_quantity) as total_revenue
        from
            book_info bf 
        join 
            orders_info oi on bf.book_id = oi.book_id
        join
            dim_date d on oi.date_id = d.date_id
        where
            (d.date >= '{start_date}' and d.date <= '{end_date}')
    """
    result = extract_data(query, connection_string).iloc[0].total_revenue
    return result
    
def get_total_orders(selected_date, connection_string):
    start_date, end_date = get_week_range(selected_date)
    query = f"""
        select
            count(distinct order_id) as total_orders
        from
            orders_info oi
        join
            dim_date d on oi.date_id = d.date_id
        where
            (d.date >= '{start_date}' and d.date <= '{end_date}')
    """
    result = extract_data(query, connection_string).iloc[0].total_orders
    return result

def get_avg_price_per_order(selected_date, connection_string):
    start_date, end_date = get_week_range(selected_date)
    query = f"""
        select
            (sum(bf.retail_price_amount * oi.order_quantity)) / (count(distinct oi.order_id)) as avg_order_value
        from
            book_info bf 
        join 
            orders_info oi on bf.book_id = oi.book_id
        join
            dim_date d on oi.date_id = d.date_id
        where
            (d.date >= '{start_date}' and d.date <= '{end_date}')
    """
    result = extract_data(query, connection_string).iloc[0].avg_order_value
    return result

def get_sales_by_region(selected_date, connection_string):
    start_date, end_date = get_week_range(selected_date)
    query = f"""
        select
            dr.name as region,
            dcp.name as city_province,
            sum(bi.retail_price_amount * oi.order_quantity) as total_revenue
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
            dim_date dd on oi.date_id = dd.date_id
        where
            (dd.date >= '{start_date}' and dd.date <= '{end_date}')
        group by
            region,
            city_province
    """
    result = extract_data(query, connection_string)
    return result

def get_sales_metrics(selected_date, connection_string):
    start_date, end_date = get_week_range(selected_date)
    query = f"""
        select
            dr.name as region,
            dcp.name as city_province,
            sum(bi.retail_price_amount * oi.order_quantity) as total_revenue,
            count(distinct oi.order_id) as total_orders,
            (sum(bi.retail_price_amount * oi.order_quantity)) / (count(distinct oi.order_id)) as avg_order_value
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
            dim_date dd on oi.date_id = dd.date_id
        where
            (dd.date >= '{start_date}' and dd.date <= '{end_date}')
        group by
            grouping sets (
                (region,
                city_province),
                (region),
                ()
            )
            
    """
    result = extract_data(query, connection_string)
    return result