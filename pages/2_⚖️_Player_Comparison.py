import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
from data.data_loader import store_session_data

st.set_page_config(page_title="Player Comparison", page_icon="⚖️", layout="wide")

st.title("⚖️ **Player Comparison**")
st.caption("Compare two football stars and see who dominates the field! ⚽🌟")
st.divider()

# Load data if not available
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
        return random_selection()

    player = random.choice(players)
    return league, team, position, player

# Ensure initial player selection
if 'player1' not in st.session_state or 'player2' not in st.session_state:
    while True:
        league1, team1, position1, player1 = random_selection()
        league2, team2, position2, player2 = random_selection()
        if player1 != player2:
            st.session_state.player1 = (league1, team1, position1, player1)
            st.session_state.player2 = (league2, team2, position2, player2)
            break

def player_selection(column, key):
    """Handles league, team, position, and player selection within a column."""
    league, team, position, player = st.session_state[key]

    with column:
        color = ":blue" if key == "player1" else ":red"
        st.subheader(f"{color}[**Player {key[-1]}**]")
        
        selected_league = st.radio(
            "🏆 **Choose a League:**",
            sorted(merged_df['League'].unique()),
            key=f"{key}_league",
            index=list(sorted(merged_df['League'].unique())).index(league)
        )

        teams = sorted(merged_df.loc[merged_df['League'] == selected_league, 'Team'].unique())
        selected_team = st.selectbox(
            "⚔️ **Pick a Team:**",
            teams,
            key=f"{key}_team",
            index=teams.index(team) if team in teams else 0
        )

        df = merged_df.query("League == @selected_league and Team == @selected_team").copy()
        df['Primary Position'] = df['Position'].str.split(',').str[0]

        selected_position = st.selectbox(
            "🔄 **Choose Position:**",
            ['GK', 'DF', 'MF', 'FW'],
            key=f"{key}_position",
            index=['GK', 'DF', 'MF', 'FW'].index(position)
        )

        players = sorted(df.loc[df['Primary Position'] == selected_position, 'Player'].unique())

        if key == "player2" and st.session_state.player1[3] in players:
            players.remove(st.session_state.player1[3])

        selected_player = st.selectbox(
            "⭐ **Select a Player:**",
            players,
            key=f"{key}_player",
            index=players.index(player) if player in players else 0
        )

        st.session_state[key] = (selected_league, selected_team, selected_position, selected_player)

        return df[df['Player'] == selected_player].reset_index(drop=True), selected_player

lc, rc = st.columns(2)
player1_df, player1 = player_selection(lc, "player1")
player2_df, player2 = player_selection(rc, "player2")

st.divider()

def highlight(row):
    """Highlights the better stat in green and the lower one in red."""
    val1, val2 = row.iloc[0], row.iloc[1]

    if pd.isna(val1) or pd.isna(val2):
        return ['color: gray;'] * 2  # Gray for missing values
    
    if val1 > val2:
        return ['color: limegreen; font-weight: bold;', 'color: tomato;']
    elif val2 > val1:
        return ['color: tomato;', 'color: limegreen; font-weight: bold;']
    else:
        return ['color: white; font-weight: bold;'] * 2  # Equal values

def plot_radar_chart(columns):
    """Displays a radar chart for comparing two players."""
    normalize = st.checkbox("📏 Normalize Values", help="Rescales stats for better comparison.", value=True)

    selected_stats = st.multiselect(
        "🎯 **Choose Stats to Compare:**",
        stats_columns,
        default=columns
    ) if st.checkbox("🎛️ **Filter Specific Stats**", help="Choose only the stats you want to compare.", value=False) else columns

    # Get positions of both players
    pos1, pos2 = st.session_state.player1[2], st.session_state.player2[2]
    
    # Filter dataset by player positions
    merged_df['Primary Position'] = merged_df['Position'].str.split(',').str[0]
    pos1_df = merged_df[merged_df['Primary Position'] == pos1]
    pos2_df = merged_df[merged_df['Primary Position'] == pos2]

    stats_p1, stats_p2 = player1_df[selected_stats], player2_df[selected_stats]

    if normalize:
        # Normalize each player's stats based on their position group
        min_vals_p1, max_vals_p1 = pos1_df[selected_stats].min(), pos1_df[selected_stats].max()
        min_vals_p2, max_vals_p2 = pos2_df[selected_stats].min(), pos2_df[selected_stats].max()

        stats_p1 = (stats_p1 - min_vals_p1) / (max_vals_p1 - min_vals_p1)
        stats_p2 = (stats_p2 - min_vals_p2) / (max_vals_p2 - min_vals_p2)
    
    if stats_p1.empty or stats_p2.empty:
        st.warning("⚠️ No data available for selected players in this category!")
        return
    
    merged_df.drop(columns=['Primary Position'], inplace=True)

    fig = go.Figure()
    colors = ['rgba(0, 191, 255, 0.4)', 'rgba(255, 69, 0, 0.4)']

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
        polar=dict(
            bgcolor='#1e2130',
            radialaxis=dict(visible=True, showline=True, linewidth=1, linecolor='white')
        ),
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

    comparison_df = pd.DataFrame({
        player1: player1_df[selected_stats].values.flatten(),
        player2: player2_df[selected_stats].values.flatten()
    }, index=selected_stats)

    with st.expander("📊 **Stat Breakdown Table**", expanded=False):
        st.dataframe(comparison_df.style.apply(highlight, axis=1).format(precision=2))

if 'data' in st.session_state:
    df_columns = {name.replace(" Data", ""): list(df.columns) for name, df in data.items()}
    categories = list(df_columns.keys())

    category_choice = st.selectbox(
        "📂 **Select a Stat Category:**",
        categories,
        index=0,
        help="Pick a category to compare players in."
    )

    selected_columns = df_columns[category_choice][7:] if category_choice in ["Standard", "Goalkeeping"] else df_columns[category_choice]

    plot_radar_chart(selected_columns)

st.divider()
