import os
from dotenv import load_dotenv

load_dotenv()

def get_connection_string():
    username = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')

    return f"postgresql://{username}:{password}@{host}:{port}/{db_name}"
