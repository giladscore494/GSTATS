import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="GiladScore", layout="centered")

# CSS עיצוב פנימי
st.markdown("""
    <style>
        body {
            background-color: #f4f6f9;
            font-family: 'Segoe UI', sans-serif;
        }
        .title {
            text-align: center;
            font-size: 3em;
            font-weight: bold;
            color: #1a1a1a;
            margin-bottom: 10px;
        }
        .box {
            background-color: white;
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin-top: 20px;
        }
        .footer {
            text-align: center;
            font-size: 0.8em;
            color: gray;
            margin-top: 40px;
        }
        .credit {
            font-size: 0.9em;
            color: #888;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title">GiladScore ⭐ מדד שחקני כדורגל</div>
""", unsafe_allow_html=True)

name = st.text_input("הכנס שם של שחקן (באנגלית)")

if name:
    query = f"{name} site:transfermarkt.com"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(f"https://html.duckduckgo.com/html/?q={query}", headers=headers)

    soup = BeautifulSoup(res.text, "html.parser")
    links = soup.find_all("a", href=True)
    player_link = None
    for link in links:
        href = link['href']
        if "/profil/spieler/" in href:
            player_link = href
            break

    if player_link:
        tm_url = "https://www.transfermarkt.com" + player_link
        tm_res = requests.get(tm_url, headers=headers)
        tm_soup = BeautifulSoup(tm_res.text, "html.parser")
        value_span = tm_soup.find("div", class_=re.compile("marktwert"))
        value = value_span.text.strip() if value_span else "לא נמצא"

        # FBref - סטטיסטיקות בסיסיות
        fbref_query = f"{name} site:fbref.com"
        fbref_res = requests.get(f"https://html.duckduckgo.com/html/?q={fbref_query}", headers=headers)
        fbref_soup = BeautifulSoup(fbref_res.text, "html.parser")
        fbref_link = None
        for link in fbref_soup.find_all("a", href=True):
            if "/en/players/" in link['href']:
                fbref_link = "https://fbref.com" + link['href']
                break

        stats = "לא נמצאו סטטיסטיקות"
        if fbref_link:
            stats = f"<a href='{fbref_link}' target='_blank'>לצפייה סטטיסטיקות</a>"

        st.markdown(f"""
        <div class="box">
            <h3>🌟 {name}</h3>
            <p><strong>שווי שוק:</strong> {value}</p>
            <p><strong>סטטיסטיקות:</strong> {stats}</p>
            <p class="credit">מקורות: <a href="{tm_url}" target="_blank">Transfermarkt</a>, FBref</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("לא נמצא קישור עמוד השחקן באתר")

st.markdown("""
<div class="footer">
    כל הנתונים נלקחו ממקורות פומביות בשישול הוגן. שווי שוק נלקח מאתר Transfermarkt. הסטטיסטיקות נשלפו מ-FBref. השימוש היא לצורך הדמה והחנה בלבד.
</div>
""", unsafe_allow_html=True)
