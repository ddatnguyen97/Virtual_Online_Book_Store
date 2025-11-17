import pandas as pd
import logging
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

def get_date(sd, ed):
    try:
        start_date = sd
        end_date = ed
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')

        df = pd.DataFrame({
        'date': date_range
        })
        logging.info(f'data extracted: {df.shape[0]} rows')
        return df 

    except Exception as e:
        logging.error(f'error: {e}')
        raise

def transform_data(df):
    try:
        df['date_id'] = df['date'].dt.strftime('%Y%m%d').astype(str)
        df['year'] = df['date'].dt.year
        df['quarter'] = df['date'].dt.quarter
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df = df.drop_duplicates()
        logging.info(f'dropped duplicates: {df.shape[0]} rows')
        return df
    
    except Exception as e:
        logging.error(f'error: {e}')
        raise

def insert_on_conflict_nothing(table, conn, keys, data_iter):
    try:
        data = [dict(zip(keys, row)) for row in data_iter]
        stmt = insert(table.table).values(data).on_conflict_do_nothing(index_elements=["date_id"])
        result = conn.execute(stmt)
        return result.rowcount
    
    except Exception as e:
        logging.error(f'error during insert: {e}')
        raise

def load_data_to_db(df, table_name, connection_string):
    try:
        engine = create_engine(connection_string)

        with engine.connect() as connection:
            df.to_sql(table_name, con=connection, index=False, if_exists='append', method=insert_on_conflict_nothing)
        logging.info(f'{df.shape[0]} date loaded to dw')

    except Exception as e:
        logging.error(f'error: {e}')
        raise
    
    except Exception as e:
        logging.error(f'error: {e}')
        raise

if __name__ == '__main__':
    table_name = 'dim_date'
    start_date = '2025-01-01'
    end_date = '2025-12-31'

    db_config = {
        'username': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'db_name': os.getenv('DB_NAME')
    }
    connection_string = f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['db_name']}"
    
    date_df = get_date(start_date, end_date)
    transformed_df = transform_data(date_df)
    load_data_to_db(transformed_df, table_name, connection_string)
    logging.info('ETL dim_date process completed.')
