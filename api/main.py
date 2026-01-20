from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List, Optional
from .database import engine, get_db
from . import schemas
from sqlalchemy import text

app = FastAPI(title="Telegram Corpus API")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Telegram Corpus API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/top-products")
def top_products(limit: int = Query(10, ge=1, le=100)):
    """Return top product image references by detection count."""
    with engine.connect() as conn:
        q = text("SELECT product_label, count(*) as cnt FROM marts.fct_image_detections GROUP BY product_label ORDER BY cnt DESC LIMIT :limit")
        res = conn.execute(q, {"limit": limit}).fetchall()
    return [{"label": r[0], "count": int(r[1])} for r in res]


@app.get("/channel-activity")
def channel_activity(channel_id: Optional[int] = None, days: int = 30):
    """Return message counts per day for a channel (or overall if channel_id omitted)."""
    with engine.connect() as conn:
        if channel_id:
            q = text("SELECT date_key, count(*) FROM marts.fct_messages WHERE channel_id = :cid AND date_key > (current_date - :days)::date GROUP BY date_key ORDER BY date_key")
            res = conn.execute(q, {"cid": channel_id, "days": days}).fetchall()
        else:
            q = text("SELECT date_key, count(*) FROM marts.fct_messages WHERE date_key > (current_date - :days)::date GROUP BY date_key ORDER BY date_key")
            res = conn.execute(q, {"days": days}).fetchall()
    return [{"date": str(r[0]), "count": int(r[1])} for r in res]


@app.get("/message-search")
def message_search(q: str = Query(..., min_length=1), limit: int = Query(50, le=100)):
    """Simple full-text search over message text."""
    with engine.connect() as conn:
        qtext = text("SELECT message_id, channel_id, date_key, text FROM marts.fct_messages WHERE text ILIKE :pat LIMIT :limit")
        likepat = f"%{q}%"
        res = conn.execute(qtext, {"pat": likepat, "limit": limit}).fetchall()
    return [{"message_id": r[0], "channel_id": r[1], "date": str(r[2]), "text": r[3]} for r in res]


@app.get("/visual-content")
def visual_content(label: Optional[str] = None, limit: int = 50):
    """Returns recent images and detection metadata. Filter by label if provided."""
    with engine.connect() as conn:
        if label:
            q = text("SELECT detection_id, image_path, product_label, score FROM marts.fct_image_detections WHERE product_label = :lbl ORDER BY detection_id DESC LIMIT :limit")
            res = conn.execute(q, {"lbl": label, "limit": limit}).fetchall()
        else:
            q = text("SELECT detection_id, image_path, product_label, score FROM marts.fct_image_detections ORDER BY detection_id DESC LIMIT :limit")
            res = conn.execute(q, {"limit": limit}).fetchall()
    return [{"detection_id": int(r[0]), "image_path": r[1], "label": r[2], "score": float(r[3])} for r in res]
