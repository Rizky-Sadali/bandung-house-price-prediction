import time
import os
import json
import re
import datetime
from urllib.parse import urljoin
import pyautogui
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- MODIFIED HELPER FUNCTION ---
def parse_full_price(tag):
    """
    Parses a price string that may contain multipliers like 'Miliar' or 'Juta'.
    Handles localized formats (e.g. Rp X.XXX Miliar).
    """
    if not (tag and tag.text):
        return None

    text = tag.get_text(strip=True).lower()
    
    # Find the number part, allowing for commas and dots
    number_match = re.search(r'[\d,\.]+', text)
    if not number_match:
        return None
        
    number_str = number_match.group(0)
    # Standardize number: remove thousand-separator dots, replace decimal comma with dot
    number_str = number_str.replace('.', '').replace(',', '.')
    
    try:
        base_price = float(number_str)
    except ValueError:
        return None

    # Apply multipliers (generic logic)
    if 'miliar' in text or 'b' in text: # 'b' for billions
        return int(base_price * 1_000_000_000)
    if 'juta' in text or 'm' in text:   # 'm' for millions
        return int(base_price * 1_000_000)
        
    return int(base_price)

# --- Other helper functions are unchanged ---
def parse_size_sqm(s):
    if s:
        numbers = re.findall(r"\d+", s)
        return int(numbers[0]) if numbers else None
    return None

def main():
    try:
        # Generic Filenames
        html_filename = "temp_page_snapshot.html"
        jsonl_filename = "platform_b_listings_raw.jsonl"
        
        # Load Base URL from ENV or use placeholder
        base_url = os.getenv("TARGET_PLATFORM_B_URL", "https://www.platform-b.com")
        
        full_path_to_save = os.path.join(os.getcwd(), html_filename)

        print("You have 5 seconds to switch to your open browser window...")
        time.sleep(5)

        print(f"Saving webpage to: {full_path_to_save}")
        pyautogui.hotkey('ctrl', 's')
        time.sleep(2)
        pyautogui.write(full_path_to_save, interval=0.05)
        pyautogui.press('enter')
        
        print("Waiting for the browser to finish saving the file...")
        timeout = 30
        start_time = time.time()
        while not os.path.exists(full_path_to_save):
            time.sleep(0.5)
            if time.time() - start_time > timeout:
                raise TimeoutError("Timed out waiting for the HTML file to be saved.")
        print("File found.")

        print(f"Parsing '{html_filename}'...")
        with open(full_path_to_save, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        listings = []
        # Generic Selector: 'div.listing-card' instead of 'cardSecondary'
        property_cards = soup.select("div.listing-card-container") 
        
        # Fallback if generic selector fails (simulated logic)
        if not property_cards:
             # In a real scenario, this would be the actual site selector
             property_cards = soup.select("div.cardSecondary") 

        print(f"Found {len(property_cards)} property cards.")

        for card in property_cards:
            specs_dict = {}
            url_tag = card.select_one("a[href*='/properti/']")
            
            if not (url_tag and url_tag.get('href')):
                continue

            url = urljoin(base_url, url_tag['href'])
            
            # Generic Selectors
            price_tag = card.select_one(".price-label strong") or card.select_one(".price__tag strong")
            address_tag = card.select_one("address")
            description_tag = card.select_one("div.card-details > p")

            spec_tags = card.select(".attribute-list > div > div")
            bedrooms, bathrooms, land_size, building_size = None, None, None, None
            
            for spec in spec_tags:
                title = spec.get('title', '')
                text = spec.get_text(strip=True)
                if 'Kamar Tidur' in title:
                    bedrooms = re.search(r'\d+', text).group() if re.search(r'\d+', text) else None
                    specs_dict['Kamar Tidur'] = bedrooms
                elif 'Kamar Mandi' in title:
                    bathrooms = re.search(r'\d+', text).group() if re.search(r'\d+', text) else None
                    specs_dict['Kamar Mandi'] = bathrooms
                elif 'Luas Tanah' in title:
                    land_size = parse_size_sqm(text)
                    specs_dict['Luas Tanah'] = f"{land_size} m²" if land_size else None
                elif 'Luas Bangunan' in title:
                    building_size = parse_size_sqm(text)
                    specs_dict['Luas Bangunan'] = f"{building_size} m²" if building_size else None

            item = {
                "id": os.path.basename(os.path.normpath(url)),
                "price": parse_full_price(price_tag),
                "address": address_tag.get_text(strip=True) if address_tag else None,
                "description": description_tag.get_text(strip=True, separator='\n') if description_tag else "",
                "url": url, # Consider hashing this in production
                "scraped_at": datetime.datetime.now().isoformat(),
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "land_size_sqm": land_size,
                "building_size_sqm": building_size,
                "specs": specs_dict
            }
            listings.append(item)

        with open(jsonl_filename, 'a', encoding='utf-8') as f:
            for item in listings:
                f.write(json.dumps(item) + '\n')

        print(f"✅ Success! Appended {len(listings)} listings to '{jsonl_filename}'.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if os.path.exists(full_path_to_save):
            try:
                os.remove(full_path_to_save)
                print(f"Cleaned up '{html_filename}'.")
            except:
                pass

if __name__ == "__main__":
    main()