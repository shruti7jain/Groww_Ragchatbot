from src.scraper.urls import CORPUS_URLS
from src.scraper.scraper import scrape_all

print("Starting full scrape of all CORPUS_URLS...")
scrape_all(CORPUS_URLS, output_dir="data/raw")
print("Scraping complete.")
