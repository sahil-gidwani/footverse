import streamlit as st
import pandas as pd
from streamlit_javascript import st_javascript
from data.api import rate_limited_request
from data.data_loader import load_json

st.set_page_config(page_title="League Table", page_icon="📈", layout="wide")

st.title("📈 League Table")
st.caption("Who's leading? Who's falling? Get the latest league table updates! ⚽🔝")
st.divider()

# Fetch current theme
st_theme = st_javascript(
	"""window.getComputedStyle(window.parent.document.getElementsByClassName("stApp")[0]).getPropertyValue("color-scheme")"""
)

# Define colors for light and dark modes
colors_light = {
    "top4": "#D4EFDF",  # Light Green (Champions League)
    "europa": "#F9E79F",  # Light Yellow (Europa League)
    "conference": "#AED6F1",  # Light Blue (Conference League)
    "relegation": "#F5B7B1",  # Light Red (Relegation)
}

colors_dark = {
    "top4": "#145A32",  # Dark Green (Champions League)
    "europa": "#7D6608",  # Dark Yellow (Europa League)
    "conference": "#1A5276",  # Dark Blue (Conference League)
    "relegation": "#78281F",  # Dark Red (Relegation)
}

# Choose colors based on theme
colors = colors_dark if st_theme == "dark" else colors_light

# Load league codes and highlight positions
league_codes = load_json("config/league-codes.json")
highlight_positions = load_json("config/highlight-positions.json")

# Function to apply colors dynamically based on league configuration
def highlight_rows(row, league_code):
    league_rules = highlight_positions.get(league_code, {})  # Get league-specific rules
    
    if row.name in league_rules.get("top", []):  # Top positions (Champions League)
        return [f'background-color: {colors["top4"]}'] * len(row)
    elif row.name in league_rules.get("europa", []):  # Europa League spots
        return [f'background-color: {colors["europa"]}'] * len(row)
    elif row.name in league_rules.get("conference", []):  # Conference League spots
        return [f'background-color: {colors["conference"]}'] * len(row)
    elif row.name in league_rules.get("relegation", []):  # Relegation zone
        return [f'background-color: {colors["relegation"]}'] * len(row)
    
    return [''] * len(row)

# Create tabs for each league
tabs = st.tabs(list(league_codes.keys()))

for i, (league_name, league_code) in enumerate(league_codes.items()):
    with tabs[i]:  # Create a separate tab for each league
        standings_data = rate_limited_request(f"/competitions/{league_code}/standings")

        if standings_data:
            # Extract season details
            competition = standings_data["competition"]
            season = standings_data["season"]

            current_season = f"{season['startDate'][:4]} - {season['endDate'][:4]}"
            current_matchday = season["currentMatchday"]
            competition_logo = competition["emblem"]

            # Display competition details
            # st.markdown(f"## 🏆 {competition['name']} Standings")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                img_bg_style = "background-color: white; padding: 10px; border-radius: 10px;" if st_theme in ["dark", "light"] else ""
                st.markdown(f"""
                    <div>
                        <img src="{competition_logo}" width="150" style="{img_bg_style}">
                    </div>
                """, unsafe_allow_html=True)
            st.markdown(f"**Season:** {current_season} | **Matchday:** {current_matchday}")

            # Extract team standings
            teams = standings_data["standings"][0]["table"]

            # Convert data into a DataFrame
            df = pd.DataFrame([
                {
                    "Position": team["position"],
                    "Crest": team["team"]["crest"],
                    "Team": team["team"]["name"],
                    "Played": team["playedGames"],
                    "Won": team["won"],
                    "Drawn": team["draw"],
                    "Lost": team["lost"],
                    "Points": team["points"],
                    "Goals For": team["goalsFor"],
                    "Goals Against": team["goalsAgainst"],
                    "Goal Difference": team["goalDifference"]
                }
                for team in teams
            ])

            df = df.drop_duplicates(subset=["Position"]) # Drop duplicate positions
            df.set_index("Position", inplace=True)  # Set position as index

            # Column configuration for Streamlit
            column_config = {
                "Crest": st.column_config.ImageColumn("Logo", help="Club Crest"),
                "Team": st.column_config.TextColumn("Team"),
                "Played": st.column_config.NumberColumn("Played"),
                "Won": st.column_config.NumberColumn("Won"),
                "Drawn": st.column_config.NumberColumn("Drawn"),
                "Lost": st.column_config.NumberColumn("Lost"),
                "Points": st.column_config.NumberColumn("Points"),
                "Goals For": st.column_config.NumberColumn("Goals For"),
                "Goals Against": st.column_config.NumberColumn("Goals Against"),
                "Goal Difference": st.column_config.NumberColumn("Goal Difference"),
            }

            # Apply styling
            styled_df = df.style.apply(lambda row: highlight_rows(row, league_code), axis=1)

            # Display the table
            st.dataframe(styled_df, column_config=column_config)
        else:
            st.warning(f"⚠️ Unable to fetch data for {league_name}.")
