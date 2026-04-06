import os
import datetime
import google.generativeai as genai
from playwright.sync_api import sync_playwright

# Setup
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')
target_url = "https://www.sports-ai.dev/predictions"

def run_syndicate_downloader():
    with sync_playwright() as p:
        # Launch stealthy to avoid the Cloudflare gate
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        
        print(f"Targeting Predictions Report: {target_url}")
        
        try:
            # 1. Navigate and wait for the "Download" button to appear
            page.goto(target_url, wait_until="networkidle", timeout=90000)
            page.wait_for_selector("text=Download Report", timeout=30000)
            
            # 2. Intercept the Download
            with page.expect_download() as download_info:
                # Some sites require a scroll to 'activate' the button
                page.get_by_text("Download Report").scroll_into_view_if_needed()
                page.get_by_text("Download Report").click()
            
            download = download_info.value
            # Use a fixed filename for the GitHub runner to find easily
            file_path = "./predictions_report.csv"
            download.save_as(file_path)
            print(f"Report secured: {file_path}")

            # 3. AI Quantitative Analysis
            with open(file_path, 'r') as f:
                raw_csv_content = f.read()

            prompt = f"""
            Analyze the following sports prediction data for {datetime.date.today()}.
            
            CRITERIA:
            1. Find matches where the Double Chance (1X) odds are between 1.13 and 1.17.
            2. If '1X' is not a column, calculate it using: 1 / ((1/HomeOdds) + (1/DrawOdds)).
            
            OUTPUT:
            Return a Markdown table: | Time | Match | League | Calculated 1X |
            If no matches qualify, write: 'Syndicate Alert: No qualifying 1.13-1.17 entries found in the latest report.'
            """
            
            response = model.generate_content([prompt, raw_csv_content])
            
            with open("results.md", "w") as f:
                f.write(f"# XCOTT Syndicate AI Analysis: {datetime.date.today()}\n\n")
                f.write(response.text)
            
            print("Syndicate report updated in results.md")

        except Exception as e:
            print(f"Mission Failed: {e}")
            with open("results.md", "w") as f:
                f.write(f"### Error Log: {datetime.datetime.now()} SAST\n")
                f.write(f"The agent couldn't reach the download stream. Details: {e}")
        
        browser.close()

if __name__ == "__main__":
    run_syndicate_downloader()
