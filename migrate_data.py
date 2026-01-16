import os
import logging
from dotenv import load_dotenv
import subprocess

load_dotenv()
logging.basicConfig(level=logging.INFO)

def dump_data(host, user, port, password, db_name, dump_file):
    pg_dump_path = os.getenv("PG_DUMP_PATH", "pg_dump")

    command = [
        pg_dump_path,
        '-h', host,
        '-U', user,
        '-p', str(port),
        '-F', 'c',
        '-f', dump_file,
        db_name
    ]

    env = os.environ.copy()
    env['PGPASSWORD'] = password

    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        logging.info(f"Database dump completed successfully: {dump_file}")

    except FileNotFoundError:
        logging.error(f"pg_dump not found at path: {pg_dump_path}")
        raise
    except subprocess.CalledProcessError as e:
        logging.error(f"pg_dump failed: {e.stderr.decode()}")
        raise

def restore_data(host, user, port, password, db_name, dump_file):
    try:
        pg_restore_path = os.getenv("PG_RESTORE_PATH", "pg_restore")
        
        command = [
            pg_restore_path,
            '-h', host,
            '-U', user,
            '-d', db_name,
            '-p', str(port),
            '--no-owner',
            '--no-privileges',
            '-v',
            dump_file
        ]

        env = os.environ.copy()
        env['PGPASSWORD'] = password
        env['PGSSLMODE'] = 'require'

        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        logging.info(f"Database restore completed successfully from: {dump_file}")

    except FileNotFoundError:
        logging.error(f"pg_restore not found at path: {pg_restore_path}")
        raise
    except subprocess.CalledProcessError as e:
        logging.error(f"pg_restore failed: {e.stderr.decode()}")
        raise

if __name__ == "__main__":
    local_user = os.getenv('DB_USER')
    local_password = os.getenv('DB_PASSWORD')
    local_host = os.getenv('DB_HOST')
    local_port = os.getenv('DB_PORT')
    local_db_name = os.getenv('DB_NAME')

    required = {
        "DB_USER": local_user,
        "DB_PASSWORD": local_password,
        "DB_HOST": local_host,
        "DB_PORT": local_port,
        "DB_NAME": local_db_name
    }

    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ValueError(f"Missing required env vars: {missing}")

    dump_file_path = "backup_data/virtual_book_store_dump.dump"

    dump_data(local_host, local_user, local_port, local_password, local_db_name, dump_file_path)
    logging.info("Database dump process completed successfully.")

    neon_user = os.getenv('NEON_DB_USER')
    neon_password = os.getenv('NEON_DB_PASSWORD')
    neon_host = os.getenv('NEON_DB_HOST')
    neon_port = os.getenv('NEON_DB_PORT')
    neon_db_name = os.getenv('NEON_DB_NAME')

    required_neon = {
        "NEON_DB_USER": neon_user,
        "NEON_DB_PASSWORD": neon_password,
        "NEON_DB_HOST": neon_host,
        "NEON_DB_PORT": neon_port,
        "NEON_DB_NAME": neon_db_name
    }
    
    missing_neon = [k for k, v in required_neon.items() if not v]
    if missing_neon:
        raise ValueError(f"Missing required NEON env vars: {missing_neon}")

    restore_data(neon_host, neon_user, neon_port, neon_password, neon_db_name, dump_file_path)
    logging.info("Database restore process completed successfully.")