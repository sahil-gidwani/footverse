import streamlit as st
import plotly.express as px
from data.data_loader import store_session_data

st.set_page_config(page_title="Stats Dashboard", page_icon="📊", layout="wide")

st.title("📊 Stats Dashboard")
st.caption("Explore Football Data with Interactive Visualizations! 📈")
st.markdown("---")

# Load data if not in session state
if 'merged_data' not in st.session_state:
    store_session_data()

# Retrieve session data
merged_df = st.session_state.merged_data
stats_columns = merged_df.columns[7:]

# Helper function to get unique sorted values
def unique_sorted_list(column):
    return sorted(merged_df[column].dropna().astype(str).unique().tolist())

# Sidebar Filters
with st.sidebar:
    st.write('__Filters__')

    filters = {
        "Leagues": st.pills("Leagues", options=unique_sorted_list('League'), selection_mode='multi'),
        "Teams": st.multiselect("Teams", options=unique_sorted_list('Team'), placeholder="Select Teams"),
        "Nations": st.multiselect("Nations", options=unique_sorted_list('Nationality'), placeholder="Select Nations"),
        "Positions": st.segmented_control("Positions", options=['GK', 'DF', 'MF', 'FW'], selection_mode='multi'),
        "Age": st.slider("Select Age Range", 15, 50, (15, 50))
    }

# Apply Filters
filtered_df = merged_df.copy()
filtered_df['Primary Position'] = filtered_df['Position'].str.split(',').str[0]

filter_conditions = {
    'League': filters["Leagues"],
    'Team': filters["Teams"],
    'Nationality': filters["Nations"],
    'Primary Position': filters["Positions"],
}

for col, values in filter_conditions.items():
    if values:
        filtered_df = filtered_df[filtered_df[col].isin(values)]

if filters["Age"] != (15, 50):
    filtered_df = filtered_df[filtered_df['Age'].between(*filters["Age"])]

filtered_df.drop(columns=['Primary Position'], errors='ignore', inplace=True)

# Statistic Selection
stat = st.selectbox("Select a Statistic", options=stats_columns, help="Select a statistic to visualize.", index=4)
top_n = st.slider("Select Number of Players", 3, 50, 10, help="Select the number of players to display.")

if 'p90' in stat:
    min_minutes = st.slider("Select Minimum Minutes Played", 0, int(filtered_df['Minutes'].max()), int(filtered_df['Minutes'].mean()))
    filtered_df = filtered_df[filtered_df['Minutes'] >= min_minutes]

# Plot Chart
stat_chart = px.bar(filtered_df.nlargest(top_n, stat), x='Player', y=stat, hover_data=['Position', 'Team', 'Age'], color='League')
st.plotly_chart(stat_chart, use_container_width=True)

# Display Data
with st.expander(f"View *__Top Players by {stat}__*", expanded=False):
    st.write(filtered_df.iloc[:, :6].join(filtered_df[[stat]]).sort_values(stat, ascending=False))
