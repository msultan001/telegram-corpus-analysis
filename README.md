# Telegram Corpus Analysis ELT Pipeline

This project is an end-to-end ELT pipeline for scraping Telegram data and transforming it into a structured dimensional model.

## Folder Structure

## Local DB and image filename expectations

- Ensure Postgres is reachable via environment variables. Create a `.env` in the project root with the following (example):

```
DATABASE_URL="postgresql://postgres:password@localhost:5432/telegram"
```

- Image files must use the filename pattern `<channel_id>_<message_id>.<ext>` (for example `1569871437_187733.jpg`) so the loader can extract `message_id` for joining detections to messages.
