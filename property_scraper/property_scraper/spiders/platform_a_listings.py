import scrapy
import json
import os
import datetime
import re
from ..items import PropertyScraperItem
from dotenv import load_dotenv

load_dotenv()

# Helper function to parse price strings from HTML
def parse_price_from_html(s):
    if s and (value := re.search(r"[\d\.,]+", s)):
        price_val = float(value.group(0).replace(".", "").replace(",", "."))
        if "miliar" in s.lower():
            return price_val * 1_000_000_000
        elif "juta" in s.lower():
            return price_val * 1_000_000
    return None


class PlatformAListingsSpider(scrapy.Spider):
    name = "platform_a_listings"  # Sanitized Name
    custom_settings = {
        'FEEDS': {
            'platform_a_properties.json': {'format': 'jsonlines', 'overwrite': True}
        }
    }
    # Load domains/URLs from environment or use placeholders
    allowed_domains = [os.getenv("PLATFORM_A_DOMAIN", "platform-a.com")]
    
    # Generate generic start URLs
    base_url = os.getenv("PLATFORM_A_BASE_URL", "https://www.platform-a.com/sale/houses/")
    start_urls = [
       f"{base_url}?page={x}" for x in range(1, 500) # Set for a larger data collection run
    ]

    def parse(self, response):
        # Generic Selector for property cards
        property_links = response.xpath('//div[contains(@class, "property-card")]//a[@title]/@href').getall()
        for link in property_links:
            yield response.follow(link, callback=self.parse_property)

    def parse_property(self, response):
        item = PropertyScraperItem()
        # Look for generic Schema.org JSON-LD (Product/RealEstateListing)
        script_data = response.xpath('//script[@type="application/ld+json" and contains(text(), "Product")]/text()').get()

        if script_data:
            # --- STRATEGY 1: Parse JSON-LD Structure ---
            try:
                data = json.loads(script_data)
                property_info = data.get('@graph', [{}])[0] 
                place_info = data.get('@graph', [{}, {}])[1]

                item['id'] = property_info.get('sku')
                item['price'] = property_info.get('offers', {}).get('price')
                item['address'] = place_info.get('address', {}).get('streetAddress')
                item['address_locality'] = place_info.get('address', {}).get('addressLocality')
                item['latitude'] = place_info.get('geo', {}).get('latitude')
                item['longitude'] = place_info.get('geo', {}).get('longitude')
                item['description'] = property_info.get('description')
                item['specs'] = self.extract_specs_from_html(response)
            except Exception:
                self.logger.warning(f"Failed to parse JSON-LD for {response.url}")

        else:
            # --- STRATEGY 2: Fallback to HTML Extraction ---
            item['id'] = os.path.basename(os.path.normpath(response.url))
            item['price'] = self.extract_price_from_html(response)
            item['address'] = self.extract_address_from_html(response)
            item['specs'] = self.extract_specs_from_html(response)
            item['description'] = self.extract_description_from_html(response)

        item['url'] = response.url # Consider hashing/masking this
        item['scraped_at'] = datetime.datetime.now().isoformat()

        yield item

    # --- HTML Extractor Functions ---
    def extract_price_from_html(self, response):
        selectors = [
            'p.price-label::text',
            'p.sticky-bar-price::text'
        ]
        for selector in selectors:
            price_text = response.css(selector).get()
            if price_text:
                return parse_price_from_html(price_text)
        return None

    def extract_address_from_html(self, response):
        return response.css('p.property-address::text').get()

    def extract_specs_from_html(self, response):
        specs = {}
        # Generic logic: Find key-value pairs in specification section
        # Finds the parent of the "Kamar Tidur" (Bedroom) label
        spec_rows = response.xpath('//div[p[text()="Kamar Tidur"]]/parent::div/div')
        for row in spec_rows:
            key = row.css('p:nth-child(1)::text').get()
            value = row.css('p:nth-child(2)::text').get()
            if key and value:
                specs[key.strip()] = value.strip()

        # Fallback for "new development" pages
        if not specs:
            specs_div = response.xpath("//div[contains(@class, 'spec-item')]")
            for spec in specs_div:
                row = spec.xpath("./span/text()").getall()
                if len(row) == 2:
                    specs[row[0].strip()] = row[1].strip()
        return specs

    def extract_description_from_html(self, response):
        desc_parts = response.css('div.property-description-text ::text').getall()
        return "\n".join([part.strip() for part in desc_parts if part.strip()])