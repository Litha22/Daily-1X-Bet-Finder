import os
import datetime
import google.generativeai as genai
from playwright.sync_api import sync_playwright

# 1. Setup Date
today = datetime.datetime.now()
# Targeting the main soccer page for the specific date
url = f"https://www.betexplorer.com/next/soccer/?year={today.year}&month={today.month:02d}&day={today.day:02d}"

# 2. Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def run_scraper():
    with sync_playwright() as p:
        # Launch with a realistic persona
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        print(f"Observing: {url}")
        
        try:
            # Go to the site and wait for the table to load
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Instead of clicking, we scroll to trigger any "lazy-loaded" data
            page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
            page.wait_for_timeout(3000)
            
            # Grab the "Full Page" content. Gemini can see the DC odds in the code 
            # even if the button hasn't been clicked on the screen!
            content = page.content()
            
            prompt = f"""
            I am providing the raw HTML from a sports betting site for {today.strftime('%Y-%m-%d')}.
            TASKS:
            1. Find the football matches in the list.
            2. For each match, look for the 'Double Chance' or 'DC' odds (specifically 1X).
            3. Filter and return ONLY the matches where the 1X odds are between 1.13 and 1.17 inclusive.
            4. Format as a clean Markdown table: | Time | League | Match | 1X Odds |
            
            If the 1X odds aren't explicitly visible, look for the '1' and 'X' odds and calculate the DC (1X) if possible.
            If no matches qualify, write: 'No qualifying 1X selections (1.13-1.17) found in the current data stream.'
            """
            
            response = model.generate_content([prompt, content])
            
            # Save the result
            with open("results.md", "w") as f:
                f.write(f"# 1X Syndicate Daily Report: {today.strftime('%Y-%m-%d')}\n\n")
                f.write(response.text)
            
            print("Syndicate Agent updated results.md successfully.")

        except Exception as e:
            print(f"Agent failed to read stream: {e}")
            with open("results.md", "w") as f:
                f.write(f"### Connection Warning: {today.strftime('%H:%M')} SAST\n")
                f.write("The stream is currently encrypted or blocked. The agent is recalibrating for the 00:05 SAST run.")
        
        browser.close()

if __name__ == "__main__":
    run_scraper()
