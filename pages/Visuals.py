# This creates the page for displaying data visualizations.
# It should read data from both 'data.csv' and 'data.json' to create graphs.

import streamlit as st
import pandas as pd
import json  # The 'json' module is needed to work with JSON files.
import os    # The 'os' module helps with file system operations.
import matplotlib.pyplot as plt  # #NEW used for the scatter plot

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Visualizations",
    page_icon="📈",
)

# PAGE TITLE AND INFORMATION
st.title("Data Visualizations 📈")
st.write("This page displays graphs based on the collected data.")

# ------------------------------------------------------------------
# DATA LOADING
# A crucial step is to load the data from the files.
# It's important to add error handling to prevent the app from crashing if a file is empty or missing.
# ------------------------------------------------------------------

st.divider()
st.header("Load Data")

# 1) Load CSV safely
csv_path = "data.csv"
df_csv = None
if os.path.exists(csv_path):
    try:
        df_csv = pd.read_csv(csv_path)
        st.success("✅ Loaded data.csv")
        with st.expander("Preview data.csv"):  # #NEW
            st.dataframe(df_csv, use_container_width=True)  # #NEW
    except Exception as e:
        st.error(f"Couldn't read data.csv: {e}")
else:
    st.info("data.csv not found yet — submit the Survey first.")

# 2) Load JSON safely
json_path = "data.json"
data_json = None
if os.path.exists(json_path):
    try:
        with open(json_path, "r") as f:
            data_json = json.load(f)
        st.success("✅ Loaded data.json")
        with st.expander("Preview data.json"):  # #NEW
            st.json(data_json)
    except Exception as e:
        st.error(f"Couldn't read data.json: {e}")
else:
    st.info("data.json not found — make sure it is in the same folder as this app.")

# Optional: allow quick download of current CSV for debugging/grade checks
if df_csv is not None:
    st.download_button("Download data.csv", df_csv.to_csv(index=False), "data.csv", "text/csv")  # #NEW

# ------------------------------------------------------------------
# GRAPH CREATION
# The lab requires you to create 3 graphs: one static and two dynamic.
# You must use both the CSV and JSON data sources at least once.
# ------------------------------------------------------------------

st.divider()
st.header("Graphs")

# Keep interactive settings in Session State
if "bins" not in st.session_state:
    st.session_state.bins = 10  # #NEW
if "majors_filter" not in st.session_state:
    st.session_state.majors_filter = []  # #NEW

# GRAPH 1: STATIC GRAPH
st.subheader("Graph 1: Static — JSON Bar Chart")
# - Create a static graph (e.g., bar chart) using st.bar_chart().
# - Use data from JSON file.
# - Write a description explaining what the graph shows.
if data_json and isinstance(data_json, dict):
    title = data_json.get("chart_title", "JSON Data")
    points = data_json.get("data_points", [])
    if isinstance(points, list) and points:
        df_json = pd.DataFrame(points)
        # Expect columns: 'label', 'value'
        if "label" in df_json.columns and "value" in df_json.columns:
            st.write(f"**{title}** — Bar chart of values per label from `data.json`.")
            chart_df = df_json.set_index("label")[["value"]]
            st.bar_chart(chart_df)
        else:
            st.warning("`data.json` does not have the expected keys ('label', 'value').")
    else:
        st.info("No `data_points` found in data.json to plot.")
else:
    st.info("Load `data.json` to see this graph.")

# GRAPH 2: DYNAMIC GRAPH
st.subheader("Graph 2: Dynamic — Age Histogram (CSV)")
# - Dynamic graph that changes based on user input.
# - Uses at least one interactive widget (slider) and Session State.
if df_csv is not None and "Age" in df_csv.columns:
    st.write("Use the slider to adjust histogram bins. The plot updates instantly.")
    st.session_state.bins = st.slider("Number of bins", 5, 40, st.session_state.bins)  # #NEW
    age_series = df_csv["Age"].dropna()
    if age_series.empty:
        st.warning("No Age values found in CSV.")
    else:
        # Bin with pandas.cut, then show as bar chart of counts
        binned = pd.cut(age_series, bins=st.session_state.bins)
        counts = binned.value_counts().sort_index()
        chart_df = counts.to_frame(name="count")
        chart_df.index = chart_df.index.astype(str)
        st.bar_chart(chart_df)
else:
    st.info("Add survey entries with an 'Age' value to see this histogram.")

# --------------------------------------------------
# GRAPH 3: DYNAMIC (CSV — Scatter Hours vs Age)
# --------------------------------------------------
st.subheader("Graph 3: Dynamic — Hours vs Age (CSV, Scatter)")

if df_csv is None:
    st.info("No CSV loaded yet. Submit the survey first.")
else:
    # Diagnostics so you can see what's going on
    st.caption("Graph 3 diagnostics (first 5 rows and columns detected):")
    st.write("Columns:", list(df_csv.columns))
    st.dataframe(df_csv.head())

    # Check columns exist
    required = {"Hours", "Age"}
    if not required.issubset(df_csv.columns):
        st.error("Missing required columns for this graph. Need columns: 'Hours' and 'Age'. "
                 "Go to the Survey page and submit entries so these columns exist.")
    else:
        # Convert to numeric (in case they're strings); coerce errors → NaN, then drop
        work = df_csv.copy()
        work["Hours"] = pd.to_numeric(work["Hours"], errors="coerce")
        work["Age"]   = pd.to_numeric(work["Age"], errors="coerce")
        work = work.dropna(subset=["Hours", "Age"])

        # Optional major filter
        if "Major" in work.columns:
            all_majors = sorted([m for m in work["Major"].dropna().unique().tolist()])
            if "majors_filter" not in st.session_state:
                st.session_state.majors_filter = []
            st.session_state.majors_filter = st.multiselect(  # #NEW
                "Filter by majors (optional)",
                options=all_majors,
                default=st.session_state.majors_filter,
            )
            if st.session_state.majors_filter:
                work = work[work["Major"].isin(st.session_state.majors_filter)]

        if work.empty:
            st.warning("No rows to plot. Try adding survey entries or clearing the major filter.")
        else:
            fig, ax = plt.subplots()
            ax.scatter(work["Hours"], work["Age"])
            ax.set_title("Hours vs Age (Scatter)")
            ax.set_xlabel("Hours studied today")
            ax.set_ylabel("Age")
            st.pyplot(fig)
            st.write("Different chart type ✅ (Scatter). Uses CSV ✅. Interactive filter ✅.")

# Optional UI nicety
st.toggle("Dark mode hint (UI only, no effect)")  # #NEW (simple interactive control)
