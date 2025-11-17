from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)

def extract_data(query, connection_string):
    try:
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        return df
    
    except Exception as e:
        logging.error(f"Error extracting data: {e}")
        return None