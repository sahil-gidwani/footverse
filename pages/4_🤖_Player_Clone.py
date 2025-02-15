import streamlit as st
import random
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances
from data.data_loader import store_session_data

st.set_page_config(page_title="Player Clone", page_icon="🤖", layout="wide")

st.title("🤖 **Player Clone**")
st.caption("Discover players who match your favorite star's playstyle! ⚡💫")
st.divider()

# Load data if not available
if "merged_data" not in st.session_state or "data" not in st.session_state:
    store_session_data()

merged_df = st.session_state.merged_data
data = st.session_state.data
stats_columns = merged_df.columns[7:]
outfield_categories = st.session_state.outfield_categories
goalkeeping_categories = st.session_state.goalkeeping_categories
outfield_columns = st.session_state.outfield_columns
goalkeeping_columns = st.session_state.goalkeeping_columns

# Extract Primary Position
merged_df["Primary Position"] = merged_df["Position"].str.split(",").str[0]


def unique_sorted_list(column, condition=None):
    df = merged_df if condition is None else merged_df[condition]
    return sorted(df[column].dropna().astype(str).unique().tolist())


def random_selection():
    league = random.choice(unique_sorted_list("League"))
    teams = unique_sorted_list("Team", condition=(merged_df["League"] == league))
    team = random.choice(teams)
    position = random.choice(["GK", "DF", "MF", "FW"])
    players = unique_sorted_list(
        "Player",
        condition=(merged_df["League"] == league)
        & (merged_df["Team"] == team)
        & (merged_df["Primary Position"] == position),
    )
    return (
        (league, team, position, random.choice(players))
        if players
        else random_selection()
    )


if "selected_league" not in st.session_state:
    (
        st.session_state.selected_league,
        st.session_state.selected_team,
        st.session_state.selected_position,
        st.session_state.selected_player,
    ) = random_selection()

# Sidebar Filters
with st.sidebar:
    st.header("⚙️ Refine Your Search")
    st.session_state.selected_league = st.radio(
        "🌍 Choose a League",
        unique_sorted_list("League"),
        index=unique_sorted_list("League").index(st.session_state.selected_league),
    )

    teams_in_league = unique_sorted_list(
        "Team", condition=(merged_df["League"] == st.session_state.selected_league)
    )
    st.session_state.selected_team = st.selectbox(
        "🏆 Select a Team",
        teams_in_league,
        index=(
            teams_in_league.index(st.session_state.selected_team)
            if st.session_state.selected_team in teams_in_league
            else 0
        ),
    )

    st.session_state.selected_position = st.selectbox(
        "🎯 Pick a Position",
        ["GK", "DF", "MF", "FW"],
        index=["GK", "DF", "MF", "FW"].index(st.session_state.selected_position),
    )

    players_in_team = unique_sorted_list(
        "Player",
        condition=(merged_df["League"] == st.session_state.selected_league)
        & (merged_df["Team"] == st.session_state.selected_team)
        & (merged_df["Primary Position"] == st.session_state.selected_position),
    )
    if players_in_team:
        st.session_state.selected_player = st.selectbox(
            "⚽ Select a Player",
            players_in_team,
            index=(
                players_in_team.index(st.session_state.selected_player)
                if st.session_state.selected_player in players_in_team
                else 0
            ),
        )
    else:
        st.session_state.selected_player = None

# Player selection
selected_player = st.session_state.selected_player
if not selected_player:
    st.warning("⚠️ No players found for the selected filters!")

# Find selected player's data
player_data = merged_df[merged_df["Player"] == selected_player]
if player_data.empty:
    st.warning("⚠️ Player not found in dataset!")

# Determine position category (GK vs Outfield)
position = player_data.iloc[0]["Position"]
player_type = "GK" if "GK" in position else "Outfield"

stats_columns = stats_columns.tolist()
if player_type == "GK":
    stats_columns = list(pd.Index(stats_columns).intersection(goalkeeping_columns))
else:
    stats_columns = list(pd.Index(stats_columns).intersection(outfield_columns))

# Determine stat categories based on player position
# * Drop Standard category for GK
categories = goalkeeping_categories[1:] if player_type == "GK" else outfield_categories
categories = [category.replace(" Data", "") for category in categories]

