import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta

# Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("Kit's Feeds")
df = conn.read(ttl=0)
# Make sure Volume is numeric
df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce")

today = datetime.now().strftime("%Y/%m/%d")

# Get today's feeds
today_df = df[df["Date"] == today].copy()

# Total volume
total_today = today_df["Volume"].sum()

st.badge(
    f"Total today: {total_today:.0f} ml",
    color="green"
)

if not today_df.empty:
    now = datetime.now()
    
    today_df["FeedDateTime"] = pd.to_datetime(
        today_df["Date"] + " " + today_df["Time"],
        format="%Y/%m/%d %H:%M"
    )

    previous_feeds = today_df[
        today_df["FeedDateTime"] <= now
    ]

    if not previous_feeds.empty:
        last_feed = previous_feeds.loc[
            previous_feeds["FeedDateTime"].idxmax()
        ]

        time_since_feed = now - last_feed["FeedDateTime"]

        badge_color = "red" if time_since_feed > timedelta(hours=2) else "yellow"

        st.badge(
            f"Last feed: {last_feed['Time']} — {last_feed['Volume']:.0f} ml",
            color=badge_color
        )
    else:
        st.badge("Last feed: None", color="red")
else:
    st.badge("Last feed: None", color="red")
# Tabs
tab1, tab2 = st.tabs(["Log Feed", "Today"])


# -------------------------
# TAB 1 — Log Feed
# -------------------------
with tab1:
    st.header("Quick Logs")

    # Quick feed buttons
    col1, col2 = st.columns(2)

    def log_feed(volume):
        current_date = datetime.now().strftime("%Y/%m/%d")
        feed_time_string = datetime.now().strftime("%H:%M")

        # Always get the latest data from Google Sheets
        df = conn.read(ttl=0)

        # Add new row
        new_row = pd.DataFrame([{
            "Date": current_date,
            "Time": feed_time_string,
            "Volume": volume
        }])

        df = pd.concat([df, new_row], ignore_index=True)

        # Save back to Google Sheets
        conn.update(data=df)

        st.success(
            f"Feed logged at {feed_time_string} — {volume} ml"
        )

    with col1:
        if st.button("180 ml", use_container_width=True):
            log_feed(180)

    with col2:
        if st.button("210 ml", use_container_width=True):
            log_feed(210)

    st.divider()

    # Manual feed
    st.subheader("Manual feed")

    feed_time = st.time_input(
        "Feed time",
        value=datetime.now().time().replace(second=0, microsecond=0)
    )

    volume = st.number_input(
        "Volume (ml)",
        min_value=0,
        step=10,
        value=0
    )

    if st.button("Log feed", use_container_width=True):
        current_date = datetime.now().strftime("%Y/%m/%d")
        feed_time_string = feed_time.strftime("%H:%M")

        df = conn.read(ttl=0)

        new_row = pd.DataFrame([{
            "Date": current_date,
            "Time": feed_time_string,
            "Volume": volume
        }])

        df = pd.concat([df, new_row], ignore_index=True)

        conn.update(data=df)

        st.success(
            f"Feed logged at {feed_time_string} — {volume} ml"
        )

# -------------------------
# TAB 2 — Today
# -------------------------
with tab2:
    st.header("Today")

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
            width='stretch'
        )
    else:
        st.info("No feeds logged today.")