import streamlit as st
import json
import os
import time
import random
import pandas as pd
import requests
from io import StringIO

st.set_page_config(page_title="Footverse", page_icon="⚽", layout="wide")

st.title(":red[Footverse]")
st.caption("Unlock the Power of Football Analytics – Dive into the Numbers Behind the Game! ⚽📊")
st.markdown("---")

@st.cache_data(show_spinner="Loading data...")
def load_json(file_path):
    """Safely loads a JSON file and handles errors."""
    if not os.path.exists(file_path):
        st.error(f"⚠️ JSON file '{file_path}' not found!")
        return None
    if os.path.getsize(file_path) == 0:
        st.error(f"⚠️ JSON file '{file_path}' is empty!")
        return None
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        st.error(f"⚠️ Error parsing JSON file '{file_path}'.")
        return None


request_timestamps = []

def fetch_with_retries(url, max_retries=5, base_delay=2):
    """Fetch data with retries in case of 429 errors and ensure rate limiting."""
    global request_timestamps
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Enforce rate limit (max 10 requests per 60 seconds)
    # Refer: https://www.sports-reference.com/bot-traffic.html
    current_time = time.time()
    request_timestamps = [t for t in request_timestamps if current_time - t < 60]  # Keep only timestamps in last 60 sec

    if len(request_timestamps) >= 10:
        wait_time = 60 - (current_time - request_timestamps[0])
        st.warning(f"⚠️ Rate limit reached! Waiting {wait_time:.2f} seconds before next request...")
        time.sleep(wait_time)

    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)

        if response.status_code == 200:  # Successful request
            request_timestamps.append(time.time())  # Log request time
            return pd.read_html(StringIO(response.text))[0]  # Convert HTML response to DataFrame

        elif response.status_code == 429:  # Too Many Requests
            wait_time = base_delay * (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
            st.warning(f"⚠️ Too many requests! Retrying in {wait_time:.2f} seconds... (Attempt {attempt+1}/{max_retries})")
            time.sleep(wait_time)  # Wait before retrying

        else:  # Other errors
            st.error(f"⚠️ Failed to fetch data (Error {response.status_code}): {response.reason}")
            return None

    st.error("🚫 Maximum retries reached. Try again later.")
    return None


@st.cache_data(show_spinner="Loading data...")
def load_data(url, json_file=None, standard=False, goalkeeping=False):
    """Loads football data from fbref.com and processes it."""
    if not url:
        st.error("⚠️ URL not provided.")
        return None
    
    df = fetch_with_retries(url)
    if df is None:
        return None
    
    json_data = load_json(json_file) if json_file else None
    if json_data is None:
        return None
    
    col_headers = json_data.get("col_headers", [])
    col_remove = json_data.get("col_remove", [])
    
    if len(df.columns) == len(col_headers):
        df.columns = col_headers
    else:
        st.error(f"⚠️ Column count mismatch for {json_file}. Using default headers.")
        return None
    
    df = df[df["Player"] != "Player"]
    df.drop(columns=["Rk", "Matches"], inplace=True, errors="ignore")
    df.drop(columns=col_remove, inplace=True, errors="ignore")
    
    if not standard and not goalkeeping:
        standard_json = load_json("columns/standard_data.json")
        if standard_json:
            standard_cols = [col for col in standard_json.get("col_headers", []) if col not in standard_json.get("col_remove", [])]
            df.drop(columns=[col for col in df.columns if col in standard_cols], inplace=True, errors="ignore")
    
    df.reset_index(drop=True, inplace=True)
    return df


datasets = {
    "Standard Data": ("https://fbref.com/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats", "columns/standard_data.json", True),
    "Shooting Data": ("https://fbref.com/en/comps/Big5/shooting/players/Big-5-European-Leagues-Stats", "columns/shooting_data.json"),
    "Passing Data": ("https://fbref.com/en/comps/Big5/passing/players/Big-5-European-Leagues-Stats", "columns/passing_data.json"),
    "Pass Types Data": ("https://fbref.com/en/comps/Big5/passing_types/players/Big-5-European-Leagues-Stats", "columns/pass_types_data.json"),
    "Goal and Shot Creation Data": ("https://fbref.com/en/comps/Big5/gca/players/Big-5-European-Leagues-Stats", "columns/goal_shot_creation_data.json"),
    "Defensive Actions Data": ("https://fbref.com/en/comps/Big5/defense/players/Big-5-European-Leagues-Stats", "columns/defensive_actions_data.json"),
    "Possession Data": ("https://fbref.com/en/comps/Big5/possession/players/Big-5-European-Leagues-Stats", "columns/possession_data.json"),
    "Playing Time Data": ("https://fbref.com/en/comps/Big5/playingtime/players/Big-5-European-Leagues-Stats", "columns/playing_time_data.json"),
    "Miscellaneous Data": ("https://fbref.com/en/comps/Big5/misc/players/Big-5-European-Leagues-Stats", "columns/misc_data.json"),
    "Goalkeeping Data": ("https://fbref.com/en/comps/Big5/keepers/players/Big-5-European-Leagues-Stats", "columns/goalkeeping_data.json", False, True),
    "Advanced Goalkeeping Data": ("https://fbref.com/en/comps/Big5/keepersadv/players/Big-5-European-Leagues-Stats", "columns/advanced_goalkeeping_data.json", False, True),
}

for name, values in datasets.items():
    url, json_file, *flags = values
    standard = bool(flags[0]) if len(flags) > 0 else False
    goalkeeping = bool(flags[1]) if len(flags) > 1 else False
    
    df = load_data(url, json_file, standard=standard, goalkeeping=goalkeeping)
    if df is not None:
        st.subheader(name)
        st.write(df)
