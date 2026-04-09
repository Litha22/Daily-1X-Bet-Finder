import os
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def setup_folders():
    """Creates storage folders if they don't exist."""
    folders = ['sot_data', 'sot_data/yesterday', 'sot_data/tomorrow']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")

def get_redscores_sot(url, category):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Setup Driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print(f"Accessing {category} matches...")
    driver.get(url)
    time.sleep(6) # Site buffer

    match_data = []
    rows = driver.find_elements(By.CLASS_NAME, "openMatch")

    for row in rows:
        try:
            cols = row.find_elements(By.TAG_NAME, "td")
            # Column 8 (index 7) is 'Shots (on goal)'
            sot = cols[7].text.strip() if len(cols) > 7 else "N/A"
            home = row.find_element(By.CLASS_NAME, "sbHome").text
            away = row.find_element(By.CLASS_NAME, "sbAway").text
            
            match_data.append({
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Home": home,
                "Away": away,
                "SOT_Total": sot
            })
        except Exception:
            continue

    driver.quit()
    
    # Save to standalone folder
    if match_data:
        df = pd.DataFrame(match_data)
        filename = f"sot_data/{category}/stats_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(filename, index=False)
        print(f"Saved {len(match_data)} matches to {filename}")

if __name__ == "__main__":
    setup_folders()
    
    targets = {
        "yesterday": "https://redscores.com/football/yesterday-results",
        "tomorrow": "https://redscores.com/football/tomorrow-match-list"
    }
    
    for cat, url in targets.items():
        get_redscores_sot(url, cat)
