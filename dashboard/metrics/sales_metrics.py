from dotenv import load_dotenv
import logging
from data import extract_data
from config.db_connection import get_connection_string

load_dotenv()
logging.basicConfig(level=logging.INFO)

connection_string = get_connection_string()

def get_total_revenue(selected_date, connection_string):
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
            d.date = '{selected_date}'
    """
    result = extract_data(query, connection_string).iloc[0].total_revenue
    return result
    
def get_total_orders(selected_date, connection_string):
    query = f"""
        select
            count(distinct order_id) as total_orders
        from
            orders_info oi
        join
            dim_date d on oi.date_id = d.date_id
        where
            d.date = '{selected_date}'
    """
    result = extract_data(query, connection_string).iloc[0].total_orders
    return result

def get_avg_price_per_order(selected_date, connection_string):
    query = f"""
        select
            (sum(bf.retail_price_amount * oi.order_quantity)) / (count(distinct oi.order_id)) as avg_price_per_order
        from
            book_info bf 
        join 
            orders_info oi on bf.book_id = oi.book_id
        join
            dim_date d on oi.date_id = d.date_id
        where
            d.date = '{selected_date}'
    """
    result = extract_data(query, connection_string).iloc[0].avg_price_per_order
    return result