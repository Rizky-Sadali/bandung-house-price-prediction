import scrapy
import json
import os
import datetime
import re
from ..items import PropertyScraperItem
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Helper functions (unchanged)
def parse_full_price(s):
    if s: numbers = re.findall(r"\d+", s); return int("".join(numbers)) if numbers else None
    return None

def parse_size_sqm(s):
    if s and isinstance(s, str): numbers = re.findall(r"\d+", s); return int(numbers[0]) if numbers else None
    return None

class PlatformBListingsSpider(scrapy.Spider):
    name = "platform_b_listings" # Sanitized name
    # Allowed domain from env or generic placeholder
    allowed_domains = [os.getenv("PLATFORM_B_DOMAIN", "platform-b.com")]

    # Output settings
    custom_settings = {
        'FEEDS': {
            'platform_b_properties.jsonl': {'format': 'jsonlines', 'overwrite': True}
        }
    }

    def __init__(self, *args, **kwargs):
        """Initializes spider with start and end page arguments."""
        super(PlatformBListingsSpider, self).__init__(*args, **kwargs)
        self.start_page = int(kwargs.get('start_page', 1))
        self.end_page = int(kwargs.get('end_page', 9999)) 

    def start_requests(self):
        """Starts the process by going to page 1 to navigate from there."""
        # Sanitized: Load base URL from env
        start_url = os.getenv("PLATFORM_B_SEARCH_URL", "https://www.platform-b.com/sale/houses/bandung")
        
        self.logger.info(f"Spider starting. Will navigate to page {self.start_page} then scrape until page {self.end_page}.")
        yield scrapy.Request(
            start_url,
            meta={'playwright': True, 'current_page': 1},
            callback=self.navigate_to_start
        )

    def navigate_to_start(self, response):
        """Navigates to the self.start_page before scraping begins."""
        current_page = response.meta['current_page']
        if current_page < self.start_page:
            self.logger.info(f"Navigating: on page {current_page}, want to start at {self.start_page}.")
            # Generic selector for pagination
            next_page_url = response.css('a.pagination-next::attr(href)').get()
            if next_page_url:
                yield scrapy.Request(
                    response.urljoin(next_page_url),
                    meta={'playwright': True, 'current_page': current_page + 1},
                    callback=self.navigate_to_start
                )
            else:
                self.logger.warning(f"No 'Next' button on page {current_page}. Starting scrape from here.")
                yield from self.parse(response)
        else:
            self.logger.info(f"Arrived at start page {self.start_page}. Beginning scrape.")
            yield from self.parse(response)

    def parse(self, response):
        """Parses property links and continues to the next page until end_page is reached."""
        
        # Regex to find page number in URL (Generic 'page' or 'p')
        page_match = re.search(r'page=(\d+)', response.url)
        current_page = int(page_match.group(1)) if page_match else 1
        
        self.logger.info(f"Scraping links from search page: {current_page}")
        
        # Extract property links (Generic Selector)
        property_links = response.xpath('//h2/parent::a/@href').getall()
        for link in property_links:
            if "/projects/" in link: continue
            yield scrapy.Request(
                response.urljoin(link), 
                callback=self.parse_property, 
                meta={'playwright': True}
            )
        
        # Check if we should continue to the next page
        if current_page >= self.end_page:
            self.logger.info(f"Reached end_page ({self.end_page}). Stopping pagination.")
            return

        # Find and follow the "Next Page" link
        next_page_url = response.css('a.pagination-next::attr(href)').get()
        if next_page_url:
            self.logger.info(f"Found next page. Following to page {current_page + 1}.")
            yield scrapy.Request(
                response.urljoin(next_page_url), 
                callback=self.parse, 
                meta={'playwright': True}
            )
        else:
            self.logger.info("No more pages to scrape. Finishing.")

    def parse_property(self, response):
        item = PropertyScraperItem()
        all_specs = self.extract_specs(response)
        item['id'] = os.path.basename(os.path.normpath(response.url))
        item['price'] = self.extract_price(response)
        item['address'] = self.extract_address(response)
        item['description'] = self.extract_description(response)
        item['url'] = response.url
        item['scraped_at'] = datetime.datetime.now().isoformat()
        item['bedrooms'] = all_specs.get('Kamar Tidur')
        item['bathrooms'] = all_specs.get('Kamar Mandi')
        item['land_size_sqm'] = parse_size_sqm(all_specs.get('Luas Tanah'))
        item['building_size_sqm'] = parse_size_sqm(all_specs.get('Luas Bangunan'))
        item['specs'] = all_specs
        yield item

    def extract_price(self, response):
        # Generic Price Selector
        price_text = response.css('div.price-tag strong::text').get()
        return parse_full_price(price_text)

    def extract_address(self, response):
        return response.css('address.location-address::text').get()

    def extract_specs(self, response):
        specs = {}
        # Generic Spec Extraction Logic
        for spec_item in response.css('div.listing-overview > div'):
            parts = [part.strip() for part in spec_item.css('::text').getall() if part.strip()]
            if len(parts) == 2: value, key = parts; specs[key] = value
            
        for row in response.css("div.listing-details table tr"):
            keys = row.css('td.table-header p::text').getall()
            values = row.css('td.table-value p::text').getall()
            if len(keys) == len(values):
                for i in range(len(keys)): specs[keys[i].strip()] = values[i].strip()
        return specs
    
    def extract_description(self, response):
        desc_parts = response.css('div.listing-description ::text').getall()
        return "\n".join([part.strip() for part in desc_parts if part.strip()])