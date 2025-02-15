import streamlit as st
from data.api import rate_limited_request
from data.data_loader import load_json

st.set_page_config(page_title="Matchday Zone", page_icon="🏟️", layout="wide")

st.title("🏟️ Matchday Zone")
st.caption("Stay updated with live, upcoming, and past matches—all in one place! ⚽📅")
st.divider()

# Load league codes
league_codes = load_json("config/league-codes.json")

# Create tabs for each league
tabs = st.tabs(list(league_codes.keys()))

for i, (league_name, league_code) in enumerate(league_codes.items()):
    with tabs[i]:
        competition_data = rate_limited_request(f"/competitions/{league_code}")

        col1, col2 = st.columns(2)

        with col1:
            current_season = int(competition_data["currentSeason"]["startDate"][:4])
            current_matchday = int(competition_data["currentSeason"]["currentMatchday"])
            selected_season = st.number_input(
                "📅 **Select Season**",
                min_value=current_season - 1,
                max_value=current_season,
                value=current_season,
                step=1,
                format="%d",
                key=f"{league_code}_season",
            )

        if current_season != selected_season:
            competition_data = rate_limited_request(
                f"/competitions/{league_code}?season={selected_season}"
            )
            for season in competition_data["seasons"]:
                if int(season["startDate"][:4]) == selected_season:
                    current_matchday = season["currentMatchday"]

        with col2:
            selected_matchday = st.number_input(
                "🔄 **Select Matchday**",
                min_value=1,
                max_value=current_matchday,
                step=1,
                value=current_matchday,
                key=f"{league_code}_matchday",
            )

        match_data = rate_limited_request(
            f"/competitions/{league_code}/matches?season={selected_season}&matchday={selected_matchday}"
        )

        st.divider()

        if not match_data or "matches" not in match_data:
            st.warning(f"⚠️ No matches available for the {selected_season} season.")

        for match in match_data["matches"]:
            home_team = match["homeTeam"]
            away_team = match["awayTeam"]
            score = match["score"]
            match_status = match["status"]

            # Match result formatting
            home_score = (
                score["fullTime"]["home"]
                if score["fullTime"]["home"] is not None
                else "-"
            )
            away_score = (
                score["fullTime"]["away"]
                if score["fullTime"]["away"] is not None
                else "-"
            )
            match_result = f"{home_score} - {away_score}"

            # Define CSS for centering content
            center_style = "text-align: center;"

            col1, col2, col3 = st.columns([3, 1, 3])

            with col1:
                st.markdown(
                    f'<div style="{center_style}"><img src="{home_team["crest"]}" width="50" style="margin-bottom: 10px;"><br><strong>{home_team["shortName"]}</strong></div>',
                    unsafe_allow_html=True,
                )

            with col2:
                if match_status == "FINISHED":
                    st.markdown(
                        f'<div style="{center_style}"><h3>{match_result}</h3></div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div style="{center_style}"><strong>Status:</strong> {match_status}</div>',
                        unsafe_allow_html=True,
                    )

            with col3:
                st.markdown(
                    f'<div style="{center_style}"><img src="{away_team["crest"]}" width="50" style="margin-bottom: 10px;"><br><strong>{away_team["shortName"]}</strong></div>',
                    unsafe_allow_html=True,
                )

            st.markdown("###")

st.divider()
