import os
import datetime
import random
import google.generativeai as genai
from playwright.sync_api import sync_playwright

today = datetime.datetime.now()
url = f"https://www.betexplorer.com/next/soccer/?year={today.year}&month={today.month:02d}&day={today.day:02d}"

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def run_scraper():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 3000} # Tall viewport for more matches
        )
        page = context.new_page()
        
        try:
            page.goto(url, wait_until="networkidle", timeout=90000)
            page.wait_for_timeout(5000)

            # --- THE SCREENSHOT COMMAND ---
            page.screenshot(path="evidence.png", full_page=True)
            print("Full page screenshot captured as evidence.png")

            page_data = page.evaluate("() => document.body.innerText")
            response = model.generate_content([
                f"Identify 1X odds (1.13-1.17) for {today.strftime('%Y-%m-%d')} from this text.",
                page_data
            ])
            
            with open("results.md", "w") as f:
                f.write(f"# 1X Syndicate Report: {today.strftime('%Y-%m-%d')}\n\n")
                f.write("![Evidence](evidence.png)\n\n") # This embeds the image in your report
                f.write(response.text)

        except Exception as e:
            with open("results.md", "w") as f:
                f.write(f"Security Wall Active at {today.strftime('%H:%M')}. Retrying at 00:05 SAST.")
        
        browser.close()

if __name__ == "__main__":
    run_scraper()
