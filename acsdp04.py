import pandas as pd
import requests
from pathlib import Path

from util import download


COUNTY_FILE_PATH = "resources/national_county2020.txt"
COUNTY_FILE_URL = "https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt"
STATE_FILE_PATH = "resources/national_state2020.txt"
STATE_FILE_URL = "https://www2.census.gov/geo/docs/reference/codes2020/national_state2020.txt"


def get_fips_state_codes():
    """Get the FIPS state codes in a `DataFrame`."""
    file_path = STATE_FILE_PATH
    file_url = STATE_FILE_URL
    
    try:
        df = pd.read_csv(file_path, sep='|')
    except FileNotFoundError:
        download(file_url, file_path)
        df = pd.read_csv(file_path, sep='|')
    
    df = df.rename(columns=lambda col: col.strip())
    df = df.rename(columns={  # rename columns to snake_case
        # Columns: STATE STATEFP STATENS STATE_NAME
        'STATE': 'state_abbr',
        'STATEFP': 'state_fips',
        'STATENS': 'state_ns_code',
        'STATE_NAME': 'state_name',
    })
    return df


def get_fips_county_codes():
    """Get the FIPS county codes in a `DataFrame`."""
    file_path = COUNTY_FILE_PATH
    file_url = COUNTY_FILE_URL
    
    try:
        df = pd.read_csv(file_path, sep='|')
    except FileNotFoundError:
        download(file_url, file_path)
        df = pd.read_csv(file_path, sep='|')
    
    df = df.rename(columns=lambda col: col.strip())
    df = df.rename(columns={  # rename columns to snake_case
        # Columns: STATE STATEFP COUNTYFP COUNTYNS COUNTYNAME CLASSFP FUNCSTAT
        'STATE': 'state_abbr',
        'STATEFP': 'state_fips',
        'COUNTYFP': 'county_fips',
        'COUNTYNS': 'county_ns_code',
        'COUNTYNAME': 'county_name',
        'CLASSFP': 'fips_class_code',
        'FUNCSTAT': 'fips_functional_status',
    })
    return df
