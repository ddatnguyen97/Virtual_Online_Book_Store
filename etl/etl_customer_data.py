import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
import logging

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
        df['customer_phone'] = df['customer_phone'].astype(str)
        df['dob'] = pd.to_datetime(df['dob'], errors='coerce')
        df['city_id'] = df['city_id'].astype(str)
        return df
    
    except Exception as e:
        logging.error(f"Error transforming data: {e}")
        return pd.DataFrame()
    
def insert_on_conflict_nothing(table, conn, keys, data_iter):
    try:
        data = [dict(zip(keys, row)) for row in data_iter]
        stmt = insert(table.table).values(data).on_conflict_do_nothing(index_elements=["customer_phone"])
        result = conn.execute(stmt)
        return result.rowcount
    
    except Exception as e:
        logging.error(f'error during insert: {e}')
        raise


def load_data_to_db(df, table_name, connection_string, method=insert_on_conflict_nothing):
    try:
        engine = create_engine(connection_string)

        with engine.connect() as connection:
            df.to_sql(
                table_name,
                con=connection,
                index=False,
                if_exists='append',
                method=method
            )
        logging.info(f"Loaded {df.shape[0]} rows into table '{table_name}'.")

    except Exception as e:
        logging.error(f"Error loading data to database: {e}")
        raise

if __name__ == "__main__":
    db_config = {
        'username': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'db_name': os.getenv('DB_NAME')
    }
    connection_string = f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['db_name']}"

    data_file = 'data_source\Customer Raw Data.csv'
    df = get_data(data_file)
    transformed_df = transform_data(df)

    table_name = 'customer_info'
    load_data_to_db(transformed_df, table_name, connection_string)
    logging.info("ETL process for customer data completed.")