import requests
import os
from dotenv import load_dotenv
import logging
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert

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
    
if __name__ == "__main__":
    db_config = {
        'username': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'db_name': os.getenv('DB_NAME')
    }
    connection_string = f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['db_name']}"

    book_id_df = pd.read_csv('data_source\Virtual Book Store Project - Book IDs List.csv')

    book_list = []
    for id in book_id_df['book_id']:
        URL = f"https://www.googleapis.com/books/v1/volumes/{id}"
        response = requests.get(URL, params=PARAMS)
        volume_df = fetch_book_category(response)
        book_list.append(volume_df)
    
    combined_df = pd.concat(book_list, ignore_index=True)
    transformed_volume_df = transform_data(combined_df)
    
    table_name = 'book_info'
    load_data_to_db(transformed_volume_df, table_name, connection_string)
    logging.info("Book data pipeline completed.")