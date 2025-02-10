import streamlit as st
import json
import os
import pandas as pd

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


@st.cache_data(show_spinner="Loading data...")
def load_data(url, json_file=None, standard=False):
    """Loads football data from fbref.com and processes it."""
    if not url:
        st.error("⚠️ URL not provided.")
        return None
    
    df = pd.read_html(url)[0]
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
    
    if not standard:
        standard_json = load_json("columns/standard_data.json")
        if standard_json:
            standard_cols = standard_json.get("col_headers", [])
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
    "Goalkeeping Data": ("https://fbref.com/en/comps/Big5/keepers/players/Big-5-European-Leagues-Stats", "columns/goalkeeping_data.json"),
    "Advanced Goalkeeping Data": ("https://fbref.com/en/comps/Big5/keepersadv/players/Big-5-European-Leagues-Stats", "columns/advanced_goalkeeping_data.json"),
}

for name, (url, json_file, *standard) in datasets.items():
    df = load_data(url, json_file, standard=bool(standard))
    if df is not None:
        st.subheader(name)
        st.write(df)
