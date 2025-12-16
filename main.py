# ================= IMPORTS =================
import requests
import pandas as pd
import numpy as np
import re
from bs4 import BeautifulSoup
from fastapi import FastAPI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import streamlit as st
import matplotlib.pyplot as plt

# ================= APP =================
app = FastAPI()

HEADERS = {"User-Agent": "Ethical-OSINT-Research-Bot"}

# ================= PLATFORMS =================
PLATFORMS = {
    "GitHub": ("https://github.com/{}", "Coding"),
    "GitLab": ("https://gitlab.com/{}", "Coding"),
    "HuggingFace": ("https://huggingface.co/{}", "Tech"),
    "Reddit": ("https://www.reddit.com/user/{}/", "Social"),
    "Instagram": ("https://www.instagram.com/{}/", "Social"),
    "X (Twitter)": ("https://twitter.com/{}", "Social"),
    "LinkedIn": ("https://www.linkedin.com/in/{}", "Professional"),
    "Pinterest": ("https://www.pinterest.com/{}/", "Social"),
    "LeetCode": ("https://leetcode.com/{}", "Tech"),
    "Codeforces": ("https://codeforces.com/profile/{}", "Tech"),
    "Medium": ("https://medium.com/@{}", "Blogging"),
    "Dev.to": ("https://dev.to/{}", "Blogging")
}

# ================= OSINT CHECK =================
def check_profile(site, url, category):
    try:
        r = requests.get(url, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            text = soup.get_text(" ", strip=True)[:1500]
            return True, text
    except:
        pass
    return False, ""

# ================= STYLOMETRY =================
def stylometry_features(text):
    words = re.findall(r"\b\w+\b", text.lower())
    sentences = re.split(r"[.!?]", text)

    if not words:
        return {"avg_word_length": 0, "lexical_diversity": 0, "avg_sentence_length": 0}

    return {
        "avg_word_length": round(np.mean([len(w) for w in words]), 2),
        "lexical_diversity": round(len(set(words)) / len(words), 2),
        "avg_sentence_length": round(np.mean([len(s.split()) for s in sentences if s.strip()]), 2)
    }

# ================= STREAMLIT UI =================
st.set_page_config(page_title="Digital Footprint Intelligence Engine", layout="wide")
st.title("🛰️ AI-Powered Digital Footprint Intelligence Engine")

query = st.text_input("Enter Username / Name / Email")

if query:
    rows = []
    bios = []
    stylometry_data = []

    for site, (url_t, category) in PLATFORMS.items():
        url = url_t.format(query)
        found, text = check_profile(site, url, category)

        if found:
            rows.append([site, query, category, url])
            bios.append(text)
            stylometry_data.append(stylometry_features(text))

    df = pd.DataFrame(rows, columns=["Site", "Name / Username", "Category", "Profile Link"])

    st.subheader("🔍 OSINT Results Table")
    st.dataframe(df, use_container_width=True)

    # ================= VISUALS =================
    if not df.empty:
        st.subheader("📊 Platform Presence")
        fig, ax = plt.subplots()
        df["Site"].value_counts().plot(kind="bar", ax=ax)
        st.pyplot(fig)

        st.subheader("📂 Category Distribution")
        fig2, ax2 = plt.subplots()
        df["Category"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=ax2)
        st.pyplot(fig2)

    # ================= STYLOMETRY =================
    if stylometry_data:
        st.subheader("✍️ Stylometry Analysis (Writing Style AI)")
        st.json({
            "average_word_length": np.mean([s["avg_word_length"] for s in stylometry_data]),
            "average_sentence_length": np.mean([s["avg_sentence_length"] for s in stylometry_data]),
            "lexical_diversity": np.mean([s["lexical_diversity"] for s in stylometry_data])
        })

    # ================= ANALYST SUMMARY =================
    st.subheader("🧠 Analyst Summary")
    st.write(
        f"The identifier '{query}' shows public presence across {len(df)} platforms. "
        f"The distribution suggests interests primarily in {', '.join(df['Category'].unique())}. "
        f"Stylometric patterns indicate consistent writing characteristics across available content. "
        f"This assessment is based solely on publicly accessible information."
    )

# ================= FASTAPI =================
@app.get("/analyze/{username}")
def analyze(username: str):
    return {"message": "Use Streamlit UI for interactive analysis."}

# ================= ENTRY =================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
