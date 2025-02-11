import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data.data_loader import store_session_data

st.set_page_config(page_title="Player Comparison", page_icon="⚖️", layout="wide")

st.title("⚖️ Player Comparison")
st.caption("Compare Football Players Side-by-Side! 🔄")
st.markdown("---")

# Load data if not in session state
if 'merged_data' not in st.session_state or 'data' not in st.session_state:
    store_session_data()

# Retrieve session data
merged_df = st.session_state.merged_data
data = st.session_state.data

def player_selection(column, key):
    """Handles league, team, position, and player selection within a column."""
    with column:
        league = st.radio("Select League:", sorted(merged_df['League'].unique()), key=f"{key}_league")
        team = st.selectbox("Select Team:", sorted(merged_df.loc[merged_df['League'] == league, 'Team'].unique()), key=f"{key}_team")

        df = merged_df[(merged_df['League'] == league) & (merged_df['Team'] == team)]
        df['Primary Position'] = df['Position'].str.split(',').str[0]

        position = st.selectbox("Select Position:", ['GK', 'DF', 'MF', 'FW'], key=f"{key}_position")
        players = sorted(df.loc[df['Primary Position'] == position, 'Player'].unique())

        if key == "player2" and player1 in players:
            players.remove(player1)

        player = st.selectbox("Select Player:", players, key=f"{key}_player")
        return df[df['Player'] == player].reset_index(drop=True), player

lc, rc = st.columns(2)
player1_df, player1 = player_selection(lc, "player1")
player2_df, player2 = player_selection(rc, "player2")

st.markdown("---")

def highlight(row):
    """Highlights the greater value in green and the lesser in red for each stat."""
    val1, val2 = row.iloc[0], row.iloc[1]  # Get the two values being compared
    
    styles = ['', '']  # Default empty styles for both values

    if pd.isna(val1) or pd.isna(val2):  # Handle missing values
        return ['color: gray;' for _ in row]  

    if val1 > val2:
        styles[0] = 'color: lawngreen; font-weight: bold;'  # Player 1 wins
        styles[1] = 'color: red;'  # Player 2 loses
    elif val2 > val1:
        styles[0] = 'color: red;'  # Player 1 loses
        styles[1] = 'color: lawngreen; font-weight: bold;'  # Player 2 wins

    return styles

def plot_radar_chart(columns):
    """Plots a radar chart comparing two players based on selected stats."""
    
    # Ensure valid column selection
    stats_p1 = player1_df[columns] if all(col in player1_df.columns for col in columns) else pd.DataFrame()
    stats_p2 = player2_df[columns] if all(col in player2_df.columns for col in columns) else pd.DataFrame()

    # Handle missing data
    if stats_p1.empty or stats_p2.empty:
        st.warning("Selected players do not have data for this category.")
        return
    
    # Allow users to select specific stats
    selected_stats = st.multiselect("Choose stats:", columns, default=columns) if st.checkbox(label="Select Specific Stats", value=False, help="Choose specific stats to compare.") else columns

    # Radar chart
    fig = go.Figure()
    for player, stats in zip([player1, player2], [stats_p1, stats_p2]):
        fig.add_trace(go.Scatterpolar(
            r=stats[selected_stats].values.flatten(), 
            theta=selected_stats, 
            fill='toself', 
            name=player
        ))
    
    fig.update_layout(
        polar=dict(bgcolor='#1e2130', radialaxis=dict(visible=True)),
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Create comparison DataFrame
    comparison_df = pd.concat([stats_p1, stats_p2], axis=0).T
    comparison_df.columns = [player1, player2]

    # Apply highlighting in expander section
    with st.expander("Comparison Table", expanded=False):
        st.dataframe(comparison_df.style.apply(highlight, axis=1).format(precision=2))

if 'data' in st.session_state:
    # Remove " Data" from category names and extract column lists
    df_columns = {name.replace(" Data", ""): list(df.columns) for name, df in st.session_state.data.items()}

    # Extract category names dynamically
    categories = list(df_columns.keys())

    # Select category dynamically
    category_choice = st.selectbox(label="Select a Category", options=categories, index=0, help="Select a category to compare players.")

	# Get selected category columns, excluding the first 7 for "Standard" and "Goalkeeping"
    selected_columns = df_columns[category_choice][7:] if category_choice in ["Standard", "Goalkeeping"] else df_columns[category_choice]

    # Plot radar chart dynamically with column names
    plot_radar_chart(selected_columns)
