import subprocess
import logging
import os
import sys

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Setup Logging
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(ROOT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "pipeline.log")),
        logging.StreamHandler()
    ]
)

def run_command(command, cwd=None):
    logging.info(f"Running command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode == 0:
        logging.info(f"Successfully ran: {command}")
        if result.stdout:
            logging.debug(result.stdout)
    else:
        logging.error(f"Error running: {command}")
        logging.error(result.stderr)
        raise Exception(f"Command failed: {command}")

def main():
    logging.info("Starting Telegram ELT Pipeline")
    
    try:
        # Step 1: Scrape Data
        logging.info("Step 1: Scraping data from Telegram...")
        run_command("python src/scraper.py", cwd=ROOT_DIR)
        
        # Step 2: Load Raw Data to PostgreSQL
        logging.info("Step 2: Loading raw data to PostgreSQL...")
        run_command("python scripts/load_raw.py", cwd=ROOT_DIR)
        
        # Step 3: Run dbt Transformations
        logging.info("Step 3: Running dbt transformations...")
        dbt_cwd = os.path.join(ROOT_DIR, "medical_warehouse")
        run_command("dbt run --profiles-dir .", cwd=dbt_cwd)
        run_command("dbt test --profiles-dir .", cwd=dbt_cwd)
        
        logging.info("Pipeline completed successfully!")
        
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()
