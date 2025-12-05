import streamlit as st
from PIL import Image
import os

st.set_page_config(page_title="SOUR Advent Calendar 💜", layout="wide")

# ---------------------------------------------------------
# Styling — SOUR theme (purple, scrapbook, soft-grain)
# ---------------------------------------------------------
st.markdown("""
<style>

body {
    background: linear-gradient(135deg, #c77dff 0%, #9d4edd 40%, #7b2cbf 100%);
    background-attachment: fixed;
}

.calendar-title {
    font-size: 52px;
    font-weight: 900;
    color: #6D0E8A;
    letter-spacing: -1px;
    text-shadow: 0 3px 12px rgba(0,0,0,0.35);
    font-family: 'Trebuchet MS', sans-serif;
}

.sour-sticker {
    background: WHITE;
    padding: 10px 14px;
    border-radius: 12px;
    font-weight: 800;
    font-size: 26px;
    font-color:;
    display: inline-block;
    box-shadow: 0 4px 8px rgba(0,0,0,0.25);
    transform: rotate(-4deg);
}

.day-card {
    background: rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 20px;
    backdrop-filter: blur(4px);
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
}

.day-button > button {
    background: #fff5ff !important;
    border-radius: 14px !important;
    border: 3px solid #d4a1ff !important;
    color: 7B2CBF !important;
    font-size: 24px !important;
    font-weight: 800 !important;
    width: 100% !important;
    height: 80px !important;
}

.day-button > button:hover {
    background: #f3d1ff !important;
    border-color: #bb72ff !important;
}

</style>
""", unsafe_allow_html=True)

import pandas as pd

df = pd.read_excel("days_media.xlsx")

df = df.dropna(how="all")   # remove blank rows

messages = {}

for i, row in df.iterrows():
    try:
        day = int(row.iloc[0])
    except:
        st.write("Invalid day at row:", i, row)
        continue

    messages[day] = {
        "message": row.iloc[1],
        "image": None if pd.isna(row.iloc[2]) else str(row.iloc[2]),
        "audio": None if pd.isna(row.iloc[3]) else str(row.iloc[3]),
    }




# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.markdown("""
<div style="text-align:center; margin-top:10px;">
    <span class="sour-sticker">SOUR</span><font-color: black>
    <div class="calendar-title">Momma boo Advent Calendar</div>
    <div style="color:E39EF0; opacity:0.9; margin-top:6px; font-size:18px;">
         Advent Calendar for my pretty cookie princess boo 💜
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")
st.write("")

# ---------------------------------------------------------
# Calendar Grid (6 x 4)
# ---------------------------------------------------------
cols_per_row = 6
rows = 4

if "open_day" not in st.session_state:
    st.session_state.open_day = None

for r in range(rows):
    row = st.columns(cols_per_row)
    for i, col in enumerate(row):
        day = r * cols_per_row + i + 1
        with col:
            st.markdown("<div class='day-card'>", unsafe_allow_html=True)
            clicked = st.container()
            with clicked:
                if st.button(str(day), key=f"day_btn_{day}", help=f"Open day {day}"):
                    st.session_state.open_day = day
            st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Modal popup
# ---------------------------------------------------------
if st.session_state.open_day:
    day = st.session_state.open_day
    entry = messages.get(day)

    with st.expander(f"Day {day} — Today Momma Angel Boo 💜", expanded=True):
        st.write(entry["message"])

        # Image
def display_image_entry(url):
    st.write("🔍 Image debug for:", url)

    if not url:
        st.write("(No URL)")
        return

    # 1) Try Streamlit directly
    try:
        st.write("Trying: st.image(url)...")
        st.image(url)
        st.success("Loaded via st.image(url)")
        return
    except Exception as e:
        st.error(f"Direct st.image error: {e}")

    # 2) Try downloading manually
    try:
        st.write("Trying: requests.get...")
        r = requests.get(url, timeout=10)
        st.write("Status:", r.status_code)
        st.write("Content-Type:", r.headers.get("content-type"))

        if r.status_code == 200:
            try:
                img = Image.open(BytesIO(r.content))
                st.image(img)
                st.success("Loaded via requests → PIL")
                return
            except Exception as e:
                st.error(f"PIL failed: {e}")
        else:
            st.error("Non-200 response")
    except Exception as e:
        st.error(f"Requests error: {e}")

    st.error("❌ Completely failed to load the image.")

# Audio
if entry["audio"]:
    try:
        if entry["audio"].startswith("http"):
                st.audio(entry["audio"])
        else:
            with open(entry["audio"], "rb") as f:
                st.audio(f.read())
    except:
        st.write("(Couldn't load audio)")

st.write("")
if st.button("Close"):
    st.session_state.open_day = None

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.write("---")
st.markdown("<div style='color:white;opacity:0.7;text-align:center;font-size:14px;'>FOR COOKIE OLIVIA BOO AND MOMMA ANGEL BOO I LOVE WITH ALL MY HEART  </div>", unsafe_allow_html=True)















