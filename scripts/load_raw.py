import os
import json
import argparse
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "telegram_messages")


def load_json_to_db(dry_run: bool = False):
    """Parse JSON files and either print a dry-run summary or load into Postgres."""
    if not os.path.exists(DATA_DIR):
        print(f"Data directory {DATA_DIR} does not exist.")
        return

    total_files = 0
    total_messages = 0
    sample = []

    if not dry_run:
        # Lazy import DB helpers only when performing a real load
        from .db_setup import get_connection
        import psycopg2
        from psycopg2.extras import execute_values
        conn = get_connection()
        cur = conn.cursor()

    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith(".json"):
                total_files += 1
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
                    total_messages += len(messages)

                    if dry_run:
                        # collect small sample for inspection
                        for m in messages[:3]:
                            sample.append({"channel": channel_name, "id": m.get('id'), "date": m.get('date')})
                        print(f"[dry-run] Parsed {len(messages)} messages for {channel_name} from {file_path}")
                        continue

                    # real load
                    data_to_insert = []
                    for msg in messages:
                        cid = channel_id
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

    if not dry_run:
        conn.commit()
        cur.close()
        conn.close()
        print("All data loaded successfully.")
    else:
        print(f"Dry-run complete: parsed {total_files} files, {total_messages} messages")
        if sample:
            print("Sample messages:")
            for s in sample:
                print(s)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Parse files but do not write to DB')
    args = parser.parse_args()
    load_json_to_db(dry_run=args.dry_run)
