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

# Function to convert form to points
def form_to_points(form):
    if not form:
        return []
    form_list = form.split(",")
    return [3 if result == "W" else 1 if result == "D" else 0 for result in form_list]

# Create tabs for each league
tabs = st.tabs(list(league_codes.keys()))

for i, (league_name, league_code) in enumerate(league_codes.items()):
    with tabs[i]:  
        competition_data = rate_limited_request(f"/competitions/{league_code}")
        
        if not competition_data:
            st.warning(f"⚠️ Unable to fetch data for {league_name}.")
            continue
        
        competition_logo = competition_data["emblem"]

        # Display competition details
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            img_bg_style = "background-color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px;" if st_theme in ["dark", "light"] else ""
            st.markdown(f"""
                <div>
                    <img src="{competition_logo}" width="150" style="{img_bg_style}">
                </div>
            """, unsafe_allow_html=True)
        
        if league_code == "CL":
            standings_data = rate_limited_request(f"/competitions/{league_code}/standings")
            
            current_season = standings_data["season"]
            current_season = f"{season['startDate'][:4]}"
            current_matchday = season["currentMatchday"]
        else:
            col1, col2 = st.columns(2)
            with col1:
                current_season = int(competition_data["currentSeason"]["startDate"][:4])
                selected_season = st.number_input(
                    "📅 **Select Season**",
                    min_value=current_season - 1,
                    max_value=current_season,
                    value=current_season,
                    step=1,
                    format="%d",
                    key=f"{league_code}_season"
                )

            standings_data = rate_limited_request(f"/competitions/{league_code}/standings?season={selected_season}")

            if not standings_data:
                st.warning(f"⚠️ No standings available for the {selected_season} season.")
                continue

            with col2:
                season = standings_data["season"]
                current_matchday = season["currentMatchday"]

                selected_matchday = st.number_input(
                    "🔄 **Select Matchday**",
                    min_value=1,
                    max_value=current_matchday,
                    step=1,
                    value=current_matchday,
                    key=f"{league_code}_matchday"
                )
            
            if selected_matchday != current_matchday:
                standings_data = rate_limited_request(f"/competitions/{league_code}/standings?season={selected_season}&matchday={selected_matchday}")
        
        st.markdown(f"**Season:** {current_season} | **Matchday:** {current_matchday}")

        # Extract team standings
        teams = standings_data["standings"][0]["table"]

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
                "Goal Difference": team["goalDifference"],
                "Form": team["form"],
            }
            for team in teams
        ])

        # Drop duplicate positions and set index
        df = df.drop_duplicates(subset=["Position"])
        df.set_index("Position", inplace=True)
        
        df['Form'] = df['Form'].apply(form_to_points)
        
        # Column configuration for the DataFrame
        column_config = {
            "Crest": st.column_config.ImageColumn("Logo"),
            "Team": st.column_config.TextColumn("Team"),
            "Played": st.column_config.NumberColumn("Played"),
            "Won": st.column_config.NumberColumn("Won"),
            "Drawn": st.column_config.NumberColumn("Drawn"),
            "Lost": st.column_config.NumberColumn("Lost"),
            "Points": st.column_config.NumberColumn("Points"),
            "Goals For": st.column_config.NumberColumn("Goals For"),
            "Goals Against": st.column_config.NumberColumn("Goals Against"),
            "Goal Difference": st.column_config.NumberColumn("Goal Difference"),
            "Form": st.column_config.LineChartColumn("Form", y_min=0, y_max=3, help="Form in the last 5 matches"),
        }

        # Apply colors to the DataFrame
        styled_df = df.style.apply(lambda row: highlight_rows(row, league_code), axis=1)

        st.dataframe(styled_df, column_config=column_config)

st.divider()
