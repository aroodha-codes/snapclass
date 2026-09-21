from html import escape

import streamlit as st


def subject_card(
    name,
    code,
    section,
    stats=None,
    footer_callback=None,
):
    safe_name = escape(str(name))
    safe_code = escape(str(code))
    safe_section = escape(str(section))

    stats_html = ""

    if stats:
        items = []

        # Keep compatibility with existing (icon, label, value) tuples.
        for _, label, value in stats:
            safe_label = escape(str(label))
            safe_value = escape(str(value))

            items.append(
                '<div>'
                f'<div class="sc-stat-value">{safe_value}</div>'
                f'<div class="sc-stat-label">{safe_label}</div>'
                '</div>'
            )

        stats_html = (
            '<div class="sc-subject-stats">'
            + "".join(items)
            + "</div>"
        )

    html = (
        '<div class="sc-subject-card">'
        f'<div class="sc-subject-title">{safe_name}</div>'
        '<div class="sc-subject-meta">'
        f'<span class="sc-subject-code">{safe_code}</span>'
        f'<span>Section {safe_section}</span>'
        '</div>'
        f'{stats_html}'
        '</div>'
    )

    st.markdown(html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()