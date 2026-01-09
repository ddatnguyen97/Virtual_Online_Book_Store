import requests
import pandas as pd
import os
from dotenv import load_dotenv
import logging
from sqlalchemy import create_engine

load_dotenv()
logging.basicConfig(level=logging.INFO)

def get_data(file_path):
    try:
        df = pd.read_csv(file_path)
        logging.info(f"Successfully read customer data from {file_path}")
        return df
    
    except Exception as e:
        logging.error(f"Error reading customer data: {e}")
        return pd.DataFrame()

def transform_data(df):
    try:
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce', dayfirst=True)
        df['date_id'] = df['order_date'].dt.strftime('%Y%m%d').astype(str)
        df['order_id'] = df['order_id'].astype(str).str.zfill(10)
        df.drop(columns=['order_date'], inplace=True)
        return df
    except Exception as e:
        logging.error(f"Error transforming data: {e}")
        return df
    
def load_data_to_db(df, table_name, connection_string):
    try:
        engine = create_engine(connection_string)

        with engine.connect() as connection:
            df.to_sql(table_name,
                       con=connection,
                       index=False,
                       if_exists='append',)
        logging.info(f'{df.shape[0]} data loaded to dw')

    except Exception as e:
        logging.error(f'error: {e}')
        raise
    
    except Exception as e:
        logging.error(f'error: {e}')
        raise

if __name__ == "__main__":
    table_name = 'orders_info'

    db_config = {
        'username': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'db_name': os.getenv('DB_NAME')
    }
    connection_string = f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['db_name']}"

    # file_path = 'backup_data\order_list.csv'
    file_path = os.getenv('ORDER_DATA_PATH')
    raw_df = get_data(file_path)
    # print(raw_df.head())
    transformed_df = transform_data(raw_df)
    load_data_to_db(transformed_df, table_name, connection_string)
    logging.info("ETL process completed successfully.")