# Extract column names for each category
df_columns = {
    name.replace(" Data", ""): list(pd.Index(df.columns).intersection(stats_columns))
    for name, df in data.items()
}

# Stat category selection
category_choice = st.selectbox(
    "📂 **Select a Stat Category:**",
    categories,
    index=0,
    help="Pick a stat category for comparison.",
)
selected_stats = (
    df_columns[category_choice][4:]
    if category_choice in ["Standard", "Goalkeeping"]
    else df_columns[category_choice]
)

# Allow narrowing stats
narrow_stats = st.checkbox(
    "🎛️ **Narrow down specific stats**", help="Select only certain stats for comparison."
)
if narrow_stats:
    selected_stats = st.multiselect(
        "📊 **Choose Stats to Compare:**", stats_columns, default=selected_stats
    )

# Allow weight adjustment
adjust_weights = st.checkbox(
    "⚖️ **Adjust stat weights**",
    help="Assign more or less importance to specific stats.",
)

# Collect weight inputs
stat_weights = {}
if adjust_weights:
    st.markdown("🔢 **Assign weight to each stat (higher value = more importance)**")
    cols = st.columns(3)  # Create three columns for better layout

    for index, stat in enumerate(selected_stats):
        with cols[index % 3]:  # Distribute inputs across three columns
            stat_weights[stat] = st.number_input(
                f"⚖️ **{stat}**", min_value=0.1, max_value=10.0, value=1.0, step=0.1
            )

# Filter dataset by position type
if player_type == "GK":
    compare_df = merged_df[merged_df["Position"].str.contains("GK")].copy()
else:
    compare_df = merged_df[~merged_df["Position"].str.contains("GK")].copy()

# Ensure selected stats exist in data
selected_stats = [stat for stat in selected_stats if stat in compare_df.columns]
if not selected_stats:
    st.warning("⚠️ No valid stats selected for comparison!")

st.divider()

# Reset indexes for comparison
compare_df.reset_index(drop=True, inplace=True)

# Extract relevant stats and normalize
scaler = StandardScaler()
stats_matrix = compare_df[selected_stats].copy()

# Handle missing values before normalizing
stats_matrix = stats_matrix.fillna(method="ffill").fillna(method="bfill")

# Normalize data
stats_matrix = scaler.fit_transform(stats_matrix)

# Apply weights if enabled
if adjust_weights:
    weight_array = np.array([stat_weights[stat] for stat in selected_stats])
    # Scale stats based on user-defined weights
    stats_matrix = stats_matrix * weight_array

# Find Euclidean Distance
player_index = compare_df[compare_df["Player"] == selected_player].index[0]

# Compute similarity
similarity_scores = 1 / (
    1 + euclidean_distances([stats_matrix[player_index]], stats_matrix)[0]
)

# Store similarity scores in DataFrame
compare_df["Similarity Score"] = similarity_scores
compare_df = compare_df.sort_values(by="Similarity Score", ascending=False).reset_index(
    drop=True
)

# Remove the selected player from results and filter out zero similarity scores
compare_df = compare_df[
    (compare_df["Player"] != selected_player) & (compare_df["Similarity Score"] > 0)
]

# Display results
if compare_df.empty:
    st.warning(
        "⚠️ No similar players found based on the selected stats. Try choosing different criteria!"
    )
else:
    st.subheader(
        f"🧩 **Similar Players to :blue[{st.session_state.selected_player}] ({len(compare_df)})**"
    )

    styled_df = compare_df.copy()
    styled_df = styled_df.set_index("Player")  # Set Player as index

    # Ensure index uniqueness
    styled_df = styled_df.loc[~styled_df.index.duplicated(keep="first")]

    # Convert Similarity Score to percentage
    styled_df["Similarity Score"] = styled_df["Similarity Score"] * 100

    # Display with styling
    st.dataframe(
        styled_df[
            ["Team", "League", "Position", "Similarity Score"]
        ].style.background_gradient(cmap="RdYlGn", subset=["Similarity Score"])
        # Convert to percentage with 2 decimal places
        .format({"Similarity Score": "{:.2f}%"})
    )

st.divider()
