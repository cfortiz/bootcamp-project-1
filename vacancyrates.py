import json

import pandas as pd
import requests
from pathlib import Path

from censuscodes import *
from config import census_api_key

# Directory for project resources
resources_dir = "resources"

# All counties for the project
project_counties = list(map(county_lookup.by.full_name.get, [
    # Counties for NYC boroughs
    "Bronx County, New York",
    "Kings County, New York",  # Brooklyn
    "New York County, New York",  # Manhattan
    "Queens County, New York",
    "Richmond County, New York",  # Staten Island
    
    # Counties adjacent to NYC boroughs
    "Westchester County, New York",
    "Rockland County, New York",
    "Nassau County, New York",
    "Bergen County, New Jersey",
    "Essex County, New Jersey",
    "Hudson County, New Jersey",
    "Middlesex County, New Jersey",
    "Union County, New Jersey",
    "Fairfield County, Connecticut",
]))

# Range of years for the project
project_year_ranges = list(range(2012, 2023))  # 2012-2022: `range` is half-open


session = requests.Session()


def get_1y_dp04(year: int, county: County):
    acs_1y_url = f"https://api.census.gov/data/{year}/acs/acs1/profile"

    group = "DP04"
    
    # assert county in project_counties, f"County not in project: {county.full_name}"
    
    params = {
        'get': f"group({group})",
        'for': f"county:{county.fips:03d}",
        'in': f"state:{county.state_fips:02d}",
        'key': census_api_key,
    }

    request = requests.Request('GET', acs_1y_url, params=params).prepare()
    url = request.url.replace(census_api_key, "API_KEY_REDACTED")
    # print(f"GET: {url}")
    response = session.send(request)
    
    if not response.ok:
        raise RuntimeError(f"Failed to get data: {response.text}")
    # data = json.loads(response.text)
    # print(f"RESPONSE: {response.status_code=}, {response.reason=}")
    # print(f"TEXT: {response.text}")
    data = response.json()
    return data


def get_1y_vacancy_rates(year: int, county: County):
    acs_1y_url = f"https://api.census.gov/data/{year}/acs/acs1/profile"

    homeowner_vacancy_rate_variable = "DP04_0004E"
    rental_vacancy_rate_variable = "DP04_0005E"

    variables = [homeowner_vacancy_rate_variable, rental_vacancy_rate_variable]
    
    # assert county in project_counties, f"County not in project: {county.full_name}"
    
    params = {
        'get': ",".join(variables),
        'for': f"county:{county.fips:03d}",
        'in': f"state:{county.state_fips:02d}",
        'key': census_api_key,
    }

    request = requests.Request('GET', acs_1y_url, params=params).prepare()
    url = request.url.replace(census_api_key, "API_KEY_REDACTED")
    print(f"GET: {url}")
    response = session.send(request)
    
    if not response.ok:
        raise RuntimeError(f"Failed to get data: {response.text}")
    # data = json.loads(response.text)
    # print(f"RESPONSE: {response.status_code=}, {response.reason=}")
    # print("START TEXT")
    # print(response.text)
    # print("END TEXT")
    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])
    return df


if __name__ == '__main__':
    dfs = []
    # print("START API CALLS")
    for year in project_year_ranges:
        for county in project_counties:
            # print(f"START API CALL: {year=}, {county.full_name=}")
            df = get_1y_vacancy_rates(year, county)
            # print("START DATA FRAME HEAD")
            # print(df.head())
            # print("END DATA FRAME HEAD")
            # print(f"END API CALL: {year=}, {county.full_name=}")
            dfs.append(df)
    # print("END API CALLS")
    merged_df = pd.concat(dfs).reset_index(drop=True)
    merged_df.to_csv("merged_df.csv")
    # print("START MERGED DATA FRAME")
    for index, row in merged_df.iterrows():
        print(row)
    # print("END MERGED DATA FRAME")