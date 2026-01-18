import os
import json
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from .db_setup import get_connection

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "telegram_messages")

def load_json_to_db():
    conn = get_connection()
    cur = conn.cursor()
    
    if not os.path.exists(DATA_DIR):
        print(f"Data directory {DATA_DIR} does not exist.")
        return

    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                channel_name = file.replace(".json", "")
                
                with open(file_path, "r", encoding="utf-8") as f:
                    messages = json.load(f)
                    
                    data_to_insert = [
                        (channel_name, msg["id"], json.dumps(msg))
                        for msg in messages
                    ]
                    
                    insert_query = """
                    INSERT INTO raw_messages (channel_name, message_id, message_data)
                    VALUES %s
                    ON CONFLICT (channel_name, message_id) DO UPDATE 
                    SET message_data = EXCLUDED.message_data,
                        scraped_at = CURRENT_TIMESTAMP
                    """
                    
                    execute_values(cur, insert_query, data_to_insert)
                    print(f"Loaded {len(messages)} messages for {channel_name} from {file_path}")
    
    conn.commit()
    cur.close()
    conn.close()
    print("All data loaded successfully.")

if __name__ == "__main__":
    load_json_to_db()
