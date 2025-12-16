
# ================= IMPORTS =================
import json
import requests
import pandas as pd
import numpy as np
import re
import streamlit as st
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

# ================= CONFIG =================
HEADERS = {"User-Agent": "Ethical-OSINT-Research-Bot"}
TIMEOUT = 2  # short timeout for scale

# ================= LOAD PLATFORM REGISTRY =================
with open("platforms.json", "r", encoding="utf-8") as f:
    PLATFORM_REGISTRY = json.load(f)

# ================= EXISTENCE CHECK =================
def profile_exists(url):
    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT,
            allow_redirects=True
        )
        return r.status_code == 200
    except requests.RequestException:
        return False

# ================= SELECTIVE TEXT EXTRACTION =================
SAFE_ANALYSIS_SITES = {
    "GitHub", "Medium", "Dev.to", "Reddit", "HuggingFace"
}

def extract_public_text(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.get_text(" ", strip=True)[:1200]
    except requests.RequestException:
        return ""

# ================= STYLOMETRY (HUMAN-FRIENDLY) =================
def stylometry_summary(texts):
    if not texts:
        return {
            "writing_consistency": "Insufficient data",
            "language_complexity": "Unknown",
            "communication_style": "Unknown"
        }

    text = " ".join(texts)
    words = re.findall(r"\b\w+\b", text)
    sentences = re.split(r"[.!?]", text)

    avg_sentence = np.mean(
        [len(s.split()) for s in sentences if s.strip()]
    )

    if avg_sentence < 12:
        complexity = "Simple"
    elif avg_sentence < 22:
        complexity = "Medium"
    else:
        complexity = "Complex"

    consistency = "Consistent" if len(set(words)) / len(words) > 0.4 else "Variable"

    return {
        "writing_consistency": consistency,
        "language_complexity": complexity,
        "communication_style": "Technical / Informational"
    }

# ================= STREAMLIT UI =================
st.set_page_config(page_title="Digital Footprint Intelligence Engine", layout="wide")
st.title("🛰️ AI-Powered Digital Footprint Intelligence Engine")

query = st.text_input("Enter Username / Name / Email")

if query:
    rows = []
    timeline = []
    texts = []

    for entry in PLATFORM_REGISTRY:
        site = entry["site"]
        category = entry["category"]
        url = entry["url"].format(query)

        if profile_exists(url):
            rows.append([site, query, category, url])
            timeline.append(site)

            if site in SAFE_ANALYSIS_SITES:
                txt = extract_public_text(url)
                if txt:
                    texts.append(txt)

    df = pd.DataFrame(
        rows,
        columns=["Site", "Name / Username", "Category", "Profile Link"]
    )

    st.subheader("🔍 OSINT Results")
    st.dataframe(df, use_container_width=True)

    # ---------- SMALL GRAPH ----------
    if not df.empty:
        st.subheader("📊 Platform Category Distribution")
        fig, ax = plt.subplots(figsize=(4, 3))
        df["Category"].value_counts().plot(kind="bar", ax=ax)
        plt.tight_layout()
        st.pyplot(fig)

    # ---------- TIMELINE ----------
    if timeline:
        st.subheader("🕒 Digital Footprint Timeline (Relative)")
        fig2, ax2 = plt.subplots(figsize=(5, 2.5))
        ax2.plot(range(len(timeline)), range(len(timeline)), marker="o")
        ax2.set_yticks(range(len(timeline)))
        ax2.set_yticklabels(timeline)
        ax2.set_xlabel("Discovery Order")
        st.pyplot(fig2)

    # ---------- STYLOMETRY ----------
    st.subheader("✍️ Writing Style Analysis")
    style = stylometry_summary(texts)
    st.json(style)

    # ---------- ANALYST SUMMARY ----------
    st.subheader("🧠 Analyst Summary")
    st.write(
        f"The identifier **'{query}'** was found across **{len(df)} platforms** "
        f"from a registry of **{len(PLATFORM_REGISTRY)} sites**. "
        f"Presence spans **{', '.join(df['Category'].unique())}** domains. "
        f"Writing style appears **{style['writing_consistency']}** "
        f"with **{style['language_complexity']}** language complexity."
    )

