import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Check if a spider name was provided from the command line
if len(sys.argv) < 2:
    print("Error: You must provide a spider name to run.")
    print("Usage: python run.py <spider_name>")
    # Example: python run.py rumah123_listings
    sys.exit(1)

# Get the spider name from the first command-line argument
spider_name = sys.argv[1]

# --- The rest of the logic is the same ---
settings = get_project_settings()
process = CrawlerProcess(settings)

process.crawl(spider_name)

# Use our bypass for the signal handling issue
process.start(install_signal_handlers=False)