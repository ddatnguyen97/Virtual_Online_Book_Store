from dotenv import load_dotenv
import logging
from data import extract_data
from config.db_connection import get_connection_string

load_dotenv()
logging.basicConfig(level=logging.INFO)

connection_string = get_connection_string()

query_total_customers = f"""
    select
        count(distinct customer_phone) as total_customers
    from
        customer_info

"""

metrics_total_customers = extract_data(query_total_customers, connection_string)