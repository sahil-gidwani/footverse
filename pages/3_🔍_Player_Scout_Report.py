import streamlit as st
import random
from data.data_loader import store_session_data

st.set_page_config(page_title="Player Scout Report", page_icon="🔍", layout="wide")

st.title("🔍 Player Scout Report")
st.caption("Scout Football Players with Advanced Analytics! 📈")
st.markdown("---")

# Load data if not available in session state
if 'merged_data' not in st.session_state or 'data' not in st.session_state:
    store_session_data()

merged_df = st.session_state.merged_data
data = st.session_state.data
stats_columns = merged_df.columns[7:]

# Helper function to get unique sorted values
def unique_sorted_list(column, condition=None):
    """Returns a sorted list of unique values for the given column, with an optional filtering condition."""
    df = merged_df if condition is None else merged_df[condition]
    return sorted(df[column].dropna().astype(str).unique().tolist())

def random_selection():
    """Selects a random league, team, position, and player."""
    league = random.choice(unique_sorted_list('League'))
    teams = unique_sorted_list('Team', condition=(merged_df['League'] == league))
    team = random.choice(teams)

    positions = ['GK', 'DF', 'MF', 'FW']
    position = random.choice(positions)

    players = unique_sorted_list('Player', condition=(merged_df['League'] == league) & 
                                                    (merged_df['Team'] == team) & 
                                                    (merged_df['Position'].str.contains(position)))
    if not players:
        return random_selection()  # Retry if no valid players found
    player = random.choice(players)

    return league, team, position, player

# Initialize session state on first render
if 'selected_league' not in st.session_state:
    st.session_state.selected_league, st.session_state.selected_team, \
    st.session_state.selected_position, st.session_state.selected_player = random_selection()

# Sidebar Filters
with st.sidebar:
    st.write('__Filters__')

    st.session_state.selected_league = st.radio("Select League", unique_sorted_list('League'), 
                                                index=unique_sorted_list('League').index(st.session_state.selected_league))

    teams_in_league = unique_sorted_list('Team', condition=(merged_df['League'] == st.session_state.selected_league))
    st.session_state.selected_team = st.selectbox("Select Team", teams_in_league, 
                                                  index=teams_in_league.index(st.session_state.selected_team))

    positions = ['GK', 'DF', 'MF', 'FW']
    st.session_state.selected_position = st.selectbox("Select Position", positions, 
                                                      index=positions.index(st.session_state.selected_position))

    players_in_team = unique_sorted_list('Player', condition=(merged_df['League'] == st.session_state.selected_league) & 
                                                          (merged_df['Team'] == st.session_state.selected_team) & 
                                                          (merged_df['Position'].str.contains(st.session_state.selected_position)))
    
    if players_in_team:
        st.session_state.selected_player = st.selectbox("Select Player", players_in_team, 
                                                        index=players_in_team.index(st.session_state.selected_player) if st.session_state.selected_player in players_in_team else 0)
    else:
        st.session_state.selected_player = None

# Apply Filters
filtered_df = merged_df[
    (merged_df['League'] == st.session_state.selected_league) &
    (merged_df['Team'] == st.session_state.selected_team) &
    (merged_df['Position'].str.contains(st.session_state.selected_position)) &
    (merged_df['Player'] == st.session_state.selected_player)
]

st.write(f"Showing data for **{st.session_state.selected_player}** from {st.session_state.selected_team} ({st.session_state.selected_league})")
st.dataframe(filtered_df)

