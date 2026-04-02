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
        browser = p.chromium.launch(headless=True)
        # Use a very common screen size and browser identity
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"Navigating to: {url}")
        # Wait until the main page structure is actually there
        page.goto(url, wait_until="networkidle")
        
        try:
            # 1. Wait for the main odds table to exist first
            page.wait_for_selector('.table-main', timeout=20000)
            
            # 2. Try to find the DC button using a broader search
            # We look for the text "Double Chance" or the DC attribute
            dc_button = page.locator('li[data-bet-type="dc"]').first
            
            if dc_button.is_visible():
                dc_button.click()
                print("DC Button clicked via attribute.")
            else:
                # Backup: try clicking by text if the attribute is hidden
                page.get_by_text("Double Chance").click()
                print("DC Button clicked via text search.")
            
            # 3. Wait for the numbers to change
            page.wait_for_timeout(6000) 
            
            content = page.content()
            
            prompt = """
            Scan the following HTML data for the Double Chance (DC) market.
            Find every football match where the '1X' odds are between 1.13 and 1.17 inclusive.
            Format the output as a Markdown table: | Time | League | Match | 1X Odds |
            If no matches qualify, write 'No qualifying 1X bets (1.13-1.17) found for today.'
            """
            
            response = model.generate_content([prompt, content])
            
            with open("results.md", "w") as f:
                f.write(f"# 1X Syndicate Selections: {today.strftime('%Y-%m-%d')}\n\n")
                f.write(response.text)
            
            print("Successfully updated results.md")

        except Exception as e:
            # If it fails, capture the page text anyway so Gemini can try to find the error
            print(f"Scrape failed: {e}")
            with open("results.md", "w") as f:
                f.write(f"### Update Error: {today.strftime('%Y-%m-%d %H:%M')}\n")
                f.write(f"The scraper couldn't find the Double Chance button. This usually happens if the site changed its layout or is blocking the bot. Retrying tomorrow automatically.")
        
        browser.close()

if __name__ == "__main__":
    run_scraper()
