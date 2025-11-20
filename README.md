# Bandung House Price Prediction

An end-to-end data science project that scrapes, cleans, and analyzes housing data in Bandung, Indonesia.

## Project Overview
- **Data Collection:** Scraped 9,000+ listings from two major property platforms (anonymized as Platform A and Platform B) using Scrapy and Playwright.
- **Data Cleaning:** AI-powered parsing (GPT-4o) and Google Maps Forward Geocoding to fix missing location data.
- **Analysis:** Geographic heatmaps and price distribution analysis.

## Setup
1. Clone the repo.
2. **Unzip the Map Data:** Go to `data/raw` and unzip `indonesia_shapefiles.zip` (these files were compressed to fit on GitHub).
3. Install dependencies: `pip install -r requirements.txt`
4. Rename `.env.example` to `.env` and add your API keys.
5. Run the notebooks in order.
