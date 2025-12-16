
# ================= IMPORTS =================
import requests
import pandas as pd
import numpy as np
import re
import streamlit as st
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

# ================= CONFIG =================
HEADERS = {"User-Agent": "Ethical-OSINT-Research-Bot"}
TIMEOUT = 6

# ================= PLATFORM REGISTRY =================
# WhatsMyName-style scalable registry (can grow to 600+)
PLATFORMS = [
    ("GitHub", "Coding", "https://github.com/{}"),
    ("GitLab", "Coding", "https://gitlab.com/{}"),
    ("HuggingFace", "Tech", "https://huggingface.co/{}"),
    ("Reddit", "Social", "https://www.reddit.com/user/{}/"),
    ("Instagram", "Social", "https://www.instagram.com/{}/"),
    ("X (Twitter)", "Social", "https://twitter.com/{}"),
    ("LinkedIn", "Professional", "https://www.linkedin.com/in/{}"),
    ("Pinterest", "Social", "https://www.pinterest.com/{}/"),
    ("LeetCode", "Tech", "https://leetcode.com/{}"),
    ("Codeforces", "Tech", "https://codeforces.com/profile/{}"),
    ("Medium", "Blogging", "https://medium.com/@{}"),
    ("Dev.to", "Blogging", "https://dev.to/{}"),
    ("PayPal", "Finance", "https://www.paypal.me/{}"),
    ("Hackster", "Tech", "https://www.hackster.io/{}"),
    ("Arduino", "Tech", "https://projecthub.arduino.cc/{}"),
]

# ================= OSINT EXISTENCE CHECK =================
def profile_exists(url: str) -> bool:
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

# ================= SELECTIVE CONTENT EXTRACTION =================
def extract_public_text(url: str) -> str:
    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT,
            allow_redirects=True
        )
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.get_text(" ", strip=True)[:1200]
    except requests.RequestException:
        return ""

# ================= STYLOMETRY (USER-FRIENDLY) =================
def stylometry_summary(texts):
    if not texts:
        return {
            "writing_consistency": "Insufficient data",
            "language_complexity": "Unknown",
            "communication_style": "Unknown"
        }

    combined_text = " ".join(texts)
    words = re.findall(r"\b\w+\b", combined_text)
    sentences = re.split(r"[.!?]", combined_text)

    avg_sentence_len = (
        np.mean([len(s.split()) for s in sentences if s.strip()])
        if sentences else 0
    )
    vocab_richness = len(set(words)) / len(words) if words else 0

    if avg_sentence_len < 12:
        complexity = "Simple"
    elif avg_sentence_len < 22:
        complexity = "Medium"
    else:
        complexity = "Complex"

    consistency = "Consistent" if vocab_richness > 0.4 else "Variable"

    return {
        "writing_consistency": consistency,
        "language_complexity": complexity,
        "communication_style": "Technical / Informational"
    }

# ================= STREAMLIT UI =================
st.set_page_config(
    page_title="Digital Footprint Intelligence Engine",
    layout="wide"
)

st.title("🛰️ AI-Powered Digital Footprint Intelligence Engine")

query = st.text_input("Enter Username / Name / Email")

if query:
    rows = []
    timeline_platforms = []
    collected_texts = []

    for site, category, url_template in PLATFORMS:
        profile_url = url_template.format(query)

        if profile_exists(profile_url):
            rows.append([site, query, category, profile_url])
            timeline_platforms.append(site)

            # Selective deep analysis (ethical)
            if site in {"GitHub", "Medium", "Dev.to", "Reddit", "HuggingFace"}:
                text = extract_public_text(profile_url)
                if text:
                    collected_texts.append(text)

    df = pd.DataFrame(
        rows,
        columns=["Site", "Name / Username", "Category", "Profile Link"]
    )

    # ================= RESULTS TABLE =================
    st.subheader("🔍 OSINT Results")
    st.dataframe(df, use_container_width=True)

    # ================= CATEGORY GRAPH (SMALL) =================
    if not df.empty:
        st.subheader("📊 Platform Category Distribution")
        fig, ax = plt.subplots(figsize=(4, 3))
        df["Category"].value_counts().plot(kind="bar", ax=ax)
        ax.set_xlabel("Category")
        ax.set_ylabel("Count")
        plt.tight_layout()
        st.pyplot(fig)

    # ================= TIMELINE GRAPH =================
    if timeline_platforms:
        st.subheader("🕒 Digital Footprint Timeline (Relative)")
        fig2, ax2 = plt.subplots(figsize=(5, 2.5))
        ax2.plot(
            range(1, len(timeline_platforms) + 1),
            range(1, len(timeline_platforms) + 1),
            marker="o"
        )
        ax2.set_yticks(range(1, len(timeline_platforms) + 1))
        ax2.set_yticklabels(timeline_platforms)
        ax2.set_xlabel("Discovery Order")
        ax2.set_ylabel("Platform")
        plt.tight_layout()
        st.pyplot(fig2)

    # ================= STYLOMETRY =================
    style_result = stylometry_summary(collected_texts)
    st.subheader("✍️ Writing Style Analysis")
    st.json(style_result)

    # ================= ANALYST SUMMARY =================
    st.subheader("🧠 Analyst Summary")
    if not df.empty:
        st.write(
            f"The identifier **'{query}'** was discovered across "
            f"**{len(df)} public platforms**. The footprint spans "
            f"**{', '.join(df['Category'].unique())}** domains. "
            f"Writing style appears **{style_result['writing_consistency']}** "
            f"with **{style_result['language_complexity']}** language complexity. "
            f"This assessment is based strictly on publicly available data."
        )
    else:
        st.warning("No public accounts found for this identifier.")
