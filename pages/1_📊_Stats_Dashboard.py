import streamlit as st
import pandas as pd
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

if filtered_df.empty:
    st.error(
        "No players found based on the selected filters. Please adjust your search."
    )
    st.stop()

tabs = st.tabs(["🔢 Overall Player Performance", "🔄 Multi-Stat Comparison"])

with tabs[0]:
    st.info("Analyze player performances based on key performance metrics.")

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

    # Plot Chart
    stat_chart = px.bar(
        filtered_df.nlargest(top_n, stat),
        x="Player",
        y=stat,
        hover_data=["Position", "Team", "Age"],
        color="League",
        title=f"🏆 Top {top_n} Players by {stat}",
    )
    st.plotly_chart(stat_chart, use_container_width=True)

    # Display Data
    with st.expander(
        f"📜 **View Complete List of Top Players by {stat}**", expanded=False
    ):
        st.dataframe(
            filtered_df.iloc[:, :6]
            .join(filtered_df[[stat]])
            .sort_values(stat, ascending=False)
            .style.background_gradient(cmap="RdYlGn", subset=[stat])
            .format({"Age": "{:.3f}"})
        )

with tabs[1]:
    st.info("Compare player performances across multiple statistics.")

    # Select 2 or 3 Stats
    selected_stats = st.multiselect(
        "📈 Choose 2 or 3 Stats for Comparison",
        options=stats_columns,
        default=stats_columns[4:6],
        max_selections=3,
        help="Select multiple statistics to compare player performances.",
    )

    top_n_multi = st.slider(
        "🏅 **How Many Players to Display for Multi-Stat Analysis?**",
        3,
        50,
        10,
        help="Adjust the number of top-performing players shown.",
    )

    if len(selected_stats) < 2:
        st.warning("⚠️ Please select at least **2 stats** to compare.")
    else:
        # Compute total ranking score by summing selected statistics
        filtered_df["Stat_Sum"] = filtered_df[selected_stats].sum(axis=1)
        top_players_multi_df = filtered_df.nlargest(top_n_multi, "Stat_Sum")

        if len(selected_stats) == 2:
            # 2D Scatter Plot
            scatter_fig = px.scatter(
                top_players_multi_df,
                x=selected_stats[0],
                y=selected_stats[1],
                color="Player",
                hover_data=["Team", "Age"],
                title=f"🏆 Top {top_n} Players by {selected_stats[0]} vs {selected_stats[1]}",
                size="Stat_Sum",
            )
        else:
            # 3D Scatter Plot (for 3 Stats)
            scatter_fig = px.scatter_3d(
                top_players_multi_df,
                x=selected_stats[0],
                y=selected_stats[1],
                z=selected_stats[2],
                color="Player",
                hover_data=["Team", "Age"],
                title=f"🏆 Top {top_n} Players by {selected_stats[0]} vs {selected_stats[1]} vs {selected_stats[2]}",
                size="Stat_Sum",
            )

        st.plotly_chart(scatter_fig, use_container_width=True)

        # Display Data
        with st.expander(
            f"📜 **View Complete List of Top Players by {', '.join(selected_stats)}**",
            expanded=False,
        ):
            # Determine the formatting for selected stats
            format_dict = {"Age": "{:.3f}"}  # Ensure Age is formatted
            for stat in selected_stats:
                if pd.api.types.is_float_dtype(filtered_df[stat]):
                    format_dict[stat] = "{:.3f}"  # Format floats to 3 decimal places
                else:
                    format_dict[stat] = "{}"  # Keep integers as they are

            # Display Data with Proper Formatting
            st.dataframe(
                filtered_df.iloc[:, :6]
                .join(filtered_df[selected_stats])
                .join(filtered_df["Stat_Sum"])
                .sort_values("Stat_Sum", ascending=False)
                .drop(columns=["Stat_Sum"])  # Remove helper column
                .style.background_gradient(cmap="RdYlGn", subset=selected_stats)
                .format(format_dict)  # Apply dynamic formatting
            )

st.divider()
