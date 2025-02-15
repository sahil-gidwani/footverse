import streamlit as st
import json
import os
import time
import random
import pandas as pd
import requests
from io import StringIO


@st.cache_data(show_spinner="Setting up...")
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


def fetch_with_retries(url, max_retries=5, base_delay=2):
    """Fetch data with retries in case of 429 errors and ensure rate limiting."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    if "request_timestamps" not in st.session_state:
        st.session_state.request_timestamps = []

    # Enforce rate limit (max 10 requests per 60 seconds)
    # Refer: https://www.sports-reference.com/bot-traffic.html
    current_time = time.time()
    st.session_state.request_timestamps = [
        t for t in st.session_state.request_timestamps if current_time - t < 60
    ]  # Keep only timestamps in last 60 sec

    if len(st.session_state.request_timestamps) >= 10:
        wait_time = 60 - (current_time - st.session_state.request_timestamps[0])
        st.warning(f"⚠️ Rate limit reached! Waiting {wait_time:.2f} seconds before next request...")
        time.sleep(wait_time)

    # Exponential backoff with jitter for retries
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)

        if response.status_code == 200:  # Successful request
            st.session_state.request_timestamps.append(time.time())  # Log request time
            return pd.read_html(StringIO(response.text))[
                0
            ]  # Convert HTML response to DataFrame

        elif response.status_code == 429:  # Too Many Requests
            wait_time = base_delay * (2**attempt) + random.uniform(
                0, 1
            )  # Exponential backoff with jitter
            st.warning(f"⚠️ Too many requests! Retrying in {wait_time:.2f} seconds... (Attempt {attempt+1}/{max_retries})")
            time.sleep(wait_time)  # Wait before retrying

        else:  # Other errors
            st.error(
                f"⚠️ Failed to fetch data (Error {response.status_code}): {response.reason}"
            )
            return None

    st.error("🚫 Maximum retries reached. Try again later.")
    return None


@st.cache_data(show_spinner="Loading data...", ttl=3600 * 24 * 1)
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

    # col_headers = json_data.get("col_headers", [])
    # if len(df.columns) == len(col_headers):
    #     df.columns = col_headers
    # else:
    #     st.error(f"⚠️ Column count mismatch for {json_file}. Using default headers.")
    #     return None

    # Join the multi-level column headers
    df.columns = [" ".join(col).strip() for col in df.columns]
    df.reset_index(drop=True, inplace=True)

    # Rename columns with only the last part of the multi-level header
    df.columns = [col.split()[-1] if "level_0" in col else col for col in df.columns]

    # Rename columns using the mapping data
    mapping_data = load_json("columns/column_mapping.json")
    df.rename(columns=mapping_data, inplace=True, errors="ignore")

    col_remove = json_data.get("col_remove", [])

    # Remove unwanted columns
    df = df[df["Player"] != "Player"]
    df.drop(columns=["Rank", "Matches"], inplace=True, errors="ignore")
    df.dropna(axis=1, how="all", inplace=True)
    df.drop(columns=col_remove, inplace=True, errors="ignore")

    if not standard and not goalkeeping:
        standard_json = load_json("columns/standard_data.json")
        if standard_json:
            standard_cols = [
                col
                for col in standard_json.get("col_headers", [])
                if col not in standard_json.get("col_remove", [])
            ]
            df.drop(
                columns=[col for col in df.columns if col in standard_cols],
                inplace=True,
                errors="ignore",
            )

    if not standard and goalkeeping:
        goalkeeping_json = load_json("columns/goalkeeping_data.json")
        if goalkeeping_json:
            goalkeeping_cols = [
                col
                for col in goalkeeping_json.get("col_headers", [])
                if col not in goalkeeping_json.get("col_remove", [])
            ]
            df.drop(
                columns=[col for col in df.columns if col in goalkeeping_cols],
                inplace=True,
                errors="ignore",
            )

    return df


def merge_data(*dfs, how="outer", on=None):
    """
    Merges multiple DataFrames into a single DataFrame.
    """
    if not dfs:
        st.error("⚠️ No DataFrames provided to merge.")

    merged_df = dfs[0]
    for df in dfs[1:]:
        if on:
            merged_df = pd.merge(merged_df, df, how=how, suffixes=("", "_dup"), on=on)
        else:
            merged_df = pd.merge(
                merged_df,
                df,
                how=how,
                suffixes=("", "_dup"),
                left_index=True,
                right_index=True,
            )

        # Remove duplicate columns generated by the merge
        for col in merged_df.columns:
            if col.endswith("_dup"):
                original_col = col.replace("_dup", "")
                merged_df[original_col] = merged_df[original_col].combine_first(
                    merged_df[col]
                )
                merged_df.drop(columns=[col], inplace=True)

    # Ensure 'Age' is a string
    merged_df["Age"] = merged_df["Age"].astype(str)
    # Format 'Age' while preserving its structure
    merged_df["Age"] = merged_df["Age"].str[:2] + "." + merged_df["Age"].str[3:6]

    # * Convert all columns to numeric (except first 5 columns)
    merged_df.iloc[:, 5:] = merged_df.iloc[:, 5:].apply(pd.to_numeric, errors="coerce")
    merged_df = merged_df.convert_dtypes()

    # * Rename the 'League' column to standard names
    league_mapping = {
        "eng Premier League": "Premier League",
        "fr Ligue 1": "Ligue 1",
        "de Bundesliga": "Bundesliga",
        "it Serie A": "Serie A",
        "es La Liga": "La Liga",
    }
    merged_df["League"] = merged_df["League"].replace(league_mapping)

    return merged_df


def store_session_data():
    # ! The playing time data consists of both outfield and goalkeeping data, so it is not included in the list of datasets.
    datasets = {
        "Standard Data": (
            "https://fbref.com/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats",
            "columns/standard_data.json",
            True,
        ),
        "Shooting Data": (
            "https://fbref.com/en/comps/Big5/shooting/players/Big-5-European-Leagues-Stats",
            "columns/shooting_data.json",
        ),
        "Passing Data": (
            "https://fbref.com/en/comps/Big5/passing/players/Big-5-European-Leagues-Stats",
            "columns/passing_data.json",
        ),
        "Pass Types Data": (
            "https://fbref.com/en/comps/Big5/passing_types/players/Big-5-European-Leagues-Stats",
            "columns/pass_types_data.json",
        ),
        "Goal and Shot Creation Data": (
            "https://fbref.com/en/comps/Big5/gca/players/Big-5-European-Leagues-Stats",
            "columns/goal_shot_creation_data.json",
        ),
        "Defensive Actions Data": (
            "https://fbref.com/en/comps/Big5/defense/players/Big-5-European-Leagues-Stats",
            "columns/defensive_actions_data.json",
        ),
        "Possession Data": (
            "https://fbref.com/en/comps/Big5/possession/players/Big-5-European-Leagues-Stats",
            "columns/possession_data.json",
        ),
        # "Playing Time Data": ("https://fbref.com/en/comps/Big5/playingtime/players/Big-5-European-Leagues-Stats", "columns/playing_time_data.json"),
        "Miscellaneous Data": (
            "https://fbref.com/en/comps/Big5/misc/players/Big-5-European-Leagues-Stats",
            "columns/misc_data.json",
        ),
        "Goalkeeping Data": (
            "https://fbref.com/en/comps/Big5/keepers/players/Big-5-European-Leagues-Stats",
            "columns/goalkeeping_data.json",
            True,
            True,
        ),
        "Advanced Goalkeeping Data": (
            "https://fbref.com/en/comps/Big5/keepersadv/players/Big-5-European-Leagues-Stats",
            "columns/advanced_goalkeeping_data.json",
            False,
            True,
        ),
    }

    outfield_categories = [
        key
        for key in datasets.keys()
        if key not in ["Goalkeeping Data", "Advanced Goalkeeping Data"]
    ]
    goalkeeping_categories = [
        "Standard Data",
        "Goalkeeping Data",
        "Advanced Goalkeeping Data",
    ]

    if (
        "outfield_categories" not in st.session_state
        or "goalkeeping_categories" not in st.session_state
    ):
        st.session_state.outfield_categories = outfield_categories
        st.session_state.goalkeeping_categories = goalkeeping_categories

    outfield_df_list = []
    goalkeeping_df_list = []

    if "data" not in st.session_state:
        st.session_state.data = {}

    for name, values in datasets.items():
        url, json_file, *flags = values
        standard = bool(flags[0]) if len(flags) > 0 else False
        goalkeeping = bool(flags[1]) if len(flags) > 1 else False

        df = load_data(url, json_file, standard=standard, goalkeeping=goalkeeping)
        if df is not None:
            st.session_state.data[name] = df
            if goalkeeping:
                goalkeeping_df_list.append(df)
            else:
                outfield_df_list.append(df)

    # * Alternatively, load data from backup file
    # load_backup()
    # # Create separate lists for outfield and goalkeeping data
    # if "data" in st.session_state:
    #     for key, value in st.session_state.data.items():
    #         if "Goalkeeping" in key:
    #             goalkeeping_df_list.append(value)
    #         else:
    #             outfield_df_list.append(value)

    outfield_data = (
        merge_data(*outfield_df_list) if outfield_df_list else pd.DataFrame()
    )
    goalkeeping_data = (
        merge_data(*goalkeeping_df_list) if goalkeeping_df_list else pd.DataFrame()
    )

    outfield_columns = outfield_data.columns if not outfield_data.empty else []
    goalkeeping_columns = goalkeeping_data.columns if not goalkeeping_data.empty else []

    if "outfield_columns" not in st.session_state:
        st.session_state.outfield_columns = outfield_columns
    if "goalkeeping_columns" not in st.session_state:
        st.session_state.goalkeeping_columns = goalkeeping_columns

    if not outfield_data.empty and not goalkeeping_data.empty:
        merged_data = merge_data(outfield_data, goalkeeping_data, on=["Player", "Team"])
        if "merged_data" not in st.session_state:
            st.session_state.merged_data = merged_data
    else:
        st.warning("⚠️ Data not loaded successfully. Try again later.")


# Define backup file path
BACKUP_FILE = "data/backup/data.json"

# Ensure backup directory exists
os.makedirs(os.path.dirname(BACKUP_FILE), exist_ok=True)


def store_backup():
    """Save `st.session_state.data` to a JSON backup file."""
    if "data" in st.session_state:
        # Convert DataFrames to JSON serializable format
        serializable_data = {
            key: df.to_dict(orient="records")
            for key, df in st.session_state.data.items()
        }

        # Save as JSON
        with open(BACKUP_FILE, "w") as f:
            json.dump(serializable_data, f)

        st.success(f"📦 Data backed up successfully to '{BACKUP_FILE}'.")
    else:
        st.warning("⚠️ No data to backup!")


def load_backup():
    """Load session data from JSON backup file and restore `st.session_state.data`."""

    if os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE, "r") as f:
            data = json.load(f)

        if not data:
            st.warning(f"⚠️ No data found in backup file '{BACKUP_FILE}'.")
            return

        # Convert JSON back to DataFrames
        st.session_state.data = {
            key: pd.DataFrame(value) for key, value in data.items()
        }
        st.success(f"📦 Data restored successfully from '{BACKUP_FILE}'.")
    else:
        st.warning(f"⚠️ Backup file '{BACKUP_FILE}' not found.")
