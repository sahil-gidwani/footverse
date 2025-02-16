import streamlit as st
import pandas as pd
import numpy as np
from data.data_loader import load_json, store_session_data
from scipy.stats import rankdata

st.set_page_config(page_title="Player Performance Index", page_icon="🧠", layout="wide")

st.title("🧠 Player Performance Index")
st.caption(
    "The missing piece in your scouting strategy—unlock performance insights like never before! 🧩⚡"
)
st.divider()

# Load data if not available in session state
if "merged_data" not in st.session_state or "data" not in st.session_state:
    store_session_data()

merged_df = st.session_state.merged_data
goalkeeping_columns = st.session_state.goalkeeping_columns
outfield_columns = st.session_state.outfield_columns

# Load metric weights
metric_weights = load_json("config/performance-index-weights.json")

# Tabs for Outfield Players and Goalkeepers
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    position_filter = st.segmented_control(
        label="Select Player Type:",
        options=["⚽ Outfield Players", "🧤 Goalkeepers"],
        default="⚽ Outfield Players",
        label_visibility="collapsed",
    )

position_filter = "Goalkeeper" if position_filter == "🧤 Goalkeepers" else "Outfield"


# Filter Players by Position**
def filter_players_by_position(df, position_filter):
    """Filters players based on whether they are Goalkeepers or Outfield players."""
    if position_filter == "Goalkeeper":
        cols_to_drop = [
            col for col in outfield_columns[11:] if col != "Passes Attempted"
        ]
        return df[df["Primary Position"] == "GK"].drop(columns=cols_to_drop)
    else:
        return df[df["Primary Position"] != "GK"].drop(columns=goalkeeping_columns[11:])


merged_df["Primary Position"] = merged_df["Position"].str.split(",").str[0]
filtered_df = filter_players_by_position(merged_df, position_filter)

# Define Outfield and Goalkeeping Categories
goalkeeper_categories = [
    "Goalkeeping Score",
    "Goalkeeping Distribution Score",
    "Goalkeeping Sweeper Score",
]

outfield_categories = [
    category
    for category in metric_weights.keys()
    if category not in goalkeeper_categories
]

# Choose relevant categories based on position
category_options = (
    goalkeeper_categories if position_filter == "Goalkeeper" else outfield_categories
)

# Select Performance Category
selected_category = st.selectbox(
    "🎯 Choose Performance Category:",
    category_options,
    help="Categories group relevant stats based on playing roles and contributions.",
)

# Sidebar Filters
with st.sidebar:
    st.subheader("🎯 **Refine Your Search**")

    filters = {
        "Leagues": st.pills(
            "🌍 Select Leagues",
            options=sorted(merged_df["League"].dropna().unique().tolist()),
            selection_mode="multi",
        ),
        "Teams": st.multiselect(
            "🏆 Choose Teams",
            options=sorted(merged_df["Team"].dropna().unique().tolist()),
            placeholder="Pick your favorite teams",
        ),
        "Nations": st.multiselect(
            "🌎 Select Nationalities",
            options=sorted(merged_df["Nationality"].dropna().unique().tolist()),
            placeholder="Filter by country",
        ),
    }

    if position_filter == "Outfield":
        filters["Positions"] = st.segmented_control(
            "⚽ Player Positions",
            options=["DF", "MF", "FW"],
            selection_mode="multi",
        )

    filters["Age"] = st.slider(
        "📅 Age Range",
        15,
        50,
        (15, 50),
        help="Select the age range of players to analyze.",
    )

# Apply Sidebar Filters
filter_conditions = {
    "League": filters["Leagues"],
    "Team": filters["Teams"],
    "Nationality": filters["Nations"],
}

if position_filter == "Outfield":
    filter_conditions["Primary Position"] = filters.get("Positions", [])

for col, values in filter_conditions.items():
    if values:
        filtered_df = filtered_df[filtered_df[col].isin(values)]

if filters["Age"] != (15, 50):
    filtered_df = filtered_df[filtered_df["Age"].between(*filters["Age"])]

filtered_df.drop(columns=["Primary Position"], errors="ignore", inplace=True)

if filtered_df.empty:
    st.error("No players found with the selected filters. Please adjust your search.")
    st.stop()

# Expander for Custom Metric Selection & Weight Adjustment
with st.expander("Customize Metrics & Weights", icon="⚙️"):
    if position_filter == "Goalkeeper":
        available_metrics = goalkeeping_columns[11:]
    else:
        available_metrics = outfield_columns[11:]

    # Get default metrics from the selected category in JSON
    default_metrics = list(metric_weights.get(selected_category, {}).keys())

    # Filter only valid metrics
    default_metrics = [
        metric for metric in default_metrics if metric in available_metrics
    ]

    # User selection for metrics
    selected_metrics = st.multiselect(
        "📊 Select Metrics:",
        options=available_metrics,
        default=default_metrics,
        help="Choose the performance metrics to include in the analysis.",
    )

    # Dictionary to store metric weights
    metric_weights_input = {}

    cols = st.columns(2)  # Create two columns

    for idx, metric in enumerate(selected_metrics):
        col = cols[idx % 2]  # Alternate between the two columns

        # Use weight from JSON or default to 0
        default_weight = metric_weights.get(selected_category, {}).get(metric, 0.0)

        with col:  # Place the number input inside the selected column
            metric_weights_input[metric] = st.number_input(
                f"⚖️ **{metric}**",
                min_value=-1.0,
                max_value=1.0,
                value=default_weight,
                step=0.01,
                help="Adjust the importance of this metric in the overall score. Values can range from -1 to 1.",
            )

