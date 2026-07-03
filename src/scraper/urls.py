# src/scraper/urls.py
"""
Corpus URL Registry — all 20 Groww mutual fund scheme pages.

Both AMCs use the same Groww page layout, so a single generic
scraper handles all 20 URLs. No separate scraper per AMC needed.

Usage:
    from src.scraper.urls import CORPUS_URLS
"""

CORPUS_URLS = {
    "Union Mutual Fund": [
        "https://groww.in/mutual-funds/union-small-and-midcap-fund-direct-growth",
        "https://groww.in/mutual-funds/union-liquid-fund-direct-growth",
        "https://groww.in/mutual-funds/union-midcap-fund-direct-growth",
        "https://groww.in/mutual-funds/union-equity-fund-direct-growth",
        "https://groww.in/mutual-funds/union-active-momentum-fund-direct-growth",
        "https://groww.in/mutual-funds/union-childrens-fund-direct-growth",
        "https://groww.in/mutual-funds/union-multi-asset-allocation-fund-direct-growth",
        "https://groww.in/mutual-funds/union-multicap-fund-direct-growth",
        "https://groww.in/mutual-funds/union-gold-etf-fof-direct-growth",
        "https://groww.in/mutual-funds/union-innovation-opportunities-fund-direct-growth",
    ],
    "HDFC Mutual Fund": [
        "https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth",
        "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
        "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth",
        "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
        "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
        "https://groww.in/mutual-funds/hdfc-short-term-opportunities-fund-direct-growth",
        "https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth",
        "https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth",
        "https://groww.in/mutual-funds/hdfc-pharma-and-healthcare-fund-direct-growth",
    ],
}

# ── Integrity guard ────────────────────────────────────────────
_all_urls = [u for urls in CORPUS_URLS.values() for u in urls]
assert len(CORPUS_URLS) == 2,                        "Expected exactly 2 AMCs"
assert "Union Mutual Fund" in CORPUS_URLS,           "Union Mutual Fund key missing"
assert "HDFC Mutual Fund"  in CORPUS_URLS,           "HDFC Mutual Fund key missing"
assert len(CORPUS_URLS["Union Mutual Fund"]) == 10,  "Union MF must have exactly 10 URLs"
assert len(CORPUS_URLS["HDFC Mutual Fund"])  == 10,  "HDFC MF must have exactly 10 URLs"
assert len(set(_all_urls)) == 20,                    "Duplicate URLs detected in CORPUS_URLS"
assert all(
    u.startswith("https://groww.in/mutual-funds/") for u in _all_urls
),                                                   "All URLs must be Groww mutual-fund URLs"
