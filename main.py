# IMPORTS
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# APP
app = FastAPI(title="AI-Powered Digital Footprint Intelligence Engine")

HEADERS = {"User-Agent": "Ethical-OSINT-Research-Bot"}

# TARGET PLATFORMS
PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Twitter": "https://twitter.com/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "Reddit": "https://www.reddit.com/user/{}/"
}

# OSINT COLLECTION
def check_profile(platform, url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(" ", strip=True)[:1500]
            return {
                "platform": platform,
                "url": url,
                "found": True,
                "bio_text": text
            }
    except:
        pass

    return {
        "platform": platform,
        "url": url,
        "found": False,
        "bio_text": ""
    }


def collect_digital_footprint(username):
    results = []
    for platform, template in PLATFORMS.items():
        results.append(check_profile(platform, template.format(username)))
    return results

# ========================= EXPLAINABLE AI =========================
def explain_identity_confidence(profiles):
    texts = [p["bio_text"] for p in profiles if p["found"] and p["bio_text"]]

    bio_similarity = 0.0
    if len(texts) >= 2:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf = vectorizer.fit_transform(texts)
        bio_similarity = float(np.mean(cosine_similarity(tfidf)))

    username_consistency = 1.0 if len(profiles) > 1 else 0.5
    platform_overlap = min(len(profiles) / 5, 1.0)

    final_score = round(
        0.5 * bio_similarity +
        0.3 * username_consistency +
        0.2 * platform_overlap,
        2
    )

    return {
        "score": final_score,
        "factors": {
            "bio_text_similarity": round(bio_similarity, 2),
            "username_consistency": username_consistency,
            "platform_overlap": round(platform_overlap, 2)
        },
        "explanation": (
            "Identity confidence is derived from textual similarity between public "
            "profile descriptions, consistent username reuse, and cross-platform presence."
        )
    }

# INTEREST INFERENCE
def infer_interests(profiles):
    combined_text = " ".join(
        p["bio_text"].lower() for p in profiles if p["found"]
    )

    keyword_map = {
        "Technology": ["developer", "python", "ai", "ml", "software"],
        "Cybersecurity": ["security", "hacking", "cyber"],
        "Gaming": ["gaming", "game", "esports"],
        "Finance": ["crypto", "trading", "stocks"],
        "Academics": ["research", "university", "student"]
    }

    interests = []
    for topic, words in keyword_map.items():
        if any(word in combined_text for word in words):
            interests.append(topic)

    return interests

# TIMELINE ANALYSIS
def timeline_analysis(profiles):
    timeline = []
    order = 1
    for p in profiles:
        if p["found"]:
            timeline.append({
                "platform": p["platform"],
                "relative_activity_order": order,
                "note": "Relative ordering inferred from public availability"
            })
            order += 1
    return timeline

# VISUAL DATA
def generate_visual_data(profiles, confidence):
    return {
        "platform_presence": {
            p["platform"]: 1 for p in profiles if p["found"]
        },
        "confidence_breakdown": confidence["factors"]
    }

# ANALYST SUMMARY
def analyst_summary(username, confidence, interests, risk):
    interest_text = ", ".join(interests) if interests else "no clearly dominant domains"

    return (
        f"The subject '{username}' demonstrates a consistent digital footprint across "
        f"multiple public platforms. Identity confidence is assessed at "
        f"{confidence['score']}, supported by textual similarity and username reuse. "
        f"Inferred interests indicate involvement in {interest_text}. "
        f"The current digital exposure level is assessed as {risk.lower()}."
    )

# REPORT GENERATION
def generate_report(username):
    profiles = collect_digital_footprint(username)
    found_profiles = [p for p in profiles if p["found"]]

    confidence = explain_identity_confidence(found_profiles)
    interests = infer_interests(found_profiles)
    timeline = timeline_analysis(found_profiles)
    visual_data = generate_visual_data(found_profiles, confidence)

    risk = "Low"
    if len(found_profiles) >= 3:
        risk = "Medium"
    if confidence["score"] > 0.75 and len(found_profiles) >= 4:
        risk = "High"

    summary = analyst_summary(username, confidence, interests, risk)

    return {
        "subject": username,
        "profiles_found": len(found_profiles),
        "platforms": found_profiles,
        "identity_confidence": confidence,
        "inferred_interests": interests,
        "timeline_analysis": timeline,
        "visual_data": visual_data,
        "risk_assessment": risk,
        "analyst_summary": summary,
        "ethics_note": (
            "This analysis is based strictly on publicly available information. "
            "All conclusions are probabilistic and require human verification."
        )
    }

# API ENDPOINT
@app.get("/analyze/{username}")
def analyze_username(username: str):
    return generate_report(username)

# ENTRY
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
