#!/usr/bin/env python3
"""Load YOLO detection CSVs into Postgres staging table `stg_image_detections`.

Usage:
  python scripts/load_detections.py --csv data/derived/image_detections/detections_20260120T172913Z.csv --db-url <DATABASE_URL> [--dry-run]

If --dry-run is provided the script will parse the CSV and print counts without connecting to the database.
"""
import argparse
import csv
import os
import sys
from datetime import datetime

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True, help="Path to detections CSV")
    p.add_argument("--db-url", help="Postgres connection string (e.g. postgresql://user:pass@host:5432/db)")
    p.add_argument("--dry-run", action="store_true", help="Parse CSV and report counts only")
    return p.parse_args()

def extract_message_id_from_path(image_path):
    # Handles Windows or POSIX paths
    base = os.path.basename(image_path)
    # Expecting <channel_id>_<message_id>.<ext>
    parts = base.split("_")
    if len(parts) < 2:
        return None
    msg_part = parts[1]
    # strip extension
    msg_id = os.path.splitext(msg_part)[0]
    try:
        return int(msg_id)
    except Exception:
        return None

def read_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            # normalize keys
            channel_id = r.get("channel_id")
            image_path = r.get("image_path")
            product_label = r.get("product_label")
            original_label = r.get("original_label")
            score = r.get("score")
            detection_timestamp = r.get("detection_timestamp")

            message_id = None
            if image_path:
                message_id = extract_message_id_from_path(image_path)

            # parse types
            try:
                channel_id = int(channel_id) if channel_id not in (None, "") else None
            except Exception:
                channel_id = None
            try:
                score = float(score) if score not in (None, "") else None
            except Exception:
                score = None
            try:
                dt = datetime.fromisoformat(detection_timestamp) if detection_timestamp else None
            except Exception:
                dt = None

            rows.append({
                "channel_id": channel_id,
                "message_id": message_id,
                "image_path": image_path,
                "product_label": product_label,
                "original_label": original_label,
                "score": score,
                "detection_timestamp": dt,
            })
    return rows

def run_db_load(rows, db_url):
    import psycopg2
    from psycopg2.extras import execute_values

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # Create table if not exists
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS public.stg_image_detections (
            id SERIAL PRIMARY KEY,
            channel_id BIGINT,
            message_id BIGINT,
            image_path TEXT,
            product_label TEXT,
            original_label TEXT,
            score DOUBLE PRECISION,
            detection_timestamp TIMESTAMP
        );
        """
    )
    # Add unique index to prevent duplicates
    cur.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS stg_image_detections_unique_idx ON public.stg_image_detections(channel_id, message_id, image_path, original_label, detection_timestamp);"
    )

    # Prepare insert rows
    values = []
    for r in rows:
        values.append((
            r["channel_id"],
            r["message_id"],
            r["image_path"],
            r["product_label"],
            r["original_label"],
            r["score"],
            r["detection_timestamp"],
        ))

    if not values:
        print("No rows to load.")
        cur.close()
        conn.commit()
        conn.close()
        return

    # Insert with ON CONFLICT DO NOTHING
    insert_sql = (
        "INSERT INTO public.stg_image_detections (channel_id, message_id, image_path, product_label, original_label, score, detection_timestamp) VALUES %s ON CONFLICT DO NOTHING"
    )
    execute_values(cur, insert_sql, values, template=None, page_size=1000)

    conn.commit()
    cur.close()
    conn.close()
    print(f"Loaded {len(values)} rows into public.stg_image_detections")

def main():
    args = parse_args()
    rows = read_csv(args.csv)
    print(f"Parsed {len(rows)} rows from {args.csv}")

    # summary counts
    from collections import Counter
    cnt = Counter((r["product_label"] or "") for r in rows)
    print("Top labels:")
    for label, c in cnt.most_common(10):
        print(f"  {label}: {c}")

    if args.dry_run:
        print("Dry-run: not loading into DB.")
        return

    db_url = args.db_url or os.environ.get("DATABASE_URL")
    if not db_url:
        print("No database URL provided. Use --db-url or set DATABASE_URL environment variable.")
        sys.exit(2)

    run_db_load(rows, db_url)

if __name__ == "__main__":
    main()
