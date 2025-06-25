import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
from datetime import datetime

st.set_page_config(page_title="GiladScore", layout="centered")

# ---------- CSS ----------
css = """
<style>
    body {background-color:#f4f6f9;font-family:'Segoe UI',sans-serif;}
    .title {text-align:center;font-size:3em;font-weight:bold;color:#1a1a1a;margin-bottom:10px;}
    .box {background-color:white;padding:20px;border-radius:16px;box-shadow:0 4px 12px rgba(0,0,0,0.1);margin-top:20px;}
    .footer {text-align:center;font-size:0.8em;color:gray;margin-top:40px;}
    .credit {font-size:0.9em;color:#888;}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

st.markdown('<div class="title">GiladScore ⭐ מדד שחקני כדורגל</div>', unsafe_allow_html=True)

# ---------- helpers ----------
HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 8

# SofaScore link

def get_sofascore_link(player_name: str) -> str | None:
    query = f"{player_name} site:sofascore.com/player"
    try:
        res = requests.get(
            f"https://www.google.com/search?q={urllib.parse.quote(query)}",
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "url?q=https://www.sofascore.com" in href and "/player/" in href:
                m = re.search(r"url\?q=(https://www\.sofascore\.com[^&]+)", href)
                if m:
                    return m.group(1)
    except Exception:
        pass
    return None

# TheSportsDB basic API

def get_sportsdb_summary(player_name: str) -> dict | None:
    try:
        url = (
            "https://www.thesportsdb.com/api/v1/json/3/searchplayers.php?p="
            f"{urllib.parse.quote(player_name)}"
        )
        js = requests.get(url, timeout=TIMEOUT).json()
        if js and js.get("player"):
            return js["player"][0]
    except Exception:
        pass
    return None

# Wikidata open API (fallback / extra info)

def _get_wikidata_entity(player_name: str) -> str | None:
    search_url = (
        "https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language=en&search="
        f"{urllib.parse.quote(player_name)}"
    )
    try:
        data = requests.get(search_url, timeout=TIMEOUT).json()
        if data.get("search"):
            return data["search"][0]["id"]  # Q-id
    except Exception:
        pass
    return None

def get_wikidata_summary(player_name: str) -> dict | None:
    qid = _get_wikidata_entity(player_name)
    if not qid:
        return None
    try:
        entity_url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
        js = requests.get(entity_url, timeout=TIMEOUT).json()
        ent = js["entities"][qid]
        claims = ent.get("claims", {})
        dob = claims.get("P569", [{}])[0].get("mainsnak", {}).get("datavalue", {}).get("value", {})
        dob = dob.get("time", "") if isinstance(dob, dict) else ""
        height = claims.get("P2048", [{}])[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("amount", "")
        position = (
            claims.get("P413", [{}])[0]
            .get("mainsnak", {})
            .get("datavalue", {})
            .get("value", {})
            .get("id", "")
        )
        club = (
            claims.get("P54", [{}])[0]
            .get("mainsnak", {})
            .get("datavalue", {})
            .get("value", {})
            .get("id", "")
        )
        result = {}
        if dob:
            result["date_of_birth"] = dob[1:11]  # +2021-06-24T00:00:00Z -> 2021-06-24
        if height:
            result["height"] = f"{float(height):.2f} m" if height.startswith("+") else height
        if position:
            result["position_wdid"] = position
        if club:
            result["club_wdid"] = club
        return result if result else None
    except Exception:
        return None

# ---------- UI ----------
name_input = st.text_input("הכנס שם של שחקן (באנגלית או בעברית)")

if name_input:
    player_name = name_input.strip()

    # SofaScore
    sofa_link = get_sofascore_link(player_name)
    sofa_html = "לא נמצא דף SofaScore"
    if sofa_link:
        sofa_html = f"<a href='{sofa_link}' target='_blank'>SofaScore Page</a>"

    # TheSportsDB
    sportsdb = get_sportsdb_summary(player_name)
    sports_html = "לא נמצאו נתונים ב‑TheSportsDB"
    if sportsdb:
        age = sportsdb.get("dateBorn") or "—"
        pos = sportsdb.get("strPosition") or "—"
        team = sportsdb.get("strTeam") or "—"
        sports_html = f"<ul><li>🎂 {age}</li><li>🕴️ {pos}</li><li>🏟️ {team}</li></ul>"

    # Wikidata extra
    wiki = get_wikidata_summary(player_name)
    wiki_html = "—"
    if wiki:
        height = wiki.get("height", "—")
        wiki_html = f"גובה: {height}"

    st.markdown(
        f"""
        <div class='box'>
            <h3>🌟 {player_name.title()}</h3>
            <p><strong>SofaScore:</strong> {sofa_html}</p>
            <p><strong>מידע בסיסי (TheSportsDB):</strong> {sports_html}</p>
            <p><strong>נתונים משלימים (Wikidata):</strong> {wiki_html}</p>
            <p class='credit'>מקורות: SofaScore (link) • TheSportsDB API • Wikidata API</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------- Footer ----------
st.markdown(
    """
<div class="footer">
    הנתונים מוצגים לצורכי הדגמה; כל המקורות מספקים מידע פתוח לשימוש לא‑מסחרי (Wikidata CC0, TheSportsDB CC BY‑SA). Opta אינה מציעה ממשק API פתוח ולכן לא משולבת בשלב זה.
</div>
""",
    unsafe_allow_html=True,
)
