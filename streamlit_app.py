import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Tabs
tab1, tab2 = st.tabs(["Log Feed", "Today"])

# -------------------------
# TAB 1 — Log Feed
# -------------------------
with tab1:
    st.title("Feed")

    # Current time
    now = datetime.now()
    current_time = now.strftime("%H:%M")

    # Feed time
    feed_time = st.time_input(
        "Feed time",
        value=now.time().replace(second=0, microsecond=0)
    )

    # Volume
    volume = st.number_input(
        "Volume (ml)",
        min_value=0,
        step=10,
        value=0
    )

    # Submit
    if st.button("Log feed"):
        current_date = datetime.now().strftime("%Y/%m/%d")
        feed_time_string = feed_time.strftime("%H:%M")

        # Read existing sheet
        df = conn.read()

        # New row
        new_row = pd.DataFrame([{
            "Date": current_date,
            "Time": feed_time_string,
            "Volume": volume
        }])

        # Add row
        df = pd.concat([df, new_row], ignore_index=True)

        # Write back to Google Sheets
        conn.update(data=df)

        st.success(
            f"Feed logged at {feed_time_string} — {volume} ml"
        )


# -------------------------
# TAB 2 — Today
# -------------------------
with tab2:
    st.title("Today")

    today = datetime.now().strftime("%Y/%m/%d")

    # Read sheet
    df = conn.read()

    # Make sure Volume is numeric
    df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce")

    # Get today's feeds
    today_df = df[df["Date"] == today].copy()

    # Total volume
    total_today = today_df["Volume"].sum()

    # Total at the top
    st.subheader(f"Total today: {total_today:.0f} ml")

    # Number of feeds
    st.write(f"**Feeds today: {len(today_df)}**")

    # Show today's feeds
    if len(today_df) > 0:
        st.dataframe(
            today_df[["Time", "Volume"]],
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No feeds logged today.")