import pandas as pd
import requests
from pathlib import Path
from dataclasses import dataclass
from types import SimpleNamespace

from util import downloaded


# for from <module> import *
__all__ = [
    'State', 'States', 'states', 'state_lookup',
    'County', 'Counties', 'counties', 'county_lookup',
]

# Initialize to None to avoid NameError
state_codes: pd.DataFrame = None
county_codes: pd.DataFrame = None


@dataclass
class State:
    state: str
    fips: str
    ns_code: str
    name: str
    counties: list = None

    @property
    def ucgid(self) -> str:
        return f"0400000US{self.fips}"


@dataclass
class County:
    state: str
    state_fips: str
    fips: str
    ns_code: str
    name: str
    fips_class_code: str
    fips_functional_status: str
    full_name: str = None
    
    @property
    def ucgid(self) -> str:
        return f"0500000US{self.state_fips}{self.fips}"


States = list[State]
Counties = list[County]

def _get_state_codes():
    """Get the FIPS state codes in a DataFrame."""
    path = "resources/national_state2020.txt"
    url = "https://www2.census.gov/geo/docs/reference/codes2020/national_state2020.txt"
    
    df = pd.read_csv(downloaded(path, url), dtype=str, sep='|')    
    df = df.rename(columns={  # rename columns to snake_case
        # Columns: STATE STATEFP STATENS STATE_NAME
        'STATE': 'state',
        'STATEFP': 'fips',
        'STATENS': 'ns_code',
        'STATE_NAME': 'name',
    })
    return df


def _get_county_codes():
    """Get the FIPS county codes in a DataFrame."""
    path = "resources/national_county2020.txt"
    url = "https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt"
    
    df = pd.read_csv(downloaded(path, url), dtype=str, sep='|')
    df = df.rename(columns={  # rename columns to snake_case
        # Columns: STATE STATEFP COUNTYFP COUNTYNS COUNTYNAME CLASSFP FUNCSTAT
        'STATE': 'state',
        'STATEFP': 'state_fips',
        'COUNTYFP': 'fips',
        'COUNTYNS': 'ns_code',
        'COUNTYNAME': 'name',
        'CLASSFP': 'fips_class_code',
        'FUNCSTAT': 'fips_functional_status',
    })
    return df


# Load state and county codes from Census Bureau into DataFrames
state_codes = _get_state_codes()
county_codes = _get_county_codes()

# Create and store State and County objects from the DataFrames
states = [State(**row) for row in state_codes.to_dict(orient='records')]
counties = [County(**row) for row in county_codes.to_dict(orient='records')]

# Add full_name to each county, and counties to each state
for county in counties:
    for state in states:
        if state.state == county.state:
            county.full_name = f"{county.name}, {state.name}"
            if state.counties is None:
                state.counties = []
            state.counties.append(county)

# Prepare lookup tables for states
state_lookup = SimpleNamespace()
state_lookup.all = states  # list of all states
state_lookup.by = SimpleNamespace()
state_lookup.by.state = {state.state: state for state in states}
state_lookup.by.fips = {state.fips: state for state in states}
state_lookup.by.name = {state.name: state for state in states}

# Prepare lookup tables for counties
county_lookup = SimpleNamespace()
county_lookup.all = counties  # list of all counties
county_lookup.by = SimpleNamespace()
county_lookup.by.state = {
    state.state: state.counties
    for state in states
}
county_lookup.by.fips = {
    state.fips: {
        county.fips: county
        for county in state.counties
    } for state in states
}
county_lookup.by.name = {
    name: [
        county
        for county in counties
        if county.name == name
    ] for name in sorted(set(county.name for county in counties))
}
county_lookup.by.full_name = {
    county.full_name: county
    for county in counties
}
county_lookup.by.state_and_name = {
    state.state: {
        county.name: county
        for county in state.counties
    } for state in states
}
