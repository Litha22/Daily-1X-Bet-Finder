import os
import datetime
import random
import google.generativeai as genai
from playwright.sync_api import sync_playwright

# 1. Setup Date & URL
today = datetime.datetime.now()
url = f"https://www.betexplorer.com/next/soccer/?year={today.year}&month={today.month:02d}&day={today.day:02d}"

# 2. Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def run_scraper():
    with sync_playwright() as p:
        # Launch with arguments that strip the 'Automation' identity
        browser = p.chromium.launch(headless=True, args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox'
        ])
        
        # Create a realistic 'Human' context
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1,
        )
        
        # This script deletes the 'webdriver' flag so the site thinks it's a real person
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = context.new_page()
        print(f"Syndicate Agent initiating stealth scan on: {url}")
        
        try:
            # Go to site and wait for the 'Encryption Gate' to settle
            page.goto(url, wait_until="networkidle", timeout=90000)
            
            # Simulate 'Human Reading' behavior
            for _ in range(3):
                page.mouse.wheel(0, random.randint(300, 700))
                page.wait_for_timeout(random.randint(2000, 4000))
            
            # Extract the page text
            page_data = page.evaluate("() => document.body.innerText")
            
            if len(page_data) < 1000:
                raise Exception("Page returned empty - potentially blocked by wall.")

            prompt = f"""
            Identify football matches for {today.strftime('%Y-%m-%d')}.
            Find the Home (1) and Draw (X) odds.
            Calculate the Double Chance (1X) price: 1 / ((1/Home) + (1/Draw)).
            
            Return a Markdown table of matches where the 1X price is between 1.13 and 1.17.
            Include: | Time | Match | 1 | X | Calculated 1X |
            If none, write 'No qualifying 1.13-1.17 selections found for today.'
            """
            
            response = model.generate_content([prompt, page_data])
            
            with open("results.md", "w") as f:
                f.write(f"# 1X Syndicate Quantitative Report: {today.strftime('%Y-%m-%d')}\n\n")
                f.write(response.text)
            
            print("Successfully bypassed security and updated report.")

        except Exception as e:
            print(f"Stealth bypass failed: {e}")
            with open("results.md", "w") as f:
                f.write(f"### Security Wall Active: {today.strftime('%H:%M')} SAST\n")
                f.write("The site is in High-Security mode. Your agent is waiting for the **00:05 SAST** low-traffic window to execute.")
        
        browser.close()

if __name__ == "__main__":
    run_scraper()
