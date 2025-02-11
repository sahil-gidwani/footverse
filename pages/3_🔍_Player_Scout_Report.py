import streamlit as st
import random
import pandas as pd
from data.data_loader import store_session_data

st.set_page_config(page_title="⚽ Player Scout Report", page_icon="🔍", layout="wide")

st.title("🔍 Player Scout Report")
st.caption("Uncover hidden gems and analyze football players with advanced scouting insights! 📊")
st.divider()

# Load data if not available in session state
if 'merged_data' not in st.session_state or 'data' not in st.session_state:
    store_session_data()

merged_df = st.session_state.merged_data
goalkeeping_columns = st.session_state.goalkeeping_columns
outfield_columns = st.session_state.outfield_columns
data = st.session_state.data
stats_columns = merged_df.columns[7:]

# Extract Primary Position
merged_df['Primary Position'] = merged_df['Position'].str.split(',').str[0]

def unique_sorted_list(column, condition=None):
    """Returns a sorted list of unique values for a given column with an optional filtering condition."""
    df = merged_df if condition is None else merged_df[condition]
    return sorted(df[column].dropna().astype(str).unique().tolist())

def random_selection():
    """Selects a random league, team, position, and player for a quick start."""
    league = random.choice(unique_sorted_list('League'))
    teams = unique_sorted_list('Team', condition=(merged_df['League'] == league))
    team = random.choice(teams)
    position = random.choice(['GK', 'DF', 'MF', 'FW'])
    players = unique_sorted_list('Player', condition=(merged_df['League'] == league) & 
                                                    (merged_df['Team'] == team) & 
                                                    (merged_df['Position'].str.contains(position)))
    return (league, team, position, random.choice(players)) if players else random_selection()

if 'selected_league' not in st.session_state:
    st.session_state.selected_league, st.session_state.selected_team, \
    st.session_state.selected_position, st.session_state.selected_player = random_selection()

# Sidebar Filters
with st.sidebar:
    st.header('⚙️ Refine Your Search')
    
    st.session_state.selected_league = st.radio("🌍 Choose a League", unique_sorted_list('League'), 
        index=unique_sorted_list('League').index(st.session_state.selected_league))
    
    teams_in_league = unique_sorted_list('Team', condition=(merged_df['League'] == st.session_state.selected_league))
    st.session_state.selected_team = st.selectbox("🏆 Select a Team", teams_in_league, 
        index=teams_in_league.index(st.session_state.selected_team) if st.session_state.selected_team in teams_in_league else 0)
    
    st.session_state.selected_position = st.selectbox("🎯 Pick a Position", ['GK', 'DF', 'MF', 'FW'],
        index=['GK', 'DF', 'MF', 'FW'].index(st.session_state.selected_position))
    
    players_in_team = unique_sorted_list('Player', condition=(merged_df['League'] == st.session_state.selected_league) &
                                                          (merged_df['Team'] == st.session_state.selected_team) &
                                                          (merged_df['Primary Position'] == st.session_state.selected_position))
    if players_in_team:
        st.session_state.selected_player = st.selectbox("⚽ Select a Player", players_in_team, 
            index=players_in_team.index(st.session_state.selected_player) if st.session_state.selected_player in players_in_team else 0)
    else:
        st.session_state.selected_player = None

@st.cache_data(show_spinner="Analyzing Performance... 📊")
def calculate_percentile_ranks(df, position):
    """Computes percentile ranks for players within their positional group."""
    return df[df['Primary Position'] == position][stats_columns].rank(pct=True) * 100

filtered_df = merged_df[
    (merged_df['League'] == st.session_state.selected_league) &
    (merged_df['Team'] == st.session_state.selected_team) &
    (merged_df['Position'].str.contains(st.session_state.selected_position)) &
    (merged_df['Player'] == st.session_state.selected_player)
]

position_percentiles = calculate_percentile_ranks(merged_df, st.session_state.selected_position)

merged_df.drop(columns=['Primary Position'], errors='ignore', inplace=True)
filtered_df.drop(columns=['Primary Position'], errors='ignore', inplace=True)

filtered_df = filtered_df.merge(position_percentiles, left_index=True, right_index=True, suffixes=("", " Percentile"))

st.subheader(f"📋 **Scouting Report for :blue[{st.session_state.selected_player}]**")
st.write(f"Analyzing **{st.session_state.selected_player}**, a {st.session_state.selected_position} from {st.session_state.selected_team} in the {st.session_state.selected_league}.")

stats_columns = stats_columns.tolist()
if st.session_state.selected_position == 'GK':
    stats_columns = list(pd.Index(stats_columns).intersection(goalkeeping_columns))
else:
    stats_columns = list(pd.Index(stats_columns).intersection(outfield_columns))
percentile_columns = [col + " Percentile" for col in stats_columns]

stats_values = filtered_df[stats_columns].values.flatten().tolist()
percentile_values = filtered_df[percentile_columns].values.flatten().tolist()

scout_report_df = pd.DataFrame({'Statistics': stats_columns, 'Value': stats_values, 'Percentile': percentile_values})
scout_report_df.set_index('Statistics', inplace=True)

with st.expander("📊 __Detailed Scout Report__", expanded=True):
    st.dataframe(
        scout_report_df.style
        .format({'Percentile': lambda x: f"{x:.2f}%"})
        .background_gradient(cmap='RdYlGn', subset=['Percentile'])
        .format(precision=2, subset=['Value'])
    )

if "data" in st.session_state:
    dataset_names = list(st.session_state.data.keys())
    dataset_names = dataset_names if st.session_state.selected_position == "GK" else dataset_names[:-2]
    
    for dataset_name in dataset_names:
        df = st.session_state.data[dataset_name]
        if not df.empty:
            with st.expander(f"📌 {dataset_name.replace(' Data', '')}"):
                valid_columns = [col for col in scout_report_df.index if col in df.columns]
                st.dataframe(
                    scout_report_df.loc[valid_columns].style
                    .format({'Percentile': "{:.2f}%"})
                    .background_gradient(cmap='RdYlGn', subset=['Percentile'])
                    .format(precision=2, subset=['Value'])
                )

st.divider()
