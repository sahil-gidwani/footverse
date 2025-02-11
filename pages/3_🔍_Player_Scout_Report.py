import streamlit as st
import random
import pandas as pd
from data.data_loader import store_session_data

st.set_page_config(page_title="Player Scout Report", page_icon="🔍", layout="wide")

st.title("🔍 Player Scout Report")
st.caption("Scout Football Players with Advanced Analytics! 📈")
st.markdown("---")

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

    # League Selection
    st.session_state.selected_league = st.radio(
        "Select League", unique_sorted_list('League'), 
        index=unique_sorted_list('League').index(st.session_state.selected_league)
    )

    # Team Selection (Ensure selected team exists in the league)
    teams_in_league = unique_sorted_list('Team', condition=(merged_df['League'] == st.session_state.selected_league))
    st.session_state.selected_team = st.selectbox(
        "Select Team", teams_in_league, 
        index=teams_in_league.index(st.session_state.selected_team) if st.session_state.selected_team in teams_in_league else 0
    )

    # Position Selection
    positions = ['GK', 'DF', 'MF', 'FW']
    st.session_state.selected_position = st.selectbox(
        "Select Position", positions, 
        index=positions.index(st.session_state.selected_position)
    )

    # Player Selection (Ensure selected player exists)
    players_in_team = unique_sorted_list('Player', condition=(merged_df['League'] == st.session_state.selected_league) & 
                                                          (merged_df['Team'] == st.session_state.selected_team) & 
                                                          (merged_df['Primary Position'] == st.session_state.selected_position))
    
    if players_in_team:
        st.session_state.selected_player = st.selectbox(
            "Select Player", players_in_team, 
            index=players_in_team.index(st.session_state.selected_player) if st.session_state.selected_player in players_in_team else 0
        )
    else:
        st.session_state.selected_player = None

@st.cache_data(show_spinner="Analyzing Data...")
def calculate_percentile_ranks(df, position):
    """Calculates percentile ranks for each player within their position group."""
    position_df = df[df['Primary Position'] == position]  # Filter players by position
    return position_df[stats_columns].rank(pct=True) * 100

# Apply Filters
filtered_df = merged_df[
    (merged_df['League'] == st.session_state.selected_league) &
    (merged_df['Team'] == st.session_state.selected_team) &
    (merged_df['Position'].str.contains(st.session_state.selected_position)) &
    (merged_df['Player'] == st.session_state.selected_player)
]

# Calculate Percentile Ranks for Selected Position
position_percentiles = calculate_percentile_ranks(merged_df, st.session_state.selected_position)

merged_df.drop(columns=['Primary Position'], errors='ignore', inplace=True)
filtered_df.drop(columns=['Primary Position'], errors='ignore', inplace=True)

# Merge Percentile Ranks with Filtered Data
filtered_df = filtered_df.merge(position_percentiles, left_index=True, right_index=True, suffixes=("", " Percentile"))

st.write(f"Showing data for **{st.session_state.selected_player}** from {st.session_state.selected_team} ({st.session_state.selected_league})")
# st.write(filtered_df)

# Extract statistics and their corresponding percentile columns
stats_columns = stats_columns.tolist()
if st.session_state.selected_position == 'GK':
	stats_columns = list(pd.Index(stats_columns).intersection(goalkeeping_columns))
else:
	stats_columns = list(pd.Index(stats_columns).intersection(outfield_columns))
percentile_columns = [col + " Percentile" for col in stats_columns]

# Extract values using column names instead of iloc
stats_values = filtered_df[stats_columns].values.flatten().tolist()
percentile_values = filtered_df[percentile_columns].values.flatten().tolist()

# Create DataFrame
scout_report_df = pd.DataFrame({'Statistics': stats_columns, 'Value': stats_values, 'Percentile': percentile_values})
scout_report_df.set_index('Statistics', inplace=True)

# Display the Scout Report
with st.expander("View *__Scout Report__*", expanded=True):
	st.dataframe(
		scout_report_df.style
		.format({'Percentile': lambda x: f"{x:.2f}%"})
		.background_gradient(cmap='RdYlGn', subset=['Percentile'])
		.format(precision=2, subset=['Value'])
	)

# 🎯 **Dynamically Generate Expanders from Session Data**
if "data" in st.session_state:
    dataset_names = list(st.session_state.data.keys())
    
    # Apply dataset filtering based on selected position
    if st.session_state.selected_position == "GK":
        dataset_names = dataset_names[:] # Include all datasets
    else:
        dataset_names = dataset_names[:-2]  # Exclude last 2 datasets

    for dataset_name in dataset_names:
        df = st.session_state.data[dataset_name]
        if not df.empty:  # Ensure dataframe has data
            with st.expander(str(dataset_name).replace(" Data", '')):
                # Extract relevant statistics from scout_report_df
                valid_columns = [col for col in scout_report_df.index if col in df.columns]

                # Display corresponding stats with formatting
                st.dataframe(
                    scout_report_df.loc[valid_columns].style
                    .format({'Percentile': "{:.2f}%"})
                    .background_gradient(cmap='RdYlGn', subset=['Percentile'])
                    .format(precision=2, subset=['Value'])
                )
