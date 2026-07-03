from playwright.sync_api import sync_playwright

def fetch_page_js(url: str) -> str:
    """Fetch JavaScript-rendered HTML using Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        content = page.content()
        browser.close()
        return content
