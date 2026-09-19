import streamlit as st


def footer_home():
    st.markdown("""
        <div style="
            margin-top: 2rem;
            text-align: center;
            color: #E0E3FF;
            font-size: 14px;
        ">
            SnapClass • AI-Powered Smart Attendance
        </div>
    """, unsafe_allow_html=True)


def footer_dashboard():
    st.markdown("""
        <div style="
            margin-top: 2rem;
            text-align: center;
            color: #666;
            font-size: 14px;
        ">
            SnapClass • AI-Powered Smart Attendance
        </div>
    """, unsafe_allow_html=True)