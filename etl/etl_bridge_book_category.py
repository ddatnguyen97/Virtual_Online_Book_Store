import requests
import os
from dotenv import load_dotenv
import logging
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
import hashlib

load_dotenv()
logging.basicConfig(level=logging.INFO)

GG_API_KEY = os.getenv('GG_API_KEY')
PARAMS = {
    "key": GG_API_KEY,
}

def fetch_book_category(response):
    try:
        data = response.json()
        books = []

        if "items" in data:
            items = data["items"]
        else:
            items = [data]
            
        for item in items:
            book_id = item.get('id', 'N/A')
            volume_info = item.get('volumeInfo', {})
            categories = volume_info.get('categories', [])

            books.append({
                "book_id": book_id,
                "categories": ', '.join(categories) if categories else 'N/A',
            })
        volume_df = pd.DataFrame(books, index=None)
        return volume_df
    except Exception as e:
        logging.error(f"Error fetching category data: {e}")
        return pd.DataFrame()
    
def transform_book_category(df):
    try:
        bridge_df = (
            df
            .assign(category=df['categories'].str.split(','))
            .explode('category')
        )

        bridge_df['category'] = (
            bridge_df['category']
            .str.strip()
            .fillna('Uncategorized')
        )

        bridge_df['category_id'] = bridge_df['category'].apply(
            lambda x: int(hashlib.sha256(x.encode()).hexdigest(), 16) % 100000
        )

        return (
            bridge_df[['book_id', 'category_id']]
            .drop_duplicates()
            .reset_index(drop=True)
        )
    except Exception as e:
        logging.error(f"Error transforming category data: {e}")
        return pd.DataFrame()

def load_data_to_db(df, table_name, connection_string):
    try:
        engine = create_engine(connection_string)

        with engine.connect() as connection:
            df.to_sql(
                table_name,
                con=connection,
                index=False,
                if_exists='append',
            )
        logging.info(f"Loaded {df.shape[0]} rows into table '{table_name}'.")

    except Exception as e:
        logging.error(f"Error loading data to database: {e}")
        raise

if __name__ == "__main__":
    book_id_df = pd.read_csv(os.getenv('BOOK_ID_LIST_PATH'))

    book_list = []
    category_list = []
    for id in book_id_df['book_id']:
        URL = f"https://www.googleapis.com/books/v1/volumes/{id}"
        response = requests.get(URL, params=PARAMS)
        volume_df = fetch_book_category(response)
        book_list.append(volume_df)
    
    combined_df = pd.concat(book_list, ignore_index=True)
    transformed_volume_df = transform_book_category(combined_df)
    
    db_config = {
        'username': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'db_name': os.getenv('DB_NAME')
    }
    connection_string = f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['db_name']}"
    table_name = "bridge_book_category"

    load_data_to_db(
        df=transformed_volume_df,
        table_name=table_name,
        connection_string=connection_string,
    )
    logging.info("Bridge book category data pipeline completed.")