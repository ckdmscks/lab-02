# pages/1_Survey.py
import streamlit as st
import pandas as pd
from pathlib import Path
import os  # for file system operations

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Survey Page", page_icon="📝", layout="wide")
st.title("📝 Survey Page")

csv_file = Path("data.csv")

st.write("Please fill out the form below to add your data to the dataset.")

# --- FORM INPUTS (ensures Name, Age, Major, Hours columns exist) ---
with st.form(key="survey_form"):
    name = st.text_input("Enter your name:")
    age = st.number_input("Enter your age:", min_value=0, max_value=120, step=1)
    major = st.selectbox("Select your major:", ["Biomedical", "Computer Science", "Biology", "Other"])
    hours = st.slider("Hours studied today:", 0, 24, 2)  # #NEW interactive widget
    submitted = st.form_submit_button("Submit")

if submitted:
    # Create a new entry as a DataFrame
    new_entry = pd.DataFrame(
        [[name, age, major, hours]],
        columns=["Name", "Age", "Major", "Hours"]
    )

    # Append to CSV if exists, else create a new one
    if csv_file.exists() and os.path.getsize(csv_file) > 0:
        try:
            df = pd.read_csv(csv_file)
            df = pd.concat([df, new_entry], ignore_index=True)
        except Exception:
            df = new_entry.copy()
    else:
        df = new_entry.copy()

    # Save to CSV
    df.to_csv(csv_file, index=False)
    st.success("✅ Data submitted successfully and saved to data.csv!")
    st.dataframe(df.tail(10), use_container_width=True)  # #NEW quick preview

# --- OPTIONAL: show existing data for confirmation ---
st.divider()
st.header("Current Data in CSV")

if csv_file.exists() and os.path.getsize(csv_file) > 0:
    df_current = pd.read_csv(csv_file)
    st.dataframe(df_current, use_container_width=True)
else:
    st.info("No data found yet. Submit a new entry above to create data.csv.")
