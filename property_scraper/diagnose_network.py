import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# The URL of the search results page to diagnose
# Sanitized: Loaded from env or uses a placeholder
START_URL = os.getenv("TARGET_PLATFORM_B_SEARCH_URL", "https://www.platform-b.com/search?page=1")

# --- This is the core of the diagnostic tool ---
# This function will be called for every network response the page receives.
async def log_response(response):
    """Logs details of relevant XHR/Fetch responses."""
    try:
        # We only care about data requests (XHR/Fetch) to the Platform's API
        # Sanitized filter: looks for generic 'api' string instead of specific domain
        if response.request.resource_type in ["xhr", "fetch"] and "/api/" in response.url:
            print("="*50)
            print(f"✅ Intercepted an API Request!")
            print(f"URL: {response.url}")
            print(f"Method: {response.request.method}")
            
            # Get the payload (the data sent WITH the request)
            post_data = response.request.post_data
            if post_data:
                print(f"Request Payload:\n{post_data}")
            else:
                print("Request Payload: None")

            # Get the actual JSON response from the server
            json_response = await response.json()
            print(f"Response JSON (first 500 chars):\n{str(json_response)[:500]}...")
            print("="*50 + "\n")

    except Exception as e:
        # This will catch cases where the response is not valid JSON
        print(f"⚠️ Could not process response from {response.url}. It might not be JSON. Error: {e}")
        print("="*50 + "\n")


async def main():
    """Main function to run the browser automation."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # headless=False lets you see the browser
        page = await browser.new_page()

        # Register our logging function to listen to network responses
        page.on("response", log_response)

        print(f"Navigating to {START_URL}...")
        try:
            await page.goto(START_URL, wait_until="networkidle", timeout=60000)
        except Exception as e:
            print(f"Error loading page: {e}")
            return

        print("Page loaded. Waiting a moment before clicking 'Next'...")
        
        await page.wait_for_timeout(3000) # Wait 3 seconds for any initial scripts to finish

        # The selector for the 'Next Page' button
        # Sanitized: Generic class name
        next_button_selector = 'a.pagination-next'
        
        print(f"Attempting to click the 'Next' button using selector: '{next_button_selector}'")
        
        # Check if the button exists before clicking
        if await page.is_visible(next_button_selector):
            await page.click(next_button_selector)
            print("Successfully clicked the 'Next' button.")
            print("Waiting for network responses... The log will appear below.")
            # Wait for a few seconds to ensure all responses are captured
            await page.wait_for_timeout(10000) 
        else:
            print("❌ Could not find the 'Next' button on the page.")

        await browser.close()
        print("\nDiagnostic script finished.")

if __name__ == "__main__":
    # Ensure Playwright browsers are installed
    # In your terminal, run: playwright install
    asyncio.run(main())