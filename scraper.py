import os
import datetime
import google.generativeai as genai
from playwright.sync_api import sync_playwright

# 1. Setup Date
today = datetime.datetime.now()
# We use the direct "soccer" path which is often more stable for scraping
url = f"https://www.betexplorer.com/next/soccer/?year={today.year}&month={today.month:02d}&day={today.day:02d}"

# 2. Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def run_scraper():
    with sync_playwright() as p:
        # Launch browser with a "High-End Mac" identity
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()
        
        print(f"Targeting: {url}")
        
        try:
            # Navigate and wait for the content to actually exist
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # FORCE the Double Chance view by executing a tiny bit of Javascript
            # This is like "teleporting" to the DC view instead of clicking the button
            page.evaluate("() => { const btn = document.querySelector('[data-bet-type=\"dc\"]'); if(btn) btn.click(); }")
            
            # Wait for the odds to refresh
            page.wait_for_timeout(8000) 
            
            # Capture the whole page content
            content = page.content()
            
            # The prompt is now even stricter to ensure accuracy
            prompt = """
            Analyze this betting data. Look specifically at the Double Chance (DC) column.
            Find matches where '1X' odds are between 1.13 and 1.17 inclusive.
            Return ONLY a Markdown table: | Time | League | Match | 1X Odds |
            If none qualify, return: 'No qualifying 1X selections for today.'
            """
            
            response = model.generate_content([prompt, content])
            
            # Save the clean output
            with open("results.md", "w") as f:
                f.write(f"# 1X Syndicate Selections: {today.strftime('%Y-%m-%d')}\n\n")
                f.write(response.text)
            
            print("Successfully updated results.md")

        except Exception as e:
            print(f"Scrape attempt failed: {e}")
            # We save a specific error log so you can see it in GitHub
            with open("results.md", "w") as f:
                f.write(f"### Update Error: {today.strftime('%Y-%m-%d %H:%M')}\n")
                f.write(f"The site is currently resisting the automated click. This is common during high-traffic times. The agent will retry at 00:05 SAST.")
        
        browser.close()

if __name__ == "__main__":
    run_scraper()
