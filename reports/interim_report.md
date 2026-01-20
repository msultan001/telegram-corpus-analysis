# Interim Report — Telegram Corpus Analysis (Kara Solutions)

Date: 2026-01-18

## Understanding and Defining the Business Objective (6 pts)

- **Business goal:** Deliver actionable insights on Ethiopian medical businesses for Kara Solutions: identify sellers, product types, product images, posting cadence, and temporal/geographic patterns to inform outreach and market intelligence and prioritize leads.
- **Relevance of the data & architecture:** Telegram scraping yields first-hand message and media data. Persisting raw JSON and media in a data lake enables reproducible ETL into a Postgres data warehouse. The dbt-driven staging and marts produce a star schema supporting KPI queries and downstream ML/image enrichment (YOLO) and APIs.

## Discussion of Completed Work and Initial Analysis (6 pts)

### Task 1 — Data scraping & data lake

- **Method & entrypoints:** Messages and media have been collected using a Telethon-based scraper. Scraper implementation: [src/scraper.py](src/scraper.py).
- **Raw data organization:**
  - [data/raw/telegram_messages/2026-01-18](data/raw/telegram_messages/2026-01-18) — per-day JSON message dumps.
  - [data/raw/images/CheMed123](data/raw/images/CheMed123) — downloaded product images organized by `channelId_messageId.jpg`.
- **Storage format:** JSON files are stored per-chat/per-day; media files saved alongside with references to file names in message JSONs.
- **Example Telethon flow (conceptual):**

```py
msgs = await client.get_messages(channel, limit=500)
for m in msgs:
    save_json(m.to_dict(), path_for(channel, date))
    if m.photo:
        download_media(m.photo, images_dir)
```

### Task 2 — Postgres loading & dbt

- **ETL / loader:** JSON messages are parsed and loaded into Postgres staging tables. Loader script: [scripts/load_raw.py](scripts/load_raw.py). DB configuration held in [api/database.py](api/database.py).
- **dbt project location:** [medical_warehouse/](medical_warehouse/) (configuration: [medical_warehouse/dbt_project.yml](medical_warehouse/dbt_project.yml)).
- **Key models:**
  - Staging: [medical_warehouse/models/staging/stg_messages.sql](medical_warehouse/models/staging/stg_messages.sql)
  - Marts (star schema):
    - [medical_warehouse/models/marts/dim_channels.sql](medical_warehouse/models/marts/dim_channels.sql)
    - [medical_warehouse/models/marts/dim_dates.sql](medical_warehouse/models/marts/dim_dates.sql)
    - [medical_warehouse/models/marts/fct_messages.sql](medical_warehouse/models/marts/fct_messages.sql)
- **Star schema overview:** `fct_messages` (facts: message_id, channel_id, date_key, text, media_ref, price_extracted) joins to `dim_channels` (channel metadata) and `dim_dates` (date dimension).

#### Schema diagram (ASCII)

dim_channels        dim_dates
    \                 /
     \               /
      \             /
       -> fct_messages <-

`fct_messages(channel_id FK -> dim_channels.channel_id, date_key FK -> dim_dates.date_key)`

#### dbt tests and quality checks

- Schema tests are declared in `models/schema.yml` with `not_null`, `unique`, and `relationships` tests for PK/FK integrity (see [medical_warehouse/models/schema.yml](medical_warehouse/models/schema.yml)).
- To run locally:

```bash
cd medical_warehouse
dbt deps
dbt run --profiles-dir .
dbt test --profiles-dir .
```

- **Initial observations:**
  - Most messages include reliable channel identifiers and timestamps. Some records have nulls in optional fields (e.g., extracted price) and occasional missing media rehydration failures.
  - Recommendation: run `dbt test` consistently after each incremental load; add freshness/source tests if ingestion latency matters.

## Next Steps and Key Areas of Focus (4 pts)

### YOLO-based image enrichment

- **Objective:** Detect product bounding boxes and generate labels (product type, packaging, text regions for price/brand) to augment message-level data.
- **Pipeline:** Batch-run YOLO inference (e.g., YOLOv8/YOLO-NG) over `data/raw/images/*` → store detection JSON sidecars and normalized rows in Postgres `image_detections` table; link to `fct_messages.media_ref` via `detection_id`.
- **Implementation notes:**
  - Use GPU-enabled container for inference.
  - Version and store model weights/config in an artifacts directory; capture model version in detection records.
  - Create a small validation subset from `CheMed123` for baseline metrics (precision/recall).

### FastAPI endpoints

- **Planned endpoints:**
  - `GET /messages/{channel_id}` — paginated messages with detection metadata.
  - `GET /images/{detection_id}` — image with bounding boxes and labels.
  - `POST /search` — filter messages by label/date/price.
- **Integration points:** Extend `api/main.py` and use `api/database.py` for DB connections; add caching (Redis) for heavy list endpoints and simple API-key auth.

### Dagster orchestration

- **Planned jobs:**
  - `ingest_telethon_job` — incremental scraping and raw persist.
  - `load_postgres_job` — parse JSON and load staging tables.
  - `dbt_run_job` — run `dbt run` and `dbt test` post-load.
  - `yolo_enrich_job` — batch image inference and DB writes.
  - `api_deploy_job` — optional deploy trigger for FastAPI service reloads.
- **Scheduling:** daily incremental schedule, with manual backfill for historical scraping as needed.

### Anticipated challenges

- OCR/price extraction from images, inconsistent message structure, media download reliability, and GPU resource availability for YOLO inference.

## Report Structure, Clarity, and Conciseness (4 pts)

- This report uses clear headings and an ASCII schema. Appendix includes runnable commands and key file references.

### Appendix — Key files & commands

- Scraper: [src/scraper.py](src/scraper.py)
- Loader: [scripts/load_raw.py](scripts/load_raw.py)
- dbt models: [medical_warehouse/models/marts/fct_messages.sql](medical_warehouse/models/marts/fct_messages.sql)

Run dbt locally:

```bash
cd medical_warehouse
dbt deps
dbt run --profiles-dir .
dbt test --profiles-dir .
```

Run conversion (if using pandoc locally):

```bash
pandoc reports/interim_report.md -o reports/interim_report.pdf
```

---

Prepared for Kara Solutions — interim deliverable covering Task 1 & Task 2 results, and planned extensions for YOLO enrichment, FastAPI endpoints, and Dagster orchestration.
