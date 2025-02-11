# Footverse

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://footverse.streamlit.app/)

## Overview

Footverse is a Streamlit-based web application designed to fetch, process, and analyze football data from various sources, primarily fbref.com. The application utilizes caching, rate limiting, data merging, and structured JSON configurations to efficiently handle and present football statistics.

## Features

- **Player Scouting Reports**: Displays detailed scouting reports with key statistics.
- **Data Fetching with Rate Limiting**: Ensures compliance with external API request limits (max 10 requests per 60 seconds).
- **JSON-based Column Mappings**: Dynamically maps and renames columns based on JSON configurations.
- **Data Cleaning & Processing**: Handles multi-level column headers, removes unnecessary columns, and standardizes league names.
- **Streamlit Caching**: Optimizes performance by caching data for 24 hours.
- **Merging Multiple Data Sources**: Combines different datasets into a unified structure.

---

## Technical Implementation

### 1. **Data Loading & Error Handling**

#### `load_json(file_path)`

- Loads and validates JSON files containing column mappings and dataset configurations.
- Checks for missing or empty files and handles JSON decoding errors gracefully.

```python
@st.cache_data(show_spinner="Setting up...")
def load_json(file_path):
    if not os.path.exists(file_path):
        st.error(f"⚠️ JSON file '{file_path}' not found!")
        return None
    if os.path.getsize(file_path) == 0:
        st.error(f"⚠️ JSON file '{file_path}' is empty!")
        return None
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        st.error(f"⚠️ Error parsing JSON file '{file_path}'.")
        return None
```

### 2. **Rate-Limited Data Fetching**

#### `fetch_with_retries(url, max_retries=5, base_delay=2)`

- Implements rate limiting (10 requests per 60 seconds).
- Uses exponential backoff with jitter for handling HTTP 429 errors.
- Extracts tables from HTML responses and converts them to pandas DataFrames.

```python
if "request_timestamps" not in st.session_state:
    st.session_state.request_timestamps = []

current_time = time.time()
st.session_state.request_timestamps = [t for t in st.session_state.request_timestamps if current_time - t < 60]

if len(st.session_state.request_timestamps) >= 10:
    wait_time = 60 - (current_time - st.session_state.request_timestamps[0])
    st.warning(f"⚠️ Rate limit reached! Waiting {wait_time:.2f} seconds before next request...")
    time.sleep(wait_time)
```

### 3. **Data Processing**

#### `load_data(url, json_file=None, standard=False, goalkeeping=False)`

- Fetches football statistics and processes them according to JSON-based column mappings.
- Cleans data by removing duplicate and empty columns.
- Joins multi-level headers into a single row.

```python
df.columns = [' '.join(col).strip() for col in df.columns]
df.reset_index(drop=True, inplace=True)
```

### 4. **Merging Multiple Data Sources**

#### `merge_data(*dfs, how="outer", on=None)`

- Merges different datasets (standard stats, passing, goalkeeping, etc.).
- Ensures column consistency and standardizes league names.

### 5. **Session State Management**

- Stores datasets in `st.session_state` for seamless interactions.
- Keeps track of outfield and goalkeeping statistics separately.

```python
if "data" not in st.session_state:
    st.session_state.data = {}
```

---

## Future Enhancements

- **Interactive Visualizations**: Implementing charts for better insights.
- **Machine Learning Predictions**: Using AI for performance forecasting.
- **User Authentication**: Enabling personalized dashboards.

---

## Installation

### **Requirements**

- Python 3.8+
- Required Libraries: `streamlit`, `pandas`, `requests`

### **Run Locally**

```sh
pip install -r requirements.txt
streamlit run app.py
```

---

## Contributing

If you'd like to contribute, please fork the repository and submit a pull request with your changes.

---

## License

This project is licensed under the MIT License.
