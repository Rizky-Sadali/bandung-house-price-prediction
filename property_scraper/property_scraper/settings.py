# property_scraper/settings.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Automatically created by: scrapy startproject
BOT_NAME = "property_scraper"

# This is the modern setting to avoid the deprecation warning.
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"

SPIDER_MODULES = ["property_scraper.spiders"]
NEWSPIDER_MODULE = "property_scraper.spiders"

# --- Politeness and Robustness Settings ---
# Sanitized: Load User Agent from environment variable for flexibility and privacy
USER_AGENT = os.getenv("SCRAPER_USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 1 # Send one request at a time
DOWNLOAD_DELAY = 3 # Wait 3 seconds between requests
RETRY_TIMES = 5

# AutoThrottle automatically adjusts scraping speed to be respectful to servers
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# --- PLAYWRIGHT SETTINGS ---
# This tells Scrapy to use Playwright for all http and https requests
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# This specific reactor is required for Playwright to work correctly
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Debugging: Launch headful browser (useful for dev, can be toggled via env in production)
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": os.getenv("HEADLESS_MODE", "False").lower() == "true"
}

# --- DEFAULT SCRAPY SETTINGS ---
# COOKIES_ENABLED = False
# DOWNLOADER_MIDDLEWARES = ...
# ITEM_PIPELINES = ...