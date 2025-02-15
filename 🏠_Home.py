import streamlit as st
from data.data_loader import store_session_data

# Page Configuration
st.set_page_config(page_title="Footverse", page_icon="⚽", layout="wide")

# Title and Subtitle
st.title("⚽ :red[Footverse]")
st.caption(
    "Unlock the Power of Football Analytics – Dive into the Numbers Behind the Game! ⚽📊"
)
st.divider()

# Ensure data is loaded into session state
if "merged_data" not in st.session_state:
    store_session_data()

# Home Page Content
st.header("🚀 Welcome to Footverse!")
st.write(
    """
Football isn’t just a game—it’s a world of numbers, patterns, and insights. **Footverse** brings you cutting-edge analytics, transforming raw data into meaningful insights. Whether you're a coach, analyst, scout, or a passionate fan, this is your ultimate **football data hub**!
"""
)

st.markdown("### 🔍 What You Can Do with Footverse")
st.write(
    """
- **Explore Player & Team Stats** – Analyze detailed player performances across leagues.  
- **Compare Players** – See how your favorite players stack up against their peers.  
- **Unlock Advanced Metrics** – Go beyond basic stats with percentile rankings & performance heatmaps.  
- **Goalkeeping & Outfield Insights** – Get specialized reports tailored for each position.  
"""
)

st.markdown("### 🏆 How It Works?")
st.write(
    """
1️⃣ **Select a League, Team & Position** – Narrow down your search with intuitive filters.  
2️⃣ **Analyze Player Performance** – Get in-depth breakdowns with percentile rankings.  
3️⃣ **Visualize Data** – Heatmaps and interactive tables make insights easy to understand.  
4️⃣ **Scout Smarter** – Use data-driven decision-making for scouting, transfers, and analysis.  
"""
)

st.markdown("### 📢 Why Footverse?")
st.write(
    """
✅ **Data-Powered Football** – Get insights from real match data.  
✅ **Intuitive & Interactive** – No more spreadsheets, just clean, visualized stats.  
✅ **Built for Fans & Professionals** – Whether you're an analyst, coach, or fan, there's something for you.  
"""
)

st.success(
    "🏁 **Start Exploring Now!** Dive into the stats and discover football like never before! ⚽🚀"
)

# st.divider()
# st.subheader("📊 Data Preview")
# st.write(st.session_state.merged_data)


@st.dialog("🌟 Share Your Feedback")
def feedback_dialog(message, icon):
    st.write("We value your feedback! Let us know what you think about Footverse.")
    user_feedback = st.text_area(
        "Your Thoughts", placeholder="Tell us what you liked or what we can improve..."
    )

    if st.button("Submit", type="primary"):
        st.toast(message, icon=icon)
        st.session_state.feedback_submitted = True
        st.rerun()


st.divider()
st.caption("How was your experience with Footverse?")
selected = st.feedback("stars")

if selected is not None and "feedback_submitted" not in st.session_state:
    if selected >= 3:
        message = (
            "🌟 Thanks for the amazing rating! We’re thrilled you love Footverse! 🔥"
        )
        icon = "🥳"
    elif selected == 2:
        message = "✨ Thanks for your feedback! Let us know how we can make Footverse even better. 💡"
        icon = "🤝"
    else:
        message = "😔 Sorry to hear that! We appreciate your feedback and will work to improve. 🙌"
        icon = "🛠️"

    feedback_dialog(message, icon)
