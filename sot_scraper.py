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
    os.makedirs('sot_data/yesterday', exist_ok=True)
    os.makedirs('sot_data/tomorrow', exist_ok=True)
    os.makedirs('debug', exist_ok=True) # For screenshots if it fails

def get_sot_stats(url, category):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Stealth: Mask as a real Chrome browser on Windows
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    print(f"Opening: {url}")
    try:
        driver.get(url)
        time.sleep(10) # Give it extra time to pass bot checks

        # DEBUG: Save a screenshot to see if the page actually loaded
        driver.save_screenshot(f"debug/{category}_load_check.png")

        match_list = []
        rows = driver.find_elements(By.CSS_SELECTOR, "tr.openMatch")
        
        print(f"Found {len(rows)} potential matches.")

        for row in rows:
            try:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) > 7:
                    sot_value = cols[7].text.strip()
                    home_team = row.find_element(By.CLASS_NAME, "sbHome").text
                    away_team = row.find_element(By.CLASS_NAME, "sbAway").text
                    
                    match_list.append({
                        "Home": home_team, 
                        "Away": away_team, 
                        "SOT": sot_value
                    })
            except: continue

        if match_list:
            df = pd.DataFrame(match_list)
            df.to_csv(f"sot_data/{category}.csv", index=False)
            print(f"SAVED: {category}.csv")
        else:
            print(f"ERROR: No data found in the table for {category}.")

    finally:
        driver.quit()

if __name__ == "__main__":
    setup_environment()
    tasks = [
        ("https://redscores.com/football/yesterday-results", "yesterday"),
        ("https://redscores.com/football/tomorrow-match-list", "tomorrow")
    ]
    for target_url, name in tasks:
        get_sot_stats(target_url, name)
