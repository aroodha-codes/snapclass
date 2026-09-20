import streamlit as st

LOGO_URL = "https://i.ibb.co/YTYGn5qV/logo.png"

def header_home():
    st.markdown(f"""
    <div style="text-align:center; margin:30px 0;">
        <img src="{LOGO_URL}" style="height:100px;">
        <h1 style="color:#E0E3FF;">SNAP<br>CLASS</h1>
    </div>
    """, unsafe_allow_html=True)

def header_dashboard():
    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:center; gap:10px;">
        <img src="{LOGO_URL}" style="height:85px;">
        <h2 style="color:#5865F2; margin:0;">SNAP<br>CLASS</h2>
    </div>
    """, unsafe_allow_html=True)