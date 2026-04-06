import os
import datetime
from playwright.sync_api import sync_playwright

def run_delivery_agent():
    with sync_playwright() as p:
        # Launching the browser to find the report
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        
        try:
            print("Navigating to Sports-AI Predictions...")
            page.goto("https://www.sports-ai.dev/predictions", wait_until="networkidle", timeout=90000)
            
            # Triggering the download event
            with page.expect_download() as download_info:
                page.get_by_text("Download Report").click()
            
            download = download_info.value
            # Saving with a static name so your App knows exactly where to look
            file_path = "./latest_predictions.csv"
            download.save_as(file_path)
            
            print(f"Success: File delivered to {file_path}")

        except Exception as e:
            print(f"Delivery failed: {e}")
        
        browser.close()

if __name__ == "__main__":
    run_delivery_agent()
