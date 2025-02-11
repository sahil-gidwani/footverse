import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
from data.data_loader import store_session_data

st.set_page_config(page_title="Player Comparison", page_icon="⚖️", layout="wide")

st.title("⚖️ Player Comparison")
st.caption("Compare Football Players Side-by-Side! 🔄")
st.markdown("---")

# Load data if not available in session state
if 'merged_data' not in st.session_state or 'data' not in st.session_state:
    store_session_data()

merged_df = st.session_state.merged_data
data = st.session_state.data
stats_columns = merged_df.columns[7:]

def random_selection():
    """Randomly selects a league, team, position, and player."""
    league = random.choice(sorted(merged_df['League'].unique()))
    team = random.choice(sorted(merged_df.loc[merged_df['League'] == league, 'Team'].unique()))

    df = merged_df.query("League == @league and Team == @team").copy()
    df['Primary Position'] = df['Position'].str.split(',').str[0]

    position = random.choice(['GK', 'DF', 'MF', 'FW'])
    players = sorted(df.loc[df['Primary Position'] == position, 'Player'].unique())

    if not players:
        return random_selection()  # Recursively select again if no players found

    player = random.choice(players)
    return league, team, position, player

# Ensure player1 and player2 are different
while True:
    league1, team1, position1, player1 = random_selection()
    league2, team2, position2, player2 = random_selection()
    
    if player1 != player2:
        break  # Ensure different players are selected

def player_selection(column, key, league, team, position, player):
    """Handles league, team, position, and player selection within a column."""
    with column:
        selected_league = st.radio("Select League:", sorted(merged_df['League'].unique()), key=f"{key}_league", index=list(sorted(merged_df['League'].unique())).index(league))
        selected_team = st.selectbox("Select Team:", sorted(merged_df.loc[merged_df['League'] == selected_league, 'Team'].unique()), key=f"{key}_team", index=list(sorted(merged_df.loc[merged_df['League'] == selected_league, 'Team'].unique())).index(team))

        df = merged_df.query("League == @selected_league and Team == @selected_team").copy()
        df['Primary Position'] = df['Position'].str.split(',').str[0]

        selected_position = st.selectbox("Select Position:", ['GK', 'DF', 'MF', 'FW'], key=f"{key}_position", index=['GK', 'DF', 'MF', 'FW'].index(position))
        players = sorted(df.loc[df['Primary Position'] == selected_position, 'Player'].unique())

        if key == "player2" and player1 in players:
            players.remove(player1)

        selected_player = st.selectbox("Select Player:", players, key=f"{key}_player", index=players.index(player) if player in players else 0)
        return df[df['Player'] == selected_player].reset_index(drop=True), selected_player

lc, rc = st.columns(2)
player1_df, player1 = player_selection(lc, "player1", league1, team1, position1, player1)
player2_df, player2 = player_selection(rc, "player2", league2, team2, position2, player2)

st.markdown("---")

def highlight(row):
    """Highlights the greater value in green, the lesser in red, and keeps equal values neutral."""
    val1, val2 = row.iloc[0], row.iloc[1]

    if pd.isna(val1) or pd.isna(val2):
        return ['color: gray;'] * 2  # Gray for missing values
    
    if val1 > val2:
        return ['color: lawngreen; font-weight: bold;', 'color: red;']
    elif val2 > val1:
        return ['color: red;', 'color: lawngreen; font-weight: bold;']
    else:  # Equal values
        return ['color: white; font-weight: bold;'] * 2  # Neutral styling for equal values

def plot_radar_chart(columns):
    """Plots a radar chart comparing two players based on selected stats."""
    
    # Allow users to filter specific stats
    selected_stats = st.multiselect("Choose stats:", stats_columns, default=columns) if st.checkbox("Select Specific Stats") else columns

    # Extract selected stats only
    stats_p1, stats_p2 = player1_df[selected_stats], player2_df[selected_stats]

    # Handle missing data
    if stats_p1.empty or stats_p2.empty:
        st.warning("Selected players do not have data for this category.")
        return

    # Radar chart with contrasting colors
    fig = go.Figure()
    colors = ['rgba(0, 191, 255, 0.4)', 'rgba(255, 69, 0, 0.4)']  # Semi-transparent colors

    for player, stats, color in zip([player1, player2], [stats_p1, stats_p2], colors):
        fig.add_trace(go.Scatterpolar(
            r=stats.values.flatten(), 
            theta=selected_stats, 
            fill='toself', 
            name=player,
            fillcolor=color,
            line=dict(color=color.replace("0.4", "1"), width=2)
        ))

    fig.update_layout(
        polar=dict(bgcolor='#1e2130', radialaxis=dict(visible=True, showline=True, linewidth=1, linecolor='white')),
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

    # Ensure comparison_df only has two columns before renaming
    comparison_df = pd.DataFrame({player1: stats_p1.values.flatten(), player2: stats_p2.values.flatten()}, index=selected_stats)

    with st.expander("Comparison Table", expanded=False):
        st.dataframe(comparison_df.style.apply(highlight, axis=1).format(precision=2))

if 'data' in st.session_state:
    df_columns = {name.replace(" Data", ""): list(df.columns) for name, df in data.items()}
    categories = list(df_columns.keys())

    category_choice = st.selectbox("Select a Category", categories, index=0, help="Select a category to compare players.")
    selected_columns = df_columns[category_choice][7:] if category_choice in ["Standard", "Goalkeeping"] else df_columns[category_choice]

    plot_radar_chart(selected_columns)
