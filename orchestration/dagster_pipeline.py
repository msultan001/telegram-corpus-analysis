from dagster import job, op, schedule, Nothing
import subprocess
import logging

logger = logging.getLogger("dagster_pipeline")


@op
def scrape_op():
    logger.info("Starting scrape op")
    # run scraper script
    subprocess.run(["python", "src/scraper.py"], check=True)
    logger.info("Scrape completed")


@op
def load_op():
    logger.info("Starting load_op - run scripts/load_raw.py")
    subprocess.run(["python", "scripts/load_raw.py"], check=True)
    logger.info("Load completed")


@op
def dbt_op():
    logger.info("Running dbt run and test")
    subprocess.run(["dbt", "deps"], cwd="medical_warehouse", check=True)
    subprocess.run(["dbt", "run", "--profiles-dir", "."], cwd="medical_warehouse", check=True)
    subprocess.run(["dbt", "test", "--profiles-dir", "."], cwd="medical_warehouse", check=True)
    logger.info("dbt completed")


@op
def yolo_op():
    logger.info("Running YOLO detection")
    # Example weights path; in prod, use artifact store path
    subprocess.run(["python", "src/yolo_detect.py", "--weights", "models/yolo_weights.pt"], check=True)
    logger.info("YOLO completed")


@job
def full_pipeline():
    scrape = scrape_op()
    load = load_op()
    dbt = dbt_op()
    yolo = yolo_op()
    dbt
    yolo


@schedule(cron_schedule="0 2 * * *", job=full_pipeline, execution_timezone="UTC")
def daily_schedule(_context):
    return {}
