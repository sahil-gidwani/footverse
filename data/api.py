import time
import requests
import streamlit as st

# Initialize session state for request timestamps
if "api_request_timestamps" not in st.session_state:
    st.session_state.api_request_timestamps = []

API_BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": st.secrets["API_FOOTBALL_DATA_KEY"]}

@st.cache_data(show_spinner="Loading data...", ttl=3600*24*1)
def rate_limited_request(endpoint, params=None, max_retries=3, base_delay=2):
    """Makes a rate-limited API request with retries."""
    
    if "api_request_timestamps" not in st.session_state:
        st.session_state.api_request_timestamps = []
    
    if params is None:
        params = {}

    current_time = time.time()
    
    # Keep only requests from the last 60 seconds
    st.session_state.api_request_timestamps = [
        t for t in st.session_state.api_request_timestamps if current_time - t < 60
    ]

    # Enforce the 10 requests per minute limit
    if len(st.session_state.api_request_timestamps) >= 10:
        wait_time = 60 - (current_time - st.session_state.api_request_timestamps[0])
        # st.warning(f"⚠️ Rate limit reached! Waiting {wait_time:.2f} seconds...")
        time.sleep(wait_time)

    # Exponential backoff for retries
    for attempt in range(max_retries):
        response = requests.get(f"{API_BASE_URL}{endpoint}", headers=HEADERS, params=params)

        if response.status_code == 200:
            st.session_state.api_request_timestamps.append(time.time())  # Log request time
            return response.json()

        elif response.status_code == 429:  # Too many requests
            wait_time = base_delay * (2 ** attempt)
            # st.warning(f"⚠️ Too many requests! Retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)

        else:
            st.error(f"⚠️ Error {response.status_code}: {response.reason}")
            return None

    # st.error("🚫 Maximum retries reached. Try again later.")
    return None
