# Import required libraries
import logging
import time

import pandas as pd
import plotly.graph_objects as go
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Function to scrape data from a single page
def scrape_page(driver):
    players = []

    # Wait for the table to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "dataContainer"))
    )

    # Find all player rows
    rows = driver.find_elements(By.CSS_SELECTOR, "tr.player")

    for row in rows:
        # Extract player name
        name = row.find_element(By.CSS_SELECTOR, "a.player__name").text

        # Extract position
        position = row.find_element(By.CSS_SELECTOR, "td.player__position").text

        # Extract nationality
        nationality = row.find_element(By.CSS_SELECTOR, "span.player__country").text

        players.append({"Name": name, "Position": position, "Nationality": nationality})

    return players


# Main function to run the scraper
def main():
    driver = webdriver.Chrome()  # Make sure you have chromedriver installed and in PATH
    url = "https://www.premierleague.com/players"
    driver.get(url)

    # Accept cookies if the popup appears
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Accept All Cookies')]")
            )
        )
        cookie_button.click()
    except Exception as e:
        logging.warning("No cookie popup found")

    all_players = []

    # Scroll to load all players
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for the page to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    all_players = scrape_page(driver)

    # Create a DataFrame and save to CSV
    df = pd.DataFrame(all_players)
    # df.to_csv("premier_league_players.csv", index=False)
    print(f"Scraped {len(all_players)} players and saved to premier_league_players.csv")

    driver.quit()

    # Create a bar chart of players per country using Plotly
    country_counts = df["Nationality"].value_counts()

    fig = go.Figure(data=[go.Bar(x=country_counts.index, y=country_counts.values)])

    fig.update_layout(
        title="Number of Premier League Players by Country",
        xaxis_title="Country",
        yaxis_title="Number of Players",
        xaxis_tickangle=-45,
    )

    fig.show()


# Run the main function
if __name__ == "__main__":
    main()
