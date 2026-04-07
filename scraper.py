import os
import datetime
from playwright.sync_api import sync_playwright

def run_delivery_agent():
    # Get today's date for the filename
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    # Create an archive directory if it doesn't exist
    if not os.path.exists('archive'):
        os.makedirs('archive')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        
        try:
            print("Fetching report...")
            page.goto("https://www.sports-ai.dev/predictions", wait_until="networkidle")
            
            with page.expect_download() as download_info:
                page.get_by_text("Download Report").click()
            
            download = download_info.value
            
            # SAVE 1: The 'Latest' version for the App to use immediately
            download.save_as("./latest_predictions.csv")
            
            # SAVE 2: The 'Dated' version for your historical records
            download.save_as(f"./archive/{today_str}.csv")
            
            print(f"Success: Delivered latest and archived as {today_str}.csv")

        except Exception as e:
            print(f"Delivery failed: {e}")
        
        browser.close()

if __name__ == "__main__":
    run_delivery_agent()
