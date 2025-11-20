# Bandung House Price Prediction

An end-to-end data science project that scrapes, cleans, and analyzes housing data in Bandung, Indonesia.

## Project Overview
- **Data Collection:** Scraped 9,000+ listings from two major property platforms (anonymized as Platform A and Platform B) using Scrapy and Playwright.
- **Data Cleaning:** AI-powered parsing (GPT-4o) and Google Maps Forward Geocoding to fix missing location data.
- **Analysis:** Geographic heatmaps and price distribution analysis.

## Setup
1. Clone the repo.
2. **Get the Map Data:** Read `data/raw/DOWNLOAD_INSTRUCTIONS.txt` and download the required shapefile (ID3 Region) from the Humanitarian Data Exchange.
3. Install dependencies: `pip install -r requirements.txt`
4. Rename `.env.example` to `.env` and add your API keys.
5. Run the notebooks in order.
