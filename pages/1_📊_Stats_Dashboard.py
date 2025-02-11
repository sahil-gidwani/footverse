import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Stats Dashboard", page_icon="📊", layout="wide")

st.title("📊 Stats Dashboard")
st.caption("Explore Football Data with Interactive Visualizations! 📈")
st.markdown("---")

# Load data if not already in session state
if 'merged_data' not in st.session_state or 'outfield_columns' not in st.session_state or 'goalkeeping_columns' not in st.session_state:
    from data.data_loader import store_session_data
    store_session_data()

# Retrieve session data
merged_df = st.session_state.merged_data
outfield_columns = st.session_state.outfield_columns
goalkeeping_columns = st.session_state.goalkeeping_columns

stats_columns = merged_df.columns[7:]

# Sidebar Filters
with st.sidebar:
    st.write('__Filters__')

    # Helper function to create sorted unique dropdown lists
    def unique_sorted_list(column):
        return sorted(pd.Series(merged_df[column]).dropna().unique().astype(str).tolist())

    # League Filter
    leagues_list = unique_sorted_list('League')
    leagues_filter = st.pills('Leagues', options=leagues_list, selection_mode='multi', default=leagues_list)

    # Apply league filter (only if selection is made)
    filtered_df = merged_df if not leagues_filter else merged_df[merged_df['League'].isin(leagues_filter)]

    # Team Filter
    teams_list = unique_sorted_list('Team')
    teams_filter = st.multiselect('Teams', options=teams_list, default=None, placeholder='Select Teams')

    # Position Filter (Extract Primary Position)
    filtered_df['Primary Position'] = filtered_df['Position'].str.split(',').str[0]
    positions_list = ['GK', 'DF', 'MF', 'FW']
    positions_filter = st.segmented_control('Positions', options=positions_list, selection_mode='multi', default=positions_list)

    # Nation Filter
    nations_list = unique_sorted_list('Nationality')
    nations_filter = st.multiselect('Nations', options=nations_list, default=None, placeholder='Select Nations')

    # Age Filter
    age_filter = st.slider('Select Age Range', 15, 50, (15, 50))

# Apply Filters Function
def filter_dataframe(df, teams=None, positions=None, nations=None, age=None):
    """Filters the DataFrame only when selections are made."""
    if not df.empty:
        if teams:
            df = df[df['Team'].isin(teams)]
        if positions:
            df = df[df['Primary Position' if 'Primary Position' in df else 'Position'].isin(positions)]
        if nations:
            df = df[df['Nationality'].isin(nations)]
        if age and age != (15, 50):  # Apply only if changed from default
            df = df[df['Age'].between(*age)]
    return df

# Apply filters only when selections are made
filtered_df = filter_dataframe(filtered_df, teams_filter or None, positions_filter or None, nations_filter or None, age_filter)

# Drop 'Primary Position' before displaying the filtered DataFrame
filtered_df = filtered_df.drop(columns=['Primary Position'], errors='ignore')

# Display Data
# st.write('__Filtered Data__', filtered_df)

stat = st.selectbox(label='Select a Statistic', options=stats_columns, help='Select a statistic to visualize.', index=4)

number_of_players = st.slider('Select Number of Players', 3, 50, 10, help='Select the number of players to display in the plot.')

if('p90' in stat):
	mean_minutes = int(filtered_df['Minutes'].mean())
	minutes_range = st.slider(
		label='Select Minimum Minutes Played', min_value=0, max_value=int(filtered_df['Minutes'].max()), value=mean_minutes, help='Select the minimum number of minutes played by a player.')
	filtered_df = filtered_df[filtered_df['Minutes'] >= minutes_range]

stat_chart = px.bar(filtered_df.sort_values(
	[stat], ascending=False).head(number_of_players), x='Player', y=stat,
	hover_data=['Position', 'Team', 'Age'], color='League')
st.plotly_chart(stat_chart, use_container_width=True)

# Ensure 'statbox_option' is included and deduplicate columns
columns_to_keep = list(filtered_df.columns[:6]) + [stat]  
# Filter the DataFrame with only selected columns
stat_df = filtered_df[columns_to_keep].sort_values([stat], ascending=False)

# Display the DataFrame
with st.expander(f'View *__Top Players by {stat}__*', expanded=False):
	st.write(stat_df)
