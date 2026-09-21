import streamlit as st


def _render_brand(description):
    st.markdown(
        f"""
        <div class="sc-brand">
            <div class="sc-brand-mark" aria-hidden="true">S</div>
            <div>
                <div class="sc-brand-name">SnapClass</div>
                <div class="sc-brand-description">{description}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def header_home():
    _render_brand("Face recognition & attendance")


def header_dashboard():
    _render_brand("Attendance workspace")