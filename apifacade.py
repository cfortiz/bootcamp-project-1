import json

import pandas as pd
import requests
from pathlib import Path

from censuscodes import county_lookup, County, state_lookup
from config import census_api_key


# ACS 1-year profile variables
ACS_TOTAL_HOUSING_UNITS = "DP04_0001E"  # HOUSING OCCUPANCY!!Total housing units
ACS_VACANT_HOUSING_UNITS = "DP04_0003E"  # HOUSING OCCUPANCY!!Total housing units!!Vacant units

# 2020 Decennial variables
DEC_TOTAL_UNITS = "H1_001N"  # OCCUPANCY STATUS!!Total:
DEC_VACANT_UNITS = "H1_003N"  # OCCUPANCY STATUS!!Total:!!Vacant

# Create a session to reuse connections, and allow us to inspect the requests
# before they are sent, including generated URLs for GET requests.
session = requests.Session()


def get_vacancy_rate(year: int, county: str|County) -> pd.DataFrame:
    """Get the vacancy rate for a year and county from the Census API."""
    acs_1y_url = f"https://api.census.gov/data/{year}/acs/acs1/profile"
    dec_url = f"https://api.census.gov/data/{year}/dec/pl"

    # Accept a string with the full name of the county, or a County object.
    if isinstance(county, str):
        # Look up the county by its full name.
        county = county_lookup.by.full_name(county)
    
    # Make sure that the county is a County object before proceeding.
    assert isinstance(county, County), "county must be a County object"
    
    # Define the variables and parameters for the request.
    vars = {
        'total_units': ACS_TOTAL_HOUSING_UNITS,
        'vacant_units': ACS_VACANT_HOUSING_UNITS,
    }
    
    # Use the decennial variables for 2020.  The ACS survery had issues in 2020
    # because of the pandemic.  The decennial survey has housing occupancy data
    # for 2020, so we use that instead.
    if year == 2020:
        vars = {
            'total_units': DEC_TOTAL_UNITS,
            'vacant_units': DEC_VACANT_UNITS,
        }
    params = {
        'get': ",".join(vars.values()),
        'for': f"county:{county.fips}",
        'in': f"state:{county.state_fips}",
        'key': census_api_key,
    }

    # Prepare the request and get the URL for inspection.
    if year == 2020:
        endpoint = dec_url
    else:
        endpoint = acs_1y_url
    request = requests.Request('GET', endpoint, params=params).prepare()
    url = request.url

    # Redact the API key for security before printing the URL.
    url = url.replace(census_api_key, "API_KEY_REDACTED")
    
    # Print the URL for inspection.  Also helps keep track of download progress.
    print(f"Year: {year}, County: {county.full_name}, GET: {url}")
    
    # Send the request and get the response.
    response = session.send(request)
    
    # Handle error conditions when making thr request.
    if not response.status_code == 200:
        raise RuntimeError(f"{response.status_code=}, {response.reason=}.  "
                           f"Failed to get data: {response.text}")
    
    # Parse the response as JSON, convert it to a DataFrame.
    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])
    
    # Year isn't part of the data; add it to the DataFrame.
    df['year'] = year
    
    # Cast total and vacant columns to integers.
    for var in vars.values():
        df[var] = df[var].astype(int)
    
    # Rename the columns to more descriptive names.
    renames = {v: k for k, v in vars.items()}
    renames['state'] = 'state_fips'
    renames['county'] = 'county_fips'
    df = df.rename(columns=renames)
    
    # Compute the vacancy rate as a percentage.
    df['vacancy_rate'] = df['vacant_units'] * 100.0 / df['total_units']
    
    # Return the DataFrame with the vacancy rate.
    return df


def get_acs1_profile_variables(years):
    """Get the variables for the ACS 1-year profile for the given years."""
    for year in years:
        path = f'/{year}/acs/acs1/profile/variables.json'
        url = f'{base_url}{path}'
        try:
            response = requests.get(url)
            variables = response.json()['variables']
            for variable, attributes in variables.items():
                label = attributes['label'].lower()
                concept = attributes['concept'].lower()
                print(f'{year=}, {variable=!r}, {label=!r}')
        except Exception as e:
            print(f"Error: {e}")
            print(f"Failed to get variables for year {year}")
            continue


def get_dec_pl_variables(years):
    """Get the variables for the Decennial census for the given years."""
    for year in years:
        path = f'/{year}/dec/pl/variables.json'
        url = f'{base_url}{path}'
        try:
            response = requests.get(url)
            variables = response.json()['variables']
            for variable, attributes in variables.items():
                label = attributes['label'].lower()
                concept = attributes['concept'].lower()
                print(f'{year=}, {variable=!r}, {concept=!r}, {label=!r}')
        except Exception as e:
            print(f"Error: {e}")
            print(f"Failed to get variables for year {year}")
            continue
