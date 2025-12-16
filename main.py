# ================= IMPORTS =================
import os
import json
import requests
import pandas as pd
import numpy as np
import re
import streamlit as st
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# ================= CONFIG =================
HEADERS = {"User-Agent": "Ethical-OSINT-Research-Bot"}
TIMEOUT = 2
MAX_WORKERS = 25   # controls speed vs safety

# ================= LOAD ALL REGISTRIES =================
def load_platform_registries(folder="registries"):
    platforms = []
    for file in os.listdir(folder):
        if file.endswith(".json"):
            with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
                platforms.extend(json.load(f))
    return platforms

PLATFORM_REGISTRY = load_platform_registries()

# ================= OSINT EXISTENCE CHECK =================
def check_platform(entry, query):
    site = entry["site"]
    category = entry["category"]
    url = entry["url"].format(query)

    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT,
            allow_redirects=True
        )
        if r.status_code == 200:
            return (site, query, category, url)
    except requests.RequestException:
        pass

    return None

# ================= SELECTIVE CONTENT EXTRACTION =================
SAFE_ANALYSIS_SITES = {
    "GitHub", "Medium", "Dev.to", "Reddit", "HuggingFace"
}

def extract_public_text(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.get_text(" ", strip=True)[:1200]
    except:
        return ""

# ================= STYLOMETRY =================
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

    avg_sentence = np.mean([len(s.split()) for s in sentences if s.strip()])
    vocab_ratio = len(set(words)) / len(words)

    complexity = "Simple"
    if avg_sentence > 12:
        complexity = "Medium"
    if avg_sentence > 22:
        complexity = "Complex"

    return {
        "writing_consistency": "Consistent" if vocab_ratio > 0.4 else "Variable",
        "language_complexity": complexity,
        "communication_style": "Technical / Informational"
    }

# ================= STREAMLIT UI =================
st.set_page_config(page_title="Digital Footprint Intelligence Engine", layout="wide")
st.title("🛰️ AI-Powered Digital Footprint Intelligence Engine")

st.caption(f"Loaded {len(PLATFORM_REGISTRY)} platforms")

query = st.text_input("Enter Username / Name / Email")

if query:
    results = []
    texts = []
    timeline = []

    with st.spinner("Scanning platforms (multithreaded)..."):
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(check_platform, entry, query)
                for entry in PLATFORM_REGISTRY
            ]

            for future in as_completed(futures):
                res = future.result()
                if res:
                    results.append(res)
                    timeline.append(res[0])

    df = pd.DataFrame(
        results,
        columns=["Site", "Name / Username", "Category", "Profile Link"]
    )

    st.subheader("🔍 OSINT Results")
    st.dataframe(df, use_container_width=True)

    # ---------- SMALL CATEGORY GRAPH ----------
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
        plt.tight_layout()
        st.pyplot(fig2)

    # ---------- STYLOMETRY ----------
    for site, _, _, link in results:
        if site in SAFE_ANALYSIS_SITES:
            txt = extract_public_text(link)
            if txt:
                texts.append(txt)

    style = stylometry_summary(texts)
    st.subheader("✍️ Writing Style Analysis")
    st.json(style)

    # ---------- ANALYST SUMMARY ----------
    st.subheader("🧠 Analyst Summary")
    st.write(
        f"The identifier **'{query}'** was found on **{len(df)} platforms** "
        f"from a registry of **{len(PLATFORM_REGISTRY)} sites**. "
        f"Presence spans **{', '.join(df['Category'].unique())}** domains. "
        f"Writing style appears **{style['writing_consistency']}** "
        f"with **{style['language_complexity']}** language complexity."
    )
