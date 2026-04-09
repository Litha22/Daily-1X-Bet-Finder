import os
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_environment():
    """Ensures the directory structure exists for the YAML to push."""
    folders = ['sot_data/yesterday', 'sot_data/tomorrow']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            print(f"Directory ready: {folder}")

def get_sot_stats(url, category):
    # Setup Headless Chrome for GitHub Actions
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Initialize Driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print(f"Scraping {category} from: {url}")
    try:
        driver.get(url)
        time.sleep(7)  # Increased wait time for RedScores dynamic tables

        match_list = []
        # Target the rows based on your specific HTML snippet
        rows = driver.find_elements(By.CSS_SELECTOR, "tr.openMatch")

        for row in rows:
            try:
                cols = row.find_elements(By.TAG_NAME, "td")
                
                # Column index 7 is the 8th column: "Shots (on goal)"
                sot_value = cols[7].text.strip() if len(cols) > 7 else "N/A"
                home_team = row.find_element(By.CLASS_NAME, "sbHome").text
                away_team = row.find_element(By.CLASS_NAME, "sbAway").text
                
                match_list.append({
                    "Date_Extracted": datetime.now().strftime("%Y-%m-%d"),
                    "Home_Team": home_team,
                    "Away_Team": away_team,
                    "SOT_Stats": sot_value
                })
            except Exception as e:
                continue

        # Save to the standalone folder structure
        if match_list:
            df = pd.DataFrame(match_list)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            file_path = f"sot_data/{category}/sot_{timestamp}.csv"
            df.to_csv(file_path, index=False)
            print(f"Successfully saved {len(match_list)} records to {file_path}")
        else:
            print(f"No match data found for {category}.")

    finally:
        driver.quit()

if __name__ == "__main__":
    # 1. Prepare folders for the Git commit
    setup_environment()
    
    # 2. Define targets
    jobs = [
        ("yesterday", "https://redscores.com/football/yesterday-results"),
        ("tomorrow", "https://redscores.com/football/tomorrow-match-list")
    ]
    
    # 3. Execute
    for category, target_url in jobs:
        get_sot_stats(target_url, category)
