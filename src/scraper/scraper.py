import requests
from bs4 import BeautifulSoup
from datetime import date
import json, time, os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_page(url: str, retries: int = 3) -> str:
    """Fetch HTML with retry logic (3 attempts, exponential backoff)."""
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)

def extract_fund_name(soup: BeautifulSoup) -> str:
    h1 = soup.select_one("h1.header_schemeName__zL6RN")
    return h1.text.strip() if h1 else "Unknown"

def extract_category(soup: BeautifulSoup) -> str:
    pills = soup.select("div.pills_container__ZxVbm a div.pill12Pill span")
    if len(pills) >= 2:
        return f"{pills[0].text.strip()} - {pills[1].text.strip()}"
    return "Unknown"

def _get_fund_detail(soup: BeautifulSoup, label: str) -> str:
    """Helper to extract values from the fund details container (NAV, Min SIP, Expense Ratio, etc)."""
    details_container = soup.select_one(".fundDetails_fundDetailsContainer__SLn0o")
    if details_container:
        for div in details_container.find_all("div", class_="valign-wrapper bodyLarge contentTertiary fundDetails_gap4__kM__Q"):
            if label.lower() in div.text.lower():
                parent = div.parent
                val_div = parent.select_one(".bodyXLargeHeavy")
                if val_div:
                    return val_div.text.strip()
    return "N/A"

def extract_nav(soup: BeautifulSoup) -> str:
    return _get_fund_detail(soup, "NAV")

def extract_expense_ratio(soup: BeautifulSoup) -> str:
    return _get_fund_detail(soup, "Expense ratio")

def extract_min_sip(soup: BeautifulSoup) -> str:
    return _get_fund_detail(soup, "Min. for SIP")

def extract_exit_load(soup: BeautifulSoup) -> str:
    headings = soup.find_all(["h3", "h4", "h5"], class_="exitLoadStampDutyTax_sectionHeading__OvXm5")
    if not headings:
        # Fallback to exitLoadStampDutyTax_heading__QOf4f
        headings = soup.find_all(["h3", "h4", "h5"], class_="exitLoadStampDutyTax_heading__QOf4f")
    for heading in headings:
        if "exit load" in heading.text.lower():
            next_div = heading.find_next_sibling("div")
            if next_div:
                return next_div.text.strip()
            next_p = heading.find_next_sibling("p")
            if next_p:
                return next_p.text.strip()
    return "N/A"

def extract_riskometer(soup: BeautifulSoup) -> str:
    pills = soup.select("div.pills_container__ZxVbm a div.pill12Pill span")
    for pill in pills:
        if "risk" in pill.text.lower():
            return pill.text.strip()
    return "N/A"

def extract_benchmark(soup: BeautifulSoup) -> str:
    bench_row = soup.select_one("div.investmentObjective_benchmarkRow__tpudX")
    if bench_row:
        val = bench_row.select_one("span.bodyLargeHeavy")
        if val:
            return val.text.strip()
    return "N/A"

def extract_lock_in(soup: BeautifulSoup) -> str:
    headings = soup.find_all(["h3", "h4", "h5"])
    for heading in headings:
        if "lock-in" in heading.text.lower() or "lock in" in heading.text.lower():
            next_div = heading.find_next_sibling("div")
            if next_div:
                return next_div.text.strip()
    return "N/A"

def parse_fund_page(html: str, url: str, amc: str) -> dict:
    """Extract structured fields from a Groww fund page."""
    soup = BeautifulSoup(html, "html.parser")
    return {
        "fund_name":      extract_fund_name(soup),
        "amc":            amc,
        "category":       extract_category(soup),
        "nav":            extract_nav(soup),
        "expense_ratio":  extract_expense_ratio(soup),
        "exit_load":      extract_exit_load(soup),
        "min_sip":        extract_min_sip(soup),
        "riskometer":     extract_riskometer(soup),
        "benchmark":      extract_benchmark(soup),
        "lock_in":        extract_lock_in(soup),
        "source_url":     url,
        "scraped_date":   date.today().strftime("%d-%b-%Y"),
    }

def scrape_all(corpus_urls: dict, output_dir: str = "data/raw"):
    """Scrape all URLs and save as JSON files."""
    import logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    for amc_name, urls in corpus_urls.items():
        amc_dir = os.path.join(output_dir, amc_name.lower().replace(" ", "_"))
        os.makedirs(amc_dir, exist_ok=True)
        for url in urls:
            logging.info(f"Scraping: {url}")
            try:
                html = fetch_page(url)
                data = parse_fund_page(html, url, amc_name)
                slug = url.rstrip("/").split("/")[-1]
                with open(f"{amc_dir}/{slug}.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logging.error(f"Failed to scrape {url}: {e}")
            time.sleep(1)  # polite delay between requests
