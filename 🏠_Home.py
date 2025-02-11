import streamlit as st
from data.data_loader import store_session_data

st.set_page_config(page_title="Footverse", page_icon="⚽", layout="wide")

st.title("⚽ :red[Footverse]")
st.caption("Unlock the Power of Football Analytics – Dive into the Numbers Behind the Game! ⚽📊")
st.markdown("---")

if 'outfield_data' not in st.session_state or 'goalkeeping_data' not in st.session_state:
    store_session_data()

st.subheader("Data")
st.write(st.session_state.merged_data)
