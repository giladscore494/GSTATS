import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

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

name_input = st.text_input("הכנס שם של שחקן (באנגלית או בעברית)")

if name_input:
    name = name_input.strip().lower()
    name_encoded = urllib.parse.quote(name)
    query = f"{name} site:transfermarkt.com"
    headers = {"User-Agent": "Mozilla/5.0"}

    # DuckDuckGo search for Transfermarkt
    search_url = f"https://html.duckduckgo.com/html/?q={query}"
    res = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    player_link = None

    for link in soup.find_all("a", href=True):
        href = link['href']
        if "/l/?uddg=" in href and "transfermarkt.com" in href:
            match = re.search(r"/l/\?uddg=(https%3A%2F%2Fwww\.transfermarkt\.com[^"]+)", href)
            if match:
                encoded_url = match.group(1)
                decoded_url = urllib.parse.unquote(encoded_url)
                player_link = decoded_url
                break

    if player_link:
        tm_url = player_link
        tm_res = requests.get(tm_url, headers=headers)
        tm_soup = BeautifulSoup(tm_res.text, "html.parser")
        value_span = tm_soup.find("div", class_=re.compile("marktwert"))
        value = value_span.text.strip() if value_span else "לא נמצא"

        # FBref - סטטיסטיקות בסיסיות (Google fallback)
        fbref_query = f"{name} site:fbref.com"
        fbref_search_url = f"https://www.google.com/search?q={fbref_query}"
        fbref_res = requests.get(fbref_search_url, headers=headers)
        fbref_soup = BeautifulSoup(fbref_res.text, "html.parser")
        fbref_link = None
        for link in fbref_soup.find_all("a", href=True):
            href = link['href']
            if "url?q=https://fbref.com" in href and "/en/players/" in href:
                match = re.search(r"url\?q=(https://fbref\.com[^&]+)&", href)
                if match:
                    fbref_link = match.group(1)
                    break

        stats = "לא נמצאו סטטיסטיקות"
        if fbref_link:
            stats = f"<a href='{fbref_link}' target='_blank'>לצפייה סטטיסטיקות</a>"

        st.markdown(f"""
        <div class="box">
            <h3>🌟 {name_input.title()}</h3>
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

