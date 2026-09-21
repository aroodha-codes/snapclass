import streamlit as st


def _render_footer():
    st.markdown(
        """
        <div class="sc-footer">
            <span><strong>SnapClass</strong></span>
            <span>Face recognition · Attendance management</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def footer_home():
    _render_footer()


def footer_dashboard():
    _render_footer()