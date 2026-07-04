"""Streamlit application entry point."""

import streamlit as st


st.set_page_config(
    page_title="CivicAI",
    page_icon="🏙️",
    layout="centered",
)

st.title("CivicAI")
st.write("Help improve your community by reporting a civic issue.")

st.file_uploader(
    "Upload an image of the issue",
    type=["jpg", "jpeg", "png"],
    help="Image analysis will be added in a future iteration.",
    disabled=True,
)

st.info("Issue reporting is being prepared. No image processing is active yet.")
