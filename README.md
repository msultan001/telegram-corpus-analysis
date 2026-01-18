# Telegram Corpus Analysis ELT Pipeline

This project is an end-to-end ELT pipeline for scraping Telegram data and transforming it into a structured dimensional model.

## Folder Structure
- `src/`: Core scraper logic.
- `api/`: FastAPI application.
- `medical_warehouse/`: dbt project for transformations.
- `scripts/`: Ingestion and orchestration scripts.
- `data/`: Local data lake.
- `logs/`: Application logs.
