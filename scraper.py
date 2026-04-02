import os
import datetime
import google.generativeai as genai
from playwright.sync_api import sync_playwright

# 1. Setup Date and URL
today = datetime.datetime.now()
url = f"https://www.betexplorer.com/?year={today.year}&month={today.month:02d}&day={today.day:02d}"

# 2. Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def run_scraper():
    with sync_playwright() as p:
        # Launch browser with a "Real Person" identity (User Agent)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"Navigating to: {url}")
        page.goto(url, wait_until="domcontentloaded")
        
        try:
            # Look for the DC (Double Chance) button
            # We add a small wait to make it look human
            page.wait_for_selector('li[data-bet-type="dc"]', timeout=15000)
            page.click('li[data-bet-type="dc"]')
            print("Clicked Double Chance button.")
            
            # Wait for the table to refresh with new odds
            page.wait_for_timeout(5000) 
            
            content = page.content()
            
            prompt = """
            Look at this betting data. Focus ONLY on the 'DC' (Double Chance) market.
            Identify matches where the '1X' odds are between 1.13 and 1.17 inclusive.
            Return a Markdown table with: Kick-off, League, Match, and 1X Odds.
            If none qualify, say 'No 1X bets found in the 1.13-1.17 range today.'
            """
            
            response = model.generate_content([prompt, content])
            
            with open("results.md", "w") as f:
                f.write(f"# 1X Strategy Selections: {today.strftime('%Y-%m-%d')}\n\n")
                f.write(response.text)
            
            print("Done! Check results.md")

        except Exception as e:
            print(f"Error details: {e}")
            # If it fails, save the error so we can see why
            with open("results.md", "w") as f:
                f.write(f"Error during scrape: {e}")
        
        browser.close()

if __name__ == "__main__":
    run_scraper()