# Check if sum of weights is exactly 1
total_weight = sum(metric_weights_input.values())

if not np.isclose(
    total_weight, 1.0, atol=0.001
):  # Allowing slight float precision error
    st.error(
        f"⚠️ The total sum of weights must be **1.0**. Current sum: **{total_weight:.3f}**"
    )
    st.stop()

# Filter out selected metrics with 0 weight
selected_metrics = [
    metric
    for metric, weight in metric_weights_input.items()
    if not np.isclose(weight, 0.0, atol=0.0001)
]

# Minimum Minutes Played Filter
min_minutes = st.slider(
    "⏳ **Minimum Minutes Played**",
    0,
    int(filtered_df["Minutes"].max()),
    int(filtered_df["Minutes"].mean()),
    help="Filter players based on game time.",
)
filtered_df = filtered_df[filtered_df["Minutes"] >= min_minutes]

st.markdown("######")


# Compute Weighted Linear Combination (WLC) Scores
def calculate_scores(df, selected_metrics, metric_weights_input):
    scores = pd.DataFrame()
    scores["Player"] = df["Player"]

    category_score = np.zeros(len(df))

    for metric in selected_metrics:
        if metric in df.columns:
            metric_values = df[metric].fillna(0)  # Fill NA with 0

            if metric_weights_input[metric] < 0:  # Penalizing negative-weighted metrics
                metric_values *= -1

            category_score += metric_values * abs(metric_weights_input[metric])

    scores["Weighted Score"] = category_score  # Store raw WLC score
    return scores, df[["Player"] + selected_metrics]  # Return raw metrics too


# Quantile Ranking (0-100 Scale)
def quantile_scaling(scores):
    """Converts scores into percentiles (0-100 scale)."""
    scores["Percentile Rank"] = rankdata(scores["Weighted Score"], method="average")
    scores["Percentile Rank"] = (
        (scores["Percentile Rank"] - 1) / (len(scores) - 1) * 100
    )
    return scores


# Enhance Final Scores DataFrame
def enhance_final_scores(df, original_df):
    """Adds extra columns and ensures correct column order."""
    extra_columns = ["Team", "League", "Position", "Age", "Nationality"]
    score_columns = ["Weighted Score", "Percentile Rank"]

    # Merge extra details from original dataframe
    df = df.merge(original_df[["Player"] + extra_columns], on="Player", how="left")

    # Set 'Player' as index
    df.set_index("Player", inplace=True)

    # Reorder columns: Extra columns first, then scores, then other metrics
    column_order = (
        extra_columns
        + score_columns
        + [col for col in df.columns if col not in extra_columns + score_columns]
    )
    df = df[column_order]

    return df


# Compute Scores for Selected Category
category_scores, raw_metrics_df = calculate_scores(
    filtered_df, selected_metrics, metric_weights_input
)
final_scores_df = quantile_scaling(category_scores)

# Merge Metrics for Display
final_scores_df = raw_metrics_df.merge(final_scores_df, on="Player")

# Enhance with additional player info and reorder columns
final_scores_df = enhance_final_scores(final_scores_df, filtered_df)

# Ensure index uniqueness
final_scores_df = final_scores_df.loc[~final_scores_df.index.duplicated(keep="first")]

# Display Results
st.caption(f"🔍 Analyzing **{selected_category}** Metrics")

# Define the columns that should have the gradient
gradient_columns = ["Weighted Score"]

# Apply styling
styled_df = (
    final_scores_df.sort_values("Percentile Rank", ascending=False)
    .style.background_gradient(cmap="RdYlGn", subset=gradient_columns)
    .format({col: "{:.2f}" for col in final_scores_df.columns}, precision=2)
    .format({"Weighted Score": "{:.3f}", "Age": "{:.3f}"}, precision=3)
)

# Display DataFrame with styling
st.dataframe(styled_df)

with st.expander("**Performance Index Metrics**", expanded=False, icon="ℹ️"):
    st.info(
        "📊 **Weighted Score**: A combined score based on selected metrics, adjusted by their assigned weights. Higher values indicate stronger overall performance."
    )
    st.info(
        "🎖️ **Percentile Rank**: Compares a player's score to others, placing them on a 0-100 scale. A higher percentile means better relative performance."
    )

st.divider()
