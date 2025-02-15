import streamlit as st
import plotly.express as px
from data.data_loader import store_session_data

# Page Configuration
st.set_page_config(page_title="Stats Dashboard", page_icon="📊", layout="wide")

# Title and Subtitle
st.title("📊 **Stats Dashboard**")
st.caption(
    "Uncover insights, compare performances, and explore football analytics like never before! ⚽📈"
)
st.divider()

# Load data if not in session state
if "merged_data" not in st.session_state:
    store_session_data()

# Retrieve session data
merged_df = st.session_state.merged_data
stats_columns = merged_df.columns[7:]


# Helper function to get unique sorted values
def unique_sorted_list(column):
    return sorted(merged_df[column].dropna().astype(str).unique().tolist())


# Sidebar Filters
with st.sidebar:
    st.subheader("🎯 **Refine Your Search**")

    filters = {
        "Leagues": st.pills(
            "🌍 Select Leagues",
            options=unique_sorted_list("League"),
            selection_mode="multi",
        ),
        "Teams": st.multiselect(
            "🏆 Choose Teams",
            options=unique_sorted_list("Team"),
            placeholder="Pick your favorite teams",
        ),
        "Nations": st.multiselect(
            "🌎 Select Nationalities",
            options=unique_sorted_list("Nationality"),
            placeholder="Filter by country",
        ),
        "Positions": st.segmented_control(
            "⚽ Player Positions",
            options=["GK", "DF", "MF", "FW"],
            selection_mode="multi",
        ),
        "Age": st.slider(
            "📅 Age Range",
            15,
            50,
            (15, 50),
            help="Select the age range of players to analyze.",
        ),
    }

# Apply Filters
filtered_df = merged_df.copy()
filtered_df["Primary Position"] = filtered_df["Position"].str.split(",").str[0]

filter_conditions = {
    "League": filters["Leagues"],
    "Team": filters["Teams"],
    "Nationality": filters["Nations"],
    "Primary Position": filters["Positions"],
}

for col, values in filter_conditions.items():
    if values:
        filtered_df = filtered_df[filtered_df[col].isin(values)]

if filters["Age"] != (15, 50):
    filtered_df = filtered_df[filtered_df["Age"].between(*filters["Age"])]

filtered_df.drop(columns=["Primary Position"], errors="ignore", inplace=True)

# Statistic Selection
st.subheader("🔢 **Dive Into The Numbers!**")
st.info("Choose a statistic to visualize and analyze player performance like a pro! 🔍")

stat = st.selectbox(
    "📈 **Select a Key Performance Metric**",
    options=stats_columns,
    help="Pick a statistic to compare players.",
    index=4,
)
top_n = st.slider(
    "🏅 **How Many Players to Display?**",
    3,
    50,
    10,
    help="Adjust the number of top-performing players shown.",
)

if "p90" in stat:
    min_minutes = st.slider(
        "⏳ **Minimum Minutes Played**",
        0,
        int(filtered_df["Minutes"].max()),
        int(filtered_df["Minutes"].mean()),
        help="Filter players based on game time.",
    )
    filtered_df = filtered_df[filtered_df["Minutes"] >= min_minutes]

st.divider()

# Plot Chart
st.markdown(f"### 🏆 **Top {top_n} Players in {stat}**")
st.success(
    "Here’s a breakdown of the best-performing players based on your selected metric!"
)

stat_chart = px.bar(
    filtered_df.nlargest(top_n, stat),
    x="Player",
    y=stat,
    hover_data=["Position", "Team", "Age"],
    color="League",
    title=f"Top {top_n} Players by {stat}",
)
st.plotly_chart(stat_chart, use_container_width=True)

# Display Data
with st.expander(f"📜 **View Complete List of Top Players by {stat}**", expanded=False):
    st.write(
        filtered_df.iloc[:, :6]
        .join(filtered_df[[stat]])
        .sort_values(stat, ascending=False)
    )

st.divider()
