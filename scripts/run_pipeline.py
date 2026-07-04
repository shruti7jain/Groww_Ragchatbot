import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

import os

def run_script(script_path: str):
    logger.info(f"--- Starting: {script_path} ---")
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()
        subprocess.run([sys.executable, script_path], check=True, env=env)
        logger.info(f"--- Completed: {script_path} ---\n")
    except subprocess.CalledProcessError as e:
        logger.error(f"--- Failed: {script_path} (Exit Code: {e.returncode}) ---")
        sys.exit(e.returncode)
    except FileNotFoundError:
        logger.error(f"--- Failed: {script_path} not found ---")
        sys.exit(1)

def main():
    logger.info("Starting Offline Data Ingestion Pipeline")
    
    # Define the sequence of scripts to execute
    pipeline_scripts = [
        "scripts/run_scraper.py",
        "src/ingestion/chunker.py",
        "scripts/embed_chunks.py",
        "scripts/build_index.py"
    ]
    
    for script in pipeline_scripts:
        run_script(script)
        
    logger.info("Offline Data Ingestion Pipeline completed successfully!")

if __name__ == "__main__":
    main()
