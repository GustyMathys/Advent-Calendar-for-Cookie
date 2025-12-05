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
        # --- BEGIN robust image loader (copy/paste here) ---
import requests
import re
from io import BytesIO
from pathlib import Path
import gdown

CACHE_DIR = Path("image_cache")
CACHE_DIR.mkdir(exist_ok=True)

def file_id_from_url(url):
    if not url:
        return None
    # /d/FILEID/
    m = re.search(r'/d/([^/]+)', url)
    if m:
        return m.group(1)
    # id=FILEID (uc?id= or uc?export=view&id=)
    m = re.search(r'id=([^&]+)', url)
    if m:
        return m.group(1)
    return None

def try_requests_bytes(url, timeout=15):
    try:
        r = requests.get(url, stream=True, timeout=timeout)
        status = r.status_code
        content_type = r.headers.get("content-type","")
        head = r.raw.read(256)  # small peek
        # return tuple with useful info and content if looks like image
        is_image = content_type.startswith("image/") or head.startswith(b'\xff\xd8') or head.startswith(b'\x89PNG')
        return {
            "ok": True,
            "status_code": status,
            "content_type": content_type,
            "head_bytes": head,
            "content": r.content if is_image else None,
            "is_image": is_image,
            "text_snippet": None if is_image else (r.content.decode("utf-8", errors="replace")[:800])
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

def download_with_gdown(file_id, out_path):
    # gdown handles Drive confirmations
    url = f"https://drive.google.com/uc?id={file_id}"
    if out_path.exists():
        return {"ok": True, "path": str(out_path)}
    try:
        gdown.download(url, str(out_path), quiet=True)
        if out_path.exists():
            return {"ok": True, "path": str(out_path)}
        return {"ok": False, "error": "gdown did not create file"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def display_image_entry(entry_image):
    """
    entry_image: URL string or local path
    """
    if not entry_image:
        st.write("(no image)")
        return

    url = str(entry_image).strip()

    # If it's a local path
    if not url.lower().startswith(("http://","https://")):
        try:
            img = Image.open(url)
            st.image(img, use_column_width=True)
            return
        except Exception as e:
            st.write("(Failed to open local file):", e)
            return

    # 1) Try letting streamlit handle it directly (fast)
    try:
        st.image(url, use_column_width=True)
        st.markdown("<small>Loaded via direct st.image(url)</small>", unsafe_allow_html=True)
        return
    except Exception as e:
        st.write("st.image(url) failed:", e)

    # 2) Use requests to inspect bytes and possibly display
    st.write("Trying requests GET to inspect the URL...")
    res = try_requests_bytes(url)
    if not res.get("ok"):
        st.write(" requests error:", res.get("error"))
    else:
        st.write(f" status: {res['status_code']}, content-type: {res['content_type']}")
        # show first bytes (hex up to 40)
        head = res['head_bytes'] or b""
        st.write(" first bytes (hex):", head[:40].hex())
        if res["is_image"] and res["content"]:
            st.image(BytesIO(res["content"]), use_column_width=True)
            st.markdown("<small>Loaded by requests (content-type indicated image)</small>", unsafe_allow_html=True)
            return
        else:
            st.write("Response did not include image bytes. Snippet of returned content (if HTML):")
            st.code(res.get("text_snippet","(no snippet)"))

    # 3) Fallback: extract file id and use gdown to download to cache, then display local file
    st.write("Attempting gdown fallback (will download to server cache)...")
    fid = file_id_from_url(url)
    if not fid:
        st.write("(Could not extract file id from the URL — cannot use gdown.)")
        return

    local_file = CACHE_DIR / f"{fid}"
    gres = download_with_gdown(fid, local_file)
    if not gres.get("ok"):
        st.write("gdown failed:", gres.get("error"))
        st.write("Downloaded URL attempted:", f"https://drive.google.com/uc?id={fid}")
        return

    # Show what we saved
    st.write("Downloaded file to:", gres.get("path"))
    # Try open as image
    try:
        img = Image.open(gres.get("path"))
        st.image(img, use_column_width=True)
        st.markdown("<small>Loaded from local gdown cache</small>", unsafe_allow_html=True)
        return
    except Exception as e:
        st.write("Downloaded file exists but could not be opened as image:", e)
        st.write("File may not be an image or may be corrupted.")
        return
# --- END robust image loader ---




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












