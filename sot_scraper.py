import os
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_environment():
    os.makedirs('sot_data', exist_ok=True)

def extract_team_sot(driver, container_selector):
    try:
        # Wait up to 10 seconds for the form table to actually appear
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, container_selector)))
        container = driver.find_element(By.CSS_SELECTOR, container_selector)
        rows = container.find_elements(By.CSS_SELECTOR, "tr.openMatch")
        
        sot_list = []
        for row in rows:
            if len(sot_list) == 6: break
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) > 7:
                val = cols[7].text.strip()
                if val and "-" in val:
                    sot_list.append(val)
        return sot_list if len(sot_list) == 6 else None
    except:
        return None

def process_day(url, filename):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(8) 
        
        matches = driver.find_elements(By.CLASS_NAME, "openMatch")
        links = [m.get_attribute("data-match-url") for m in matches if m.get_attribute("data-match-url")]
        
        results = []
        for link in links[:20]: # Start with a small batch to test stability
            try:
                driver.get(f"https://redscores.com/match/{link}")
                time.sleep(4)
                
                home_sot = extract_team_sot(driver, ".match-history-home")
                away_sot = extract_team_sot(driver, ".match-history-away")
                
                if home_sot and away_sot:
                    results.append({
                        "Home": driver.find_element(By.CLASS_NAME, "sbHome").text,
                        "Away": driver.find_element(By.CLASS_NAME, "sbAway").text,
                        "Home_SOT": "|".join(home_sot),
                        "Away_SOT": "|".join(away_sot)
                    })
            except: continue
            
        if results:
            pd.DataFrame(results).to_csv(f"sot_data/{filename}.csv", index=False)
            print(f"Success: Created {filename}.csv")
    finally:
        driver.quit()

if __name__ == "__main__":
    setup_environment()
    # Testing with 'yesterday' first to verify data exists
    process_day("https://redscores.com/football/yesterday-results", "yesterday")
    process_day("https://redscores.com/football/tomorrow-match-list", "tomorrow")
