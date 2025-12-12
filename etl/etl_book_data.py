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

def extract_book_identifiers(identifiers):
    isbn_10 = None
    isbn_13 = None

    for identifier in identifiers:
        if identifier.get('type') == 'ISBN_10':
            isbn_10 = identifier.get('identifier')
        elif identifier.get('type') == 'ISBN_13':
            isbn_13 = identifier.get('identifier')
    return isbn_10, isbn_13

def extract_list_price(list_price):
    amount = list_price.get('amount', 'N/A')
    currency_code = list_price.get('currencyCode', 'N/A')
    return amount, currency_code

def extract_retail_price(retail_price):
    amount = retail_price.get('amount', 'N/A')
    currency_code = retail_price.get('currencyCode', 'N/A')
    return amount, currency_code

def fetch_book_data(response):
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
            sales_info = item.get('saleInfo', {})
            access_info = item.get('accessInfo', {})

            title = volume_info.get('title', 'N/A')
            subtitle = volume_info.get('subtitle', 'N/A')
            authors = volume_info.get('authors', [])
            publisher = volume_info.get('publisher', 'N/A')
            published_date = volume_info.get('publishedDate', 'N/A')

            identifiers = volume_info.get('industryIdentifiers', [])
            isbn_10, isbn_13 = extract_book_identifiers(identifiers)

            page_count = volume_info.get('pageCount', 'N/A')
            print_type = volume_info.get('printType', 'N/A')
            # categories = volume_info.get('categories', [])

            language = volume_info.get('language', 'N/A')

            list_price_info = sales_info.get('listPrice', {})
            list_price_amount, list_price_currency = extract_list_price(list_price_info)

            retail_price_info = sales_info.get('retailPrice', {})
            retail_price_amount, _ = extract_retail_price(retail_price_info)

            text_to_speech_permission = access_info.get('textToSpeechPermission', 'N/A')
            epub_available = access_info.get('epub', {}).get('isAvailable')
            pdf_available = access_info.get('pdf', {}).get('isAvailable', 'N/A')

            books.append({
                "book_id": book_id,
                "title": title,
                "subtitle": subtitle,
                "authors": ', '.join(authors) if authors else 'N/A',
                "publisher": publisher,
                "published_date": published_date,
                "isbn_10": isbn_10,
                "isbn_13": isbn_13,
                "page_count": page_count,
                "print_type": print_type,
                # "categories": ', '.join(categories) if categories else 'N/A',
                "language": language,
                "list_price_amount": list_price_amount,
                "retail_price_amount": retail_price_amount,
                "currency": list_price_currency,
                "text_to_speech_permission": text_to_speech_permission,
                "epub_available": epub_available,
                "pdf_available": pdf_available
            })

        volume_df = pd.DataFrame(books, index=None)
        return volume_df
    
    except Exception as e:
        logging.error(f"Error fetching volume data: {e}")
        return pd.DataFrame()

def create_thickness_id(page_count):
    try:
        if page_count <= 150:
            return "1"
        elif page_count <= 300:
            return "2"
        elif page_count <= 450:
            return "3"
        else:
            return "4"
    except Exception as e:
        logging.error(f"Error creating thickness_id: {e}")
        raise

def transform_book_data(df):
    try:
        df['published_date'] = pd.to_datetime(df['published_date'], errors='coerce')
        numeric_cols = [
            'page_count',
            'list_price_amount', 'retail_price_amount'
        ]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df['thickness_id'] = df['page_count'].apply(create_thickness_id)

        logging.info("Transformed book data successfully.")
        return df

    except Exception as e:
        logging.error(f"Error transforming data: {e}")
        raise

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
    
def transform_dim_book_category(df):
    try:
        categories = (
            df['categories']
            .str.split(',')
            .explode()
            .str.strip()
            .fillna('Uncategorized')
            .unique()
        )

        df_cat = pd.DataFrame(categories, columns=['category'])

        df_cat['category_lv1'] = df_cat['category'].apply(
            lambda x: x.split('/')[0].strip() if len(x.split('/')) > 0 else 'N/A'
        )
        df_cat['category_lv2'] = df_cat['category'].apply(
            lambda x: x.split('/')[1].strip() if len(x.split('/')) > 1 else 'N/A'
        )
        df_cat['category_lv3'] = df_cat['category'].apply(
            lambda x: x.split('/')[2].strip() if len(x.split('/')) > 2 else 'N/A'
        )

        df_cat['category_id'] = df_cat['category'].apply(
            lambda x: int(hashlib.sha256(x.encode()).hexdigest(), 16) % 100000
        )

        return df_cat[['category_id', 'category', 'category_lv1', 'category_lv2', 'category_lv3']]
    except Exception as e:
        logging.error(f"Error transforming category data: {e}")
        raise

def insert_on_conflict_nothing(table, conn, keys, data_iter, index_elements=None):
    try:
        data = [dict(zip(keys, row)) for row in data_iter]
        stmt = insert(table.table).values(data)

        if index_elements:
            stmt = stmt.on_conflict_do_nothing(index_elements=index_elements)

        return conn.execute(stmt).rowcount

    except Exception as e:
        logging.error(f'error during insert: {e}')
        raise

def conflict_method(index_elements):
    def wrapper(table, conn, keys, data_iter):
        return insert_on_conflict_nothing(
            table=table,
            conn=conn,
            keys=keys,
            data_iter=data_iter,
            index_elements=index_elements
        )
    return wrapper

def load_data_to_db(df, table_name, connection_string, index_elements):
    try:
        engine = create_engine(connection_string)

        with engine.connect() as connection:
            df.to_sql(
                table_name,
                con=connection,
                index=False,
                if_exists="append",
                method=conflict_method(index_elements)
            )

        logging.info(f"Loaded {df.shape[0]} rows into table '{table_name}'.")

    except Exception as e:
        logging.error(f"Error loading data: {e}")
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

    book_id_df = pd.read_csv(os.getenv('BOOK_ID_LIST_PATH'))

    book_list = []
    category_list = []
    for id in book_id_df['book_id']:
        URL = f"https://www.googleapis.com/books/v1/volumes/{id}"
        response = requests.get(URL, params=PARAMS)
        volume_df = fetch_book_data(response)
        book_list.append(volume_df)

        category_df = fetch_book_category(response)
        category_list.append(category_df)
    
    combined_df = pd.concat(book_list, ignore_index=True)
    transformed_volume_df = transform_book_data(combined_df)

    table_name = 'book_info'
    load_data_to_db( 
        df=transformed_volume_df,
        table_name=table_name,
        connection_string=connection_string,
        index_elements=['book_id']
    )
    logging.info("Book data pipeline completed.")

    combined_category_df = pd.concat(category_list, ignore_index=True)
    transformed_category_df = transform_dim_book_category(combined_category_df)

    category_table_name = 'dim_category'
    load_data_to_db(
        df=transformed_category_df,
        table_name=category_table_name,
        connection_string=connection_string,
        index_elements=['category_id']
    )
    logging.info("Book category data pipeline completed.")