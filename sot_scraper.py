import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_environment():
    os.makedirs('sot_data', exist_ok=True)

def extract_team_sot(driver, team_container_selector):
    """
    Scans a team's recent form. 
    Checks up to 12 matches to find at least 6 with valid SOT.
    """
    try:
        # Targeting the specific team's recent matches table
        container = driver.find_element(By.CSS_SELECTOR, team_container_selector)
        rows = container.find_elements(By.CSS_SELECTOR, "tr.openMatch")
        
        sot_list = []
        games_checked = 0
        
        for row in rows:
            # STOP once we have 6 or if we've exhausted the 12-game limit
            if len(sot_list) == 6 or games_checked >= 12:
                break
            
            games_checked += 1
            cols = row.find_elements(By.TAG_NAME, "td")
            
            # Index 7 is the "Shots (on goal)" column
            if len(cols) > 7:
                val = cols[7].text.strip()
                # Ensure the cell isn't empty and contains the score/stat format
                if val and "-" in val:
                    sot_list.append(val)
        
        # Return only if we successfully found exactly 6 valid games
        return sot_list if len(sot_list) == 6 else None
    except Exception:
        return None

def process_day(url, filename):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(6)

    final_data = []
    
    # Locate all match rows on the main list
    matches = driver.find_elements(By.CLASS_NAME, "openMatch")
    match_links = [m.get_attribute("data-match-url") for m in matches if m.get_attribute("data-match-url")]

    print(f"Total potential matches found: {len(match_links)}")

    for link in match_links:
        try:
            driver.get(f"https://redscores.com/match/{link}")
            time.sleep(4)

            home_name = driver.find_element(By.CLASS_NAME, "sbHome").text
            away_name = driver.find_element(By.CLASS_NAME, "sbAway").text

            # Extracting from Home Form Table and Away Form Table (Bypassing H2H)
            home_sot = extract_team_sot(driver, ".match-history-home") 
            away_sot = extract_team_sot(driver, ".match-history-away")

            # Validate both teams have the required 6-game history
            if home_sot and away_sot:
                final_data.append({
                    "Home_Team": home_name,
                    "Away_Team": away_name,
                    "Home_Last_6_SOT": "|".join(home_sot),
                    "Away_Last_6_SOT": "|".join(away_sot)
                })
                print(f"VALID: {home_name} vs {away_name}")
            else:
                print(f"OMITTED: {home_name} vs {away_name} (Failed 6/12 check)")

        except Exception:
            continue

    driver.quit()

    if final_data:
        pd.DataFrame(final_data).to_csv(f"sot_data/{filename}.csv", index=False)
        print(f"Successfully updated {filename}.csv with {len(final_data)} matches.")

if __name__ == "__main__":
    setup_environment()
    
    # Target URLs mapping to your 3 specific files
    tasks = [
        ("https://redscores.com/football/yesterday-results", "yesterday"),
        ("https://redscores.com/", "today"),
        ("https://redscores.com/football/tomorrow-match-list", "tomorrow")
    ]

    for target_url, file_name in tasks:
        print(f"--- Running {file_name.upper()} Scrape ---")
        process_day(target_url, file_name)
