import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image, ImageOps

from src.pipelines.face_pipeline import (
    FACE_MATCH_THRESHOLD,
    get_trained_model,
    identify_faces,
)


@st.dialog("Face Identification")
def face_identification_dialog():
    st.write(
        "Upload a new photo to identify faces against the enrolled "
        "student database. This does not save attendance."
    )

    uploaded = st.file_uploader(
        "Choose a photo",
        type=["jpg", "jpeg", "png"],
        key="face_identification_upload",
    )

    if uploaded is None:
        return

    try:
        image = ImageOps.exif_transpose(
            Image.open(uploaded)
        ).convert("RGB")
    except Exception:
        st.error("Could not read this image. Please upload another photo.")
        return

    st.image(image, caption="Query photo", width="stretch")

    if st.button(
        "Identify Faces",
        type="primary",
        width="stretch",
    ):
        try:
            with st.spinner("Matching faces..."):
                # Use the latest enrollment data for this explicit test.
                get_trained_model.clear()

                if get_trained_model() is None:
                    st.warning(
                        "No enrolled face profiles are available. "
                        "Register a student first."
                    )
                    return

                results = identify_faces(np.asarray(image))
        except Exception:
            st.error(
                "Face identification failed. Check the image, "
                "database connection, and enrolled face profiles."
            )
            return

        if not results:
            st.warning(
                "No face detected. Try a clearer, front-facing photo."
            )
            return

        display_rows = []

        for result in results:
            display_rows.append({
                "Face": result["Face"],
                "Name": result["Name"],
                "Status": result["Status"],
                "Nearest Distance": (
                    round(result["Distance"], 4)
                    if result["Distance"] is not None
                    else "-"
                ),
            })

        st.dataframe(
            pd.DataFrame(display_rows),
            hide_index=True,
            width="stretch",
        )

        st.caption(
            f"Match threshold: {FACE_MATCH_THRESHOLD}. "
            "Lower distance means a closer match; it is not a "
            "confidence percentage. Faces are numbered left to right."
        )