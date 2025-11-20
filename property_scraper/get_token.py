# File: get_token.py
import asyncio
import os
from playwright.async_api import async_playwright
# This import will work with the specific version (1.0.6) we just installed.
from playwright_stealth import stealth_async
from dotenv import load_dotenv

load_dotenv()

async def main():
    """
    Launches a stealthy browser to intercept the authorization token
    and prints it to the console.
    """
    # Load targets from environment to hide specific URLs
    target_url = os.getenv("TARGET_PLATFORM_B_URL", "https://www.platform-b.com/listings")
    
    # Generic API pattern (In reality, this matches the specific site's auth endpoint)
    target_api_pattern = "**/api/auth/token" 

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Apply the stealth patches
        await stealth_async(page)

        print(f"Navigating to {target_url} with a stealth browser...")

        try:
            # Listen for the token response while navigating
            async with page.expect_response(target_api_pattern, timeout=30000) as response_info:
                await page.goto(target_url)
            
            token_response = await response_info.value
            token_data = await token_response.json()
            
            # Assuming standard OAuth structure
            access_token = token_data.get('access_token')

            print("\n✅ SUCCESS! Here is your token:\n")
            print(access_token)
            print("\nCopy this token and paste it into your Scrapy spider.")
        
        except Exception as e:
            print(f"\n❌ ERROR: Failed to get token. The site's security may have changed, or a CAPTCHA appeared.")
            print(f"   Details: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())