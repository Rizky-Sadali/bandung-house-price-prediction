import json
import re
import datetime
import os
from urllib.parse import urljoin
from parsel import Selector
from playwright.sync_api import sync_playwright, TimeoutError
from dotenv import load_dotenv

# Load environment variables for paths and keys
load_dotenv()

# --- Helper Functions (Generic) ---
def parse_full_price(s):
    if s: numbers = re.findall(r"\d+", s); return int("".join(numbers)) if numbers else None
    return None

def parse_size_sqm(s):
    if s and isinstance(s, str): numbers = re.findall(r"\d+", s); return int(numbers[0]) if numbers else None
    return None
    
def extract_specs(selector):
    """
    Generic function to extract key-value specs from a listing page.
    Selectors should be adjusted based on the target site structure.
    """
    specs = {}
    # Example logic for 'Platform A' structure
    for spec_item in selector.css('div.generic-listing-overview > div'):
        parts = [part.strip() for part in spec_item.css('::text').getall() if part.strip()]
        if len(parts) == 2: value, key = parts; specs[key] = value
    
    for row in selector.css("div.generic-detail-table table tr"):
        keys = row.css('td.header p::text').getall()
        values = row.css('td.description p::text').getall()
        if len(keys) == len(values):
            for i in range(len(keys)): specs[keys[i].strip()] = values[i].strip()
    return specs

# --- Main Scraping Script ---
def run_manual_scraper():
    # --- PATHS LOADED FROM ENV (Privacy Protection) ---
    # executable_path and user_data_dir should be set in your .env file
    executable_path = os.getenv("CHROME_EXECUTABLE_PATH", "default/path/to/chrome")
    user_data_dir = os.getenv("CHROME_USER_DATA_DIR", "default/path/to/profile")

    if "default/path" in user_data_dir:
        print("❌ CONFIG ERROR: Please set CHROME_USER_DATA_DIR in your .env file.")
        return

    print("🚨 IMPORTANT: Make sure all Chrome windows are closed before proceeding.")
    input("   Press ENTER to launch the browser...")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            channel="chrome",
            executable_path=executable_path,
            ignore_default_args=["--enable-automation"],
            permissions=["geolocation"],
            geolocation={"latitude": float(os.getenv("TARGET_LAT", 0.0)), 
                         "longitude": float(os.getenv("TARGET_LON", 0.0))}
        )
        page = context.new_page()

        # Load target URL from environment or use a placeholder
        start_url = os.getenv("TARGET_SCRAPE_URL", "https://www.generic-property-site.com/listings")
        print(f"Controlling your 'Scraper' Chrome profile. Navigating to: {start_url}")
        
        try:
            page.goto(start_url, wait_until='domcontentloaded', timeout=90000)
        except TimeoutError:
             print("Page load timed out. The site might be slow. Try running again.")
             context.close()
             return

        print("✅ Scraper profile is now running. The browser window should be fully interactive.")
        
        while True:
            print("\n--------------------------------------------------------------------")
            choice = input(">>> Press ENTER to scrape the page (or type 'q' and ENTER to quit): ")

            if choice.lower() == 'q':
                break

            current_search_page_url = page.url
            
            print("Waiting for listing links to appear...")
            try:
                # Generic selector for listing cards
                page.wait_for_selector('//h2/parent::a', timeout=60000)
                print("✅ Listings found. Starting scrape.")
            except TimeoutError:
                print("❌ Timed out waiting for listings.")
                continue

            # Extract page number from URL for clean file naming
            page_match = re.search(r'page=(\d+)', current_search_page_url)
            current_page = int(page_match.group(1)) if page_match else 1
            filename = f"platform_a_listings_page_{current_page}.jsonl"
            
            print(f"Scraping page {current_page}...")
            selector = Selector(text=page.content())
            property_links = selector.xpath('//h2/parent::a/@href').getall()
            print(f"Found {len(property_links)} listings.")
            
            scraped_items = []
            for i, link in enumerate(property_links):
                if "/projects/" in link: continue # Skip ads/projects
                full_url = urljoin(current_search_page_url, link)
                print(f"   > Scraping item {i+1}/{len(property_links)}...")
                try:
                    page.goto(full_url, wait_until='domcontentloaded', timeout=60000)
                    item_selector = Selector(text=page.content())
                    specs = extract_specs(item_selector)
                    
                    # Generic Item Structure
                    item = {
                        'url': full_url, # Note: You might want to mask this in production
                        'price': parse_full_price(item_selector.css('div.price-tag strong::text').get()),
                        'address': item_selector.css('address.location-text::text').get(),
                        'bedrooms': specs.get('Kamar Tidur'),
                        'bathrooms': specs.get('Kamar Mandi'),
                        'land_size_sqm': parse_size_sqm(specs.get('Luas Tanah')),
                        'building_size_sqm': parse_size_sqm(specs.get('Luas Bangunan')),
                        'scraped_at': datetime.datetime.now().isoformat(),
                        'all_specs': specs
                    }
                    scraped_items.append(item)
                except Exception as e:
                    print(f"     [ERROR] Failed to scrape item: {e}")
                finally:
                    page.goto(current_search_page_url, wait_until='domcontentloaded') 

            with open(filename, 'w', encoding='utf-8') as f:
                for item in scraped_items:
                    f.write(json.dumps(item) + '\n')
            
            print(f"\n✅ Success! Saved {len(scraped_items)} listings to '{filename}'.")
            print(">>> Script is paused. Click 'Next Page' in the browser.")

        print("Exiting. Closing browser.")
        context.close()

if __name__ == "__main__":
    run_manual_scraper()