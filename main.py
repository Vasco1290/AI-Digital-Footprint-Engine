# ---------------- IMPORTS ----------------
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ---------------- APP ----------------
app = FastAPI(title="Digital Footprint Intelligence Engine")

# ---------------- OSINT TARGET PLATFORMS ----------------
PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Twitter": "https://twitter.com/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "Reddit": "https://www.reddit.com/user/{}/"
}

HEADERS = {"User-Agent": "OSINT-Research-Bot"}

# ---------------- CORE FUNCTIONS ----------------

def check_profile(platform, url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            text = soup.get_text(" ", strip=True)[:1000]
            return {
                "platform": platform,
                "url": url,
                "found": True,
                "bio_text": text
            }
    except:
        pass

    return {"platform": platform, "url": url, "found": False}


def collect_digital_footprint(username):
    results = []
    for platform, url_template in PLATFORMS.items():
        profile_url = url_template.format(username)
        results.append(check_profile(platform, profile_url))
    return results


def ai_identity_similarity(profiles):
    texts = [p["bio_text"] for p in profiles if p.get("found") and p.get("bio_text")]

    if len(texts) < 2:
        return 0.4  # low confidence

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(texts)
    sim_matrix = cosine_similarity(tfidf)

    score = np.mean(sim_matrix)
    return round(float(score), 2)


def extract_interests(profiles):
    combined_text = " ".join(
        p["bio_text"] for p in profiles if p.get("found") and p.get("bio_text")
    ).lower()

    keywords = {
        "technology": ["python", "code", "developer", "ai", "ml"],
        "gaming": ["game", "gaming", "esports"],
        "security": ["security", "hacking", "cyber"],
        "finance": ["crypto", "trading", "stocks"],
        "academics": ["research", "university", "student"]
    }

    interests = []
    for topic, words in keywords.items():
        if any(w in combined_text for w in words):
            interests.append(topic)

    return interests


def generate_intelligence_report(username, profiles):
    found_profiles = [p for p in profiles if p["found"]]

    similarity_score = ai_identity_similarity(found_profiles)
    interests = extract_interests(found_profiles)

    risk = "Low"
    if len(found_profiles) >= 4:
        risk = "Medium"
    if similarity_score > 0.75 and len(found_profiles) >= 5:
        risk = "High"

    return {
        "subject": username,
        "profiles_found": len(found_profiles),
        "platforms": found_profiles,
        "identity_confidence": similarity_score,
        "inferred_interests": interests,
        "risk_assessment": risk,
        "ethics_note": "Analysis based only on publicly available data."
    }

# ---------------- API ENDPOINT ----------------

@app.get("/analyze/{username}")
def analyze_username(username: str):
    profiles = collect_digital_footprint(username)
    report = generate_intelligence_report(username, profiles)
    return report

# ---------------- ENTRY ----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
