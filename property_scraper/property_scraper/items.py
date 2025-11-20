# property_scraper/items.py
import scrapy

class PropertyScraperItem(scrapy.Item):
    # Define the fields for your item here
    id = scrapy.Field()
    url = scrapy.Field()
    scraped_at = scrapy.Field()
    
    # Main Fields
    price = scrapy.Field()
    address = scrapy.Field()
    address_locality = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    description = scrapy.Field()
    
    # --- NEW DEDICATED SPEC FIELDS ---
    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()
    land_size_sqm = scrapy.Field()
    building_size_sqm = scrapy.Field()
    # ------------------------------------
    
    # The full dictionary of all other specs
    specs = scrapy.Field()