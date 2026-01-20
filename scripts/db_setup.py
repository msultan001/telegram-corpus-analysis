import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "telegram_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "password"),
        port=os.getenv("DB_PORT", "5432")
    )

def setup_database():
    commands = (
        """
        CREATE TABLE IF NOT EXISTS raw_messages (
            id SERIAL PRIMARY KEY,
            channel_id BIGINT,
            channel_name TEXT NOT NULL,
            message_id INTEGER NOT NULL,
            message_data JSONB NOT NULL,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(channel_name, message_id)
        )
        """,
    )
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        cur.close()
        conn.commit()
        print("Database setup successfully.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    setup_database()
