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
            background-color: white

