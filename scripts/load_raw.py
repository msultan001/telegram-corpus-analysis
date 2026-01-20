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
                # Filename pattern: <channel_id>_<channel_name>_<date>.json OR <channel_name>.json
                base = file.replace('.json', '')
                parts = base.split('_')
                channel_id = None
                channel_name = base
                if len(parts) >= 3 and parts[0].isdigit():
                    channel_id = int(parts[0])
                    # join remaining parts except date
                    channel_name = '_'.join(parts[1:-1]) if len(parts) > 2 else parts[1]
                else:
                    channel_name = base

                with open(file_path, "r", encoding="utf-8") as f:
                    messages = json.load(f)

                    data_to_insert = []
                    for msg in messages:
                        cid = channel_id
                        # attempt to read channel_id from message if not in filename
                        if cid is None:
                            cid = msg.get('channel_id')
                        data_to_insert.append((cid, channel_name, msg["id"], json.dumps(msg)))

                    insert_query = """
                    INSERT INTO raw_messages (channel_id, channel_name, message_id, message_data)
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
