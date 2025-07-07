import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_afl_stats(year=2024):
    url = f"https://afltables.com/afl/stats/{year}.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all('table')

    # For demonstration, let's assume we're pulling the 2nd table:
    df = pd.read_html(str(tables[1]))[0]
    df.to_csv(f"afl_{year}_stats.csv", index=False)
    print(f"Saved stats to afl_{year}_stats.csv")

if __name__ == "__main__":
    scrape_afl_stats()
