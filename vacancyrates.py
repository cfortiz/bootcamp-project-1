import json

import pandas as pd
import requests
from pathlib import Path

from censuscodes import county_lookup, County
from config import census_api_key

from typing import Iterable


# Directory for project resources
output_dir = "resources"

# ACS 1-year profile variables
HOMEOWNER_VACANCY_RATE = "DP04_0004E"
RENTAL_VACANCY_RATE = "DP04_0005E"

# Create a session to reuse connections, and allow us to inspect the requests
# before they are sent, including generated URLs for GET requests.
session = requests.Session()


def get_acs_1y_vacancy_rates(year: int, county: str|County) -> pd.DataFrame:
    """Get the vacancy rates for a year and county from the ACS 1 yr profile."""
    acs_1y_url = f"https://api.census.gov/data/{year}/acs/acs1/profile"

    # Accept a string with the full name of the county, or a County object.
    if isinstance(county, str):
        # Look up the county by its full name.
        county = county_lookup.by.full_name(county)
    
    # Make sure that the county is a County object before proceeding.
    assert isinstance(county, County), "county must be a County object"
    
    # Define the variables and parameters for the request.
    variables = [
        HOMEOWNER_VACANCY_RATE,
        RENTAL_VACANCY_RATE,
    ]
    params = {
        'get': ",".join(variables),
        'for': f"county:{county.fips}",
        'in': f"state:{county.state_fips}",
        'key': census_api_key,
    }

    # Prepare the request and get the URL for inspection.
    request = requests.Request('GET', acs_1y_url, params=params).prepare()
    url = request.url
    url = url.replace(census_api_key, "API_KEY_REDACTED")  # Redact the API key
    
    # Print the URL for inspection.  Also helps keep track of download progress.
    print(f"GET: {url}")
    
    # Send the request and get the response.
    response = session.send(request)
    
    # Handle error conditions when making thr request.
    if not response.ok:
        raise RuntimeError(f"Failed to get data: {response.text}")
    
    # Parse the response as JSON, convert it to a DataFrame, and return it.
    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])
    return df
