import os
import datetime
import google.generativeai as genai
from playwright.sync_api import sync_playwright

# 1. Setup Date and URL
today = datetime.datetime.now()
# We use the current date for the URL
url = f"https://www.betexplorer.com/?year={today.year}&month={today.month:02d}&day={today.day:02d}"

# 2. Configure Gemini
# This looks for the secret key you will add in the next step
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def run_scraper():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"Navigating to: {url}")
        page.goto(url)
        
        try:
            # Look for the DC (Double Chance) button and click it
            page.wait_for_selector('li[data-bet-type="dc"]', timeout=10000)
            page.click('li[data-bet-type="dc"]')
            page.wait_for_timeout(5000) # Give it time to switch the odds
            
            # Extract the page content
            content = page.content()
            
            # The prompt for Gemini to filter your specific range
            prompt = """
            Extract matches from this betting data where the '1X' odds are between 1.13 and 1.17 inclusive.
            Return a Markdown table with: Kick-off Time, League, Match, and 1X Odds.
            If no matches qualify, write 'No qualifying 1X bets for today.'
            Do not include any other text.
            """
            
            response = model.generate_content([prompt, content])
            
            # Save the results to a file
            with open("results.md", "w") as f:
                f.write(f"# 1X Betting Selections for {today.strftime('%Y-%m-%d')}\n\n")
                f.write(response.text)
            
            print("Successfully updated results.md")

        except Exception as e:
            print(f"An error occurred: {e}")
        
        browser.close()

if __name__ == "__main__":
    run_scraper()
