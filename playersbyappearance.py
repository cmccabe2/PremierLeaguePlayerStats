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

    while True:
        # Wait for the table to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "statsTableContainer"))
        )

        # Find all player rows
        rows = driver.find_elements(By.CLASS_NAME, "table__row")

        for row in rows:
            # Extract player name
            name = row.find_element(By.CLASS_NAME, "playerName").text

            # Extract club
            club = row.find_element(
                By.CLASS_NAME, "stats-table__cell-icon-align"
            ).text.strip()

            # Extract nationality
            try:
                nationality = row.find_element(
                    By.CSS_SELECTOR,
                    ".stats-table__cell-icon-align img.stats-table__flag-icon",
                ).get_attribute("title")
            except Exception:
                nationality = "Unknown"

            # Extract appearances
            appearances = int(
                row.find_element(By.CLASS_NAME, "stats-table__main-stat").text
            )

            players.append(
                {
                    "Name": name,
                    "Club": club,
                    "Nationality": nationality,
                    "Appearances": appearances,
                }
            )

        # Check if there's a next page
        try:
            next_button = driver.find_element(By.CLASS_NAME, "paginationNextContainer")
            if "inactive" not in next_button.get_attribute("class"):
                next_button.click()
                time.sleep(2)  # Wait for the page to load
            else:
                break
        except Exception as e:
            # No more pages, exit the loop
            logging.warning(f"No next page found: {e}")
            break

    return players


# Main function to run the scraper
def main():
    driver = webdriver.Chrome()  # Make sure you have chromedriver installed and in PATH
    url = "https://www.premierleague.com/stats/top/players/appearances"
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

    all_players = scrape_page(driver)

    # Create a DataFrame with all players
    df_all = pd.DataFrame(all_players)
    logging.info(f"Scraped {len(all_players)} players")

    logging.info(f"{len(df_all)} players have made at least one appearance")

    driver.quit()

    # Calculate percentage of English players per team
    df_all["Is_English"] = df_all["Nationality"] == "England"
    team_stats = (
        df_all.groupby("Club")
        .agg({"Is_English": "mean", "Name": "count"})
        .reset_index()
    )
    team_stats = team_stats.rename(
        columns={"Is_English": "Percent_English", "Name": "Total_Players"}
    )
    team_stats["Percent_English"] *= 100  # Convert to percentage

    # Sort teams by percentage of English players
    team_stats = team_stats.sort_values("Percent_English", ascending=False)

    # Create a bar chart using Plotly
    fig = go.Figure(
        data=[
            go.Bar(
                x=team_stats["Club"],
                y=team_stats["Percent_English"],
                text=team_stats["Percent_English"].round(1).astype(str) + "%",
                textposition="auto",
                hovertemplate="%{x}<br>English Players: %{text}<br>Total Players: %{customdata}",
                customdata=team_stats["Total_Players"],
                marker_color="royalblue",  # Add a color to make bars visible
            )
        ]
    )

    fig.update_layout(
        title="Percentage of English Players by Premier League Team",
        xaxis_title="Team",
        yaxis_title="Percentage of English Players",
        xaxis_tickangle=-45,
        yaxis_range=[0, 100],
        plot_bgcolor="white",  # Set plot background to white
        paper_bgcolor="white",  # Set paper background to white
        margin=dict(t=100, l=50, r=50, b=100),  # Adjust margins
    )

    # Add a border around the chart area
    fig.update_xaxes(showline=True, linewidth=1, linecolor="black", mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black", mirror=True)

    fig.show()

    logging.info("Chart of teams by percentage of English players created.")


# Run the main function
if __name__ == "__main__":
    main()
