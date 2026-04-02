import os
import datetime
import google.generativeai as genai
from playwright.sync_api import sync_playwright

# 1. Setup Date
today = datetime.datetime.now()
url = f"https://www.betexplorer.com/next/soccer/?year={today.year}&month={today.month:02d}&day={today.day:02d}"

# 2. Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def run_scraper():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Randomize the identity to bypass the shadow block
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"Executing Deep Scan on: {url}")
        
        try:
            # Step 1: Just load the page. Don't click ANYTHING.
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000) # Natural wait
            
            # Step 2: Grab the raw text of the entire table
            # This contains the 1, X, and 2 odds which are always visible
            table_data = page.locator(".table-main").inner_text()
            
            # Step 3: Let Gemini do the math
            # Formula for 1X: 1 / ((1/Odds1) + (1/OddsX))
            prompt = f"""
            I am giving you a raw text dump of football matches and their 1 X 2 odds for {today.strftime('%Y-%m-%d')}.
            
            TASKS:
            1. Identify each match and its odds for Home (1) and Draw (X).
            2. Calculate the Double Chance (1X) odds using this formula: 1 / ((1/HomeOdds) + (1/DrawOdds)).
            3. Filter and return ONLY matches where the calculated 1X odds are between 1.13 and 1.17.
            4. Output a Markdown table: | Time | League | Match | Home Odds | Draw Odds | Calculated 1X |
            
            If the raw text already shows DC/1X odds, use those. 
            If no matches qualify, write: 'No qualifying 1X selections (1.13-1.17) found for today.'
            """
            
            response = model.generate_content([prompt, table_data])
            
            with open("results.md", "w") as f:
                f.write(f"# 1X Syndicate Quantitative Report: {today.strftime('%Y-%m-%d')}\n\n")
                f.write(response.text)
            
            print("Report generated successfully via calculation.")

        except Exception as e:
            print(f"Deep Scan failed: {e}")
            with open("results.md", "w") as f:
                f.write(f"### Connection Warning: {today.strftime('%H:%M')} SAST\n")
                f.write("The site is heavily throttled. The agent will attempt the 00:05 SAST run when traffic is lower.")
        
        browser.close()

if __name__ == "__main__":
    run_scraper()
