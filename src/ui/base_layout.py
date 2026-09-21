import streamlit as st


def style_background_home():
    st.markdown(
        """
        <style>
            .stApp {
                background-color: #F5F7FA;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def style_background_dashboard():
    style_background_home()


def style_base_layout():
    st.markdown(
        """
        <style>
            /* Page layout */
            .block-container {
                max-width: 1100px;
                padding-top: 2.5rem;
                padding-bottom: 2rem;
            }

            .stApp {
                color: #243247;
                font-family:
                    -apple-system, BlinkMacSystemFont,
                    "Segoe UI", Arial, sans-serif;
            }

            /* Typography */
            h1, h2, h3, h4 {
                font-family:
                    -apple-system, BlinkMacSystemFont,
                    "Segoe UI", Arial, sans-serif !important;
                color: #14243B !important;
                letter-spacing: -0.025em;
            }

            h1 {
                font-size: 2.25rem !important;
                font-weight: 700 !important;
                line-height: 1.2 !important;
            }

            h2 {
                font-size: 1.5rem !important;
                font-weight: 650 !important;
                line-height: 1.35 !important;
            }

            h3 {
                font-size: 1.125rem !important;
                font-weight: 600 !important;
            }

            p, li {
                line-height: 1.65;
            }

            /* Buttons */
            .stButton > button {
                min-height: 2.65rem;
                border-radius: 8px !important;
                font-weight: 600 !important;
                box-shadow: none !important;
                transition:
                    background-color 0.15s ease,
                    border-color 0.15s ease;
            }

            .stButton > button[kind="primary"] {
                background-color: #2458C6 !important;
                border: 1px solid #2458C6 !important;
                color: #FFFFFF !important;
            }

            .stButton > button[kind="primary"]:hover {
                background-color: #1D48A3 !important;
                border-color: #1D48A3 !important;
            }

            .stButton > button[kind="secondary"] {
                background-color: #FFFFFF !important;
                border: 1px solid #CDD5DF !important;
                color: #243247 !important;
            }

            .stButton > button[kind="secondary"]:hover {
                background-color: #F0F4FA !important;
                border-color: #8EA4C3 !important;
            }

            .stButton > button[kind="tertiary"] {
                background-color: transparent !important;
                color: #52647C !important;
                border: 1px solid transparent !important;
            }

            .stButton > button[kind="tertiary"]:hover {
                background-color: #EAF0F7 !important;
                color: #183B70 !important;
            }

            .stButton > button:disabled {
                opacity: 0.45;
                cursor: not-allowed;
            }

            .stButton > button:focus-visible {
                outline: 3px solid #AFC7FA !important;
                outline-offset: 2px;
            }

            /* Inputs */
            div[data-testid="stTextInput"] input,
            div[data-testid="stTextArea"] textarea {
                border-radius: 8px;
            }

            /* Tables and expandable sections */
            div[data-testid="stDataFrame"] {
                border: 1px solid #DFE5ED;
                border-radius: 10px;
                overflow: hidden;
            }

            div[data-testid="stExpander"] {
                background-color: #FFFFFF;
                border-radius: 10px;
            }

            hr {
                border-color: #DFE5ED !important;
                margin: 1.25rem 0 !important;
            }

            /* Brand */
            .sc-brand {
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .sc-brand-mark {
                width: 42px;
                height: 42px;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                background: #183B70;
                color: #FFFFFF;
                border-radius: 10px;
                font-size: 23px;
                font-weight: 700;
            }

            .sc-brand-name {
                color: #14243B;
                font-size: 22px;
                font-weight: 700;
                letter-spacing: -0.6px;
                line-height: 1.2;
            }

            .sc-brand-description {
                color: #67768B;
                font-size: 12px;
                margin-top: 3px;
            }

            .sc-home-intro {
                margin: 38px 0 28px;
                max-width: 680px;
            }

            .sc-home-intro p {
                color: #637289;
                font-size: 16px;
                margin-top: 12px;
            }

            .sc-section-label {
                color: #637289;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1.4px;
                text-transform: uppercase;
                margin-bottom: 8px;
            }

            /* Subject cards */
            .sc-subject-card {
                background: #FFFFFF;
                border: 1px solid #DFE5ED;
                border-left: 3px solid #2458C6;
                border-radius: 10px;
                padding: 22px;
                margin-bottom: 12px;
            }

            .sc-subject-title {
                color: #14243B;
                font-size: 19px;
                font-weight: 650;
                margin: 0 0 10px;
                overflow-wrap: anywhere;
            }

            .sc-subject-meta {
                display: flex;
                align-items: center;
                flex-wrap: wrap;
                gap: 12px;
                color: #637289;
                font-size: 13px;
            }

            .sc-subject-code {
                background: #EDF3FF;
                color: #2458C6;
                border-radius: 5px;
                padding: 3px 8px;
                font-size: 12px;
                font-weight: 600;
            }

            .sc-subject-stats {
                display: flex;
                flex-wrap: wrap;
                gap: 24px;
                border-top: 1px solid #EDF0F5;
                margin-top: 18px;
                padding-top: 16px;
            }

            .sc-stat-value {
                color: #14243B;
                font-size: 21px;
                font-weight: 650;
                line-height: 1.2;
            }

            .sc-stat-label {
                color: #67768B;
                font-size: 12px;
                margin-top: 4px;
            }

            /* Footer */
            .sc-footer {
                display: flex;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 8px;
                border-top: 1px solid #DFE5ED;
                margin-top: 40px;
                padding-top: 16px;
                color: #778398;
                font-size: 12px;
            }

            .sc-footer strong {
                color: #52647C;
                font-weight: 600;
            }

            @media (max-width: 640px) {
                .block-container {
                    padding-top: 1.5rem;
                }

                h1 {
                    font-size: 1.8rem !important;
                }

                .sc-home-intro {
                    margin-top: 26px;
                }

                .sc-subject-card {
                    padding: 18px;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )