import requests
from bs4 import BeautifulSoup
import pandas as pd

# Cos .append warnings get tiresome as fuck
import warnings

# These are the sub categories for the different data types
DATA_CATEGORIES = ['shooting', 'passing', 'passing_types', 'gca', 'defense', 'possession', 'misc']
BASE_STATS_URL = 'https://fbref.com/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats'

warnings.filterwarnings("ignore")

def get_stats(url: str):
  response = requests.get(url)

  # Parse the HTML content of the page
  soup = BeautifulSoup(response.text, 'html.parser')

  # Find the table element that contains the headers
  table = soup.find('table')

  # Initialize an empty list to store the combined headers
  combined_headers = []

  # Find all header rows (both levels) within the table
  header_rows = table.find_all('th')

  headers = []

  for header in header_rows:
      # Extract the text of each header cell
      try:
          if 'data-stat' in header.attrs and header['data-stat'] not in headers and "header" not in header['data-stat'] and header['data-stat'] != '' and header['data-stat'] != "matches":
            headers.append(header['data-stat'])
      except:
        pass


  # Now get the data


  rows = table.find_all('tr')

  df = pd.DataFrame(columns= headers)

  count = 1

  for row in rows:
    # This stores the row of stats and info on the player
    data = []
    data.append(count)
    for stat in row.find_all('td'):
      if stat.text != "Matches":
        data.append(stat.text)
    # Creates a new dictionary with the row and the headers used
    new_dict = {col: val for col, val in zip(df.columns, data)}
    if len(data) == len(headers):
      df = df.append(new_dict, ignore_index=True)
    count += 1

  return df

def get_all_this_season_stats():
    overall_df = get_stats(BASE_STATS_URL)
    for stat in DATA_CATEGORIES:
        # changes based on the list of keywords within the URL of the sites
        url = f'https://fbref.com/en/comps/Big5/{stat}/players/Big-5-European-Leagues-Stats'
        new_df = get_stats(url)

        # Gets the columns that are common so they can join correctly
        common_columns = overall_df.columns.intersection(new_df.columns).tolist()
        overall_df = overall_df.merge(new_df, on=common_columns, how='inner')

    return overall_df

def get_all_season_stats(season: str):
  overall_df = get_stats(f'https://fbref.com/en/comps/Big5/{season}/stats/players/{season}-Big-5-European-Leagues-Stats')
  print(overall_df)
  for stat in DATA_CATEGORIES:
    # changes based on the list of keywords within the URL of the sites
    url = f'https://fbref.com/en/comps/Big5/{season}/{stat}/players/{season}-Big-5-European-Leagues-Stats'
    new_df = get_stats(url)

    # Gets the columns that are common so they can join correctly
    common_columns = overall_df.columns.intersection(new_df.columns).tolist()
    overall_df = overall_df.merge(new_df, on=common_columns, how='inner')
    print(overall_df)
    print("CYCLE DONE")

  return overall_df

