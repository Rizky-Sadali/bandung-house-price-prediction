from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

if __name__ == "__main__":
    # Get the project settings from settings.py
    settings = get_project_settings()

    # Create a CrawlerProcess
    process = CrawlerProcess(settings)

    # Tell the process which spider to crawl
    # Sanitized: 'platform_a_listings' refers to the main target spider
    process.crawl("platform_a_listings")

    # Start the process but tell it NOT to install the broken signal handlers
    process.start(install_signal_handlers=False)