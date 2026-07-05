"""Streamlit frontend for CivicAI image analysis."""

import html
import math
import os
from textwrap import dedent
from typing import Any

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
ANALYZE_URL = f"{API_BASE_URL}/analyze"


def analyze_image(
    image_bytes: bytes,
    filename: str,
    content_type: str,
    full_name: str,
    contact_number: str,
    location: str,
) -> dict[str, Any]:
    """Send an image to the CivicAI API and return its analysis."""
    try:
        response = requests.post(
            ANALYZE_URL,
            files={"image": (filename, image_bytes, content_type)},
            data={
                "full_name": full_name,
                "contact_number": contact_number,
                "location": location,
            },
            timeout=(5, 120),
        )
    except requests.ConnectionError as exc:
        raise RuntimeError(
            "CivicAI cannot reach the analysis service. Please try again shortly."
        ) from exc
    except requests.Timeout as exc:
        raise RuntimeError(
            "The analysis took too long. Please try again with a smaller image."
        ) from exc
    except requests.RequestException as exc:
        raise RuntimeError(
            "Something went wrong while sending the image. Please try again."
        ) from exc

    if response.status_code == 400:
        try:
            detail = response.json().get("detail")
        except (AttributeError, ValueError):
            detail = None
        raise ValueError(detail or "Please upload a valid JPEG or PNG image.")

    if response.status_code >= 500:
        raise RuntimeError(
            "The analysis service is temporarily unavailable. Please try again."
        )

    try:
        result = response.json()

        analysis = result["image_analysis"]
        department = result["department"]
        complaint = result["complaint"]
        citizen = result["citizen_details"]
        issue_type = analysis["issue_type"]
        description = analysis["description"]
        confidence = float(analysis["confidence"])
    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        raise RuntimeError(
            "The analysis service returned an unexpected response."
        ) from exc

    if not isinstance(issue_type, str) or not isinstance(description, str):
        raise RuntimeError("The analysis service returned an unexpected response.")
    if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
        raise RuntimeError("The analysis service returned an unexpected response.")

    return {
        "citizen": citizen,
        "analysis": analysis,
        "department": department,
        "complaint": complaint,
    }


st.set_page_config(
    page_title="CivicAI",
    page_icon="🏙️",
    layout="centered",
)

st.html(
    dedent(
        """
    <style>
        html, body, [class*="st-"] {
            font-family: "Avenir Next", "Inter", "Segoe UI", sans-serif;
        }
        /* Make Streamlit's header blend with the page background */
        header[data-testid="stHeader"] {
            background: rgba(248, 251, 255, 0.85) !important;
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(99, 102, 241, 0.08);
        }
        .stApp {
            background:
                radial-gradient(circle at 8% 5%, rgba(56, 189, 248, 0.22), transparent 26rem),
                radial-gradient(circle at 92% 8%, rgba(167, 139, 250, 0.24), transparent 24rem),
                linear-gradient(180deg, #f8fbff 0%, #f8fafc 55%, #eef2ff 100%);
        }
        .block-container {
            max-width: 820px;
            padding-top: 3.5rem;
            padding-bottom: 5rem;
        }
        .brand-row {
            align-items: center;
            display: flex;
            gap: 0.65rem;
            margin-bottom: 2rem;
            margin-top: 0.5rem;
        }
        .brand-mark {
            align-items: center;
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            border-radius: 0.8rem;
            box-shadow: 0 8px 22px rgba(79, 70, 229, 0.25);
            color: white;
            display: inline-flex;
            font-size: 1.15rem;
            height: 2.5rem;
            justify-content: center;
            width: 2.5rem;
        }
        .brand-name {
            color: #172554;
            font-size: 1.08rem;
            font-weight: 800;
            letter-spacing: -0.02em;
        }
        .civic-eyebrow {
            color: #4f46e5;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            margin-bottom: 0.75rem;
            text-transform: uppercase;
        }
        .civic-title {
            color: #0f172a !important;
            font-size: clamp(2.55rem, 7vw, 4.35rem);
            font-weight: 850;
            letter-spacing: -0.055em;
            line-height: 0.98;
            margin: 0;
        }
        .title-accent {
            background: linear-gradient(90deg, #2563eb, #7c3aed 62%, #db2777);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent !important;
        }
        .civic-subtitle {
            color: #64748b;
            font-size: 1.08rem;
            line-height: 1.7;
            margin: 1.2rem 0 2.4rem;
            max-width: 39rem;
        }
        .upload-heading {
            color: #1e293b;
            font-size: 1.05rem;
            font-weight: 750;
            margin: 0 0 0.25rem;
        }
        .upload-hint {
            color: #94a3b8;
            font-size: 0.88rem;
            margin: 0 0 0.85rem;
        }
        [data-testid="stTextInput"] input {
            background: rgba(255, 255, 255, 0.92);
            border-color: #cbd5e1;
            border-radius: 0.75rem;
            color: #0f172a;
        }
        [data-testid="stTextInput"] input:focus {
            border-color: #6366f1;
            box-shadow: 0 0 0 1px #6366f1;
        }
        [data-testid="stTextInput"] label {
            color: #334155;
            font-weight: 700;
        }
        [data-testid="stFileUploader"] {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(99, 102, 241, 0.18);
            border-radius: 1.15rem;
            box-shadow: 0 14px 38px rgba(71, 85, 105, 0.08);
            padding: 0.55rem;
        }
        [data-testid="stFileUploaderDropzone"] {
            background: linear-gradient(135deg, #f8fbff, #faf5ff);
            border: 1.5px dashed #a5b4fc;
            border-radius: 0.9rem;
            align-items: center;
            justify-content: center;
        }
        [data-testid="stFileUploaderDropzone"] p,
        [data-testid="stFileUploaderDropzone"] small {
            display: none !important;
        }
        [data-testid="stImage"] img {
            border: 3px solid rgba(255, 255, 255, 0.9);
            border-radius: 1.2rem;
            box-shadow: 0 16px 40px rgba(30, 41, 59, 0.13);
            margin-top: 0.5rem;
        }
        /* Improve contrast for image captions, spinner text, and uploader icons */
        [data-testid="stImage"] figcaption,
        [data-testid="stImage"] .stCaption,
        .stImageCaption {
            color: #0f172a !important;
        }
        [data-testid="stImage"] {
            color: #0f172a;
        }
        .stSpinner,
        .stSpinner *,
        [data-testid="stSpinner"],
        [data-testid="stProgress"] {
            color: #0f172a !important;
        }
        [data-testid="stFileUploader"] svg {
            fill: #0f172a !important;
        }
        [data-testid="stFileUploader"] {
            color: #0f172a !important;
        }
        [data-testid="stFileUploaderDropzone"] button {
            background: #ffffff !important;
            border-color: #94a3b8 !important;
            color: #0f172a !important;
            min-width: 8rem;
            padding: 0.55rem 1rem;
            white-space: nowrap;
        }
        [data-testid="stFileUploaderDropzone"] button * {
            color: #0f172a !important;
            white-space: nowrap;
        }
        [data-testid="stFileUploaderDropzone"] button:hover {
            background: #eef2ff !important;
            border-color: #6366f1 !important;
            color: #0f172a !important;
        }
        .result-card {
            background:
                linear-gradient(#ffffff, #ffffff) padding-box,
                linear-gradient(135deg, #60a5fa, #8b5cf6, #ec4899) border-box;
            border: 1.5px solid transparent;
            border-radius: 1.25rem;
            box-shadow: 0 20px 50px rgba(67, 56, 202, 0.12);
            margin-top: 1.5rem;
            overflow: hidden;
            padding: 1.65rem;
        }
        .result-topline {
            align-items: center;
            display: flex;
            justify-content: space-between;
            margin-bottom: 1.5rem;
        }
        .result-heading {
            color: #172554;
            font-size: 1.25rem;
            font-weight: 800;
            letter-spacing: -0.025em;
        }
        .result-badge {
            background: #dcfce7;
            border: 1px solid #bbf7d0;
            border-radius: 999px;
            color: #15803d;
            font-size: 0.75rem;
            font-weight: 800;
            padding: 0.38rem 0.7rem;
        }
        .result-label {
            color: #6366f1;
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }
        .result-value {
            color: #0f172a;
            font-size: 1.65rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            margin: 0.2rem 0 1.25rem;
        }
        .result-description {
            color: #334155;
            font-size: 1rem;
            line-height: 1.7;
            margin: 0.3rem 0 1.5rem;
        }
        .citizen-details {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 1rem;
            display: grid;
            gap: 0.85rem 1.25rem;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            margin-bottom: 1.5rem;
            padding: 1rem 1.1rem;
        }
        .citizen-details .detail-location {
            grid-column: 1 / -1;
        }
        .detail-label {
            color: #64748b;
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .detail-value {
            color: #1e293b;
            font-size: 0.92rem;
            font-weight: 650;
            margin-top: 0.18rem;
            overflow-wrap: anywhere;
        }
        .confidence-box {
            background: linear-gradient(135deg, #eef2ff, #faf5ff);
            border: 1px solid #e0e7ff;
            border-radius: 1rem;
            padding: 1rem 1.1rem;
        }
        .confidence-row {
            align-items: center;
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.7rem;
        }
        .confidence-label {
            color: #4338ca;
            font-size: 0.85rem;
            font-weight: 750;
        }
        .confidence-value {
            background: linear-gradient(90deg, #2563eb, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.65rem;
            font-weight: 900;
            letter-spacing: -0.04em;
        }
        .confidence-track {
            background: #ddd6fe;
            border-radius: 999px;
            height: 0.65rem;
            overflow: hidden;
        }
        .confidence-fill {
            background: linear-gradient(90deg, #38bdf8, #6366f1, #a855f7);
            border-radius: inherit;
            box-shadow: 0 0 14px rgba(99, 102, 241, 0.45);
            height: 100%;
        }
        .section-heading {
            align-items: center;
            color: #172554;
            display: flex;
            font-size: 1.15rem;
            font-weight: 800;
            gap: 0.55rem;
            letter-spacing: -0.02em;
            margin: 2.25rem 0 0.9rem;
        }
        .section-heading .section-icon {
            font-size: 1.3rem;
        }
        .dept-card {
            background: linear-gradient(135deg, #eff6ff, #eef2ff);
            border: 1px solid #dbeafe;
            border-radius: 1.15rem;
            box-shadow: 0 14px 34px rgba(59, 130, 246, 0.1);
            padding: 1.25rem 1.35rem;
        }
        .dept-row {
            align-items: baseline;
            display: flex;
            gap: 0.5rem;
        }
        .dept-row + .dept-row {
            margin-top: 0.65rem;
        }
        .dept-key {
            color: #1e3a8a;
            font-size: 0.82rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            min-width: 5.5rem;
            text-transform: uppercase;
        }
        .dept-val {
            color: #1e293b;
            font-size: 0.98rem;
            font-weight: 600;
            overflow-wrap: anywhere;
        }
        .dept-val a {
            color: #2563eb;
            font-weight: 700;
            text-decoration: none;
        }
        .dept-val a:hover {
            text-decoration: underline;
        }
        .complaint-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 1.15rem;
            box-shadow: 0 16px 40px rgba(30, 41, 59, 0.08);
            overflow: hidden;
        }
        .complaint-head {
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: #ffffff;
            padding: 1.15rem 1.35rem;
        }
        .complaint-title {
            font-size: 1.15rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            margin: 0;
        }
        .complaint-subject {
            color: rgba(255, 255, 255, 0.88);
            font-size: 0.88rem;
            margin-top: 0.3rem;
        }
        .complaint-body {
            color: #334155;
            font-size: 0.98rem;
            line-height: 1.75;
            padding: 1.25rem 1.35rem;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
        }
        .stButton > button {
            background: linear-gradient(90deg, #2563eb, #6d28d9);
            border: 0;
            border-radius: 0.9rem;
            box-shadow: 0 10px 24px rgba(79, 70, 229, 0.24);
            color: white;
            font-size: 1rem;
            font-weight: 750;
            min-height: 3.25rem;
            transition: transform 150ms ease, box-shadow 150ms ease;
        }
        .stButton > button:hover {
            box-shadow: 0 14px 30px rgba(79, 70, 229, 0.32);
            color: white;
            transform: translateY(-1px);
        }
        .stButton > button:disabled {
            background: #cbd5e1;
            box-shadow: none;
            color: #f8fafc;
        }
        @media (max-width: 640px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1.5rem;
            }
            .brand-row {
                margin-bottom: 2rem;
            }
            .result-card {
                padding: 1.25rem;
            }
            .citizen-details {
                grid-template-columns: 1fr;
            }
            .citizen-details .detail-location {
                grid-column: auto;
            }
        }
    </style>
    """
    )
)

st.html(
    dedent(
        """
    <div class="brand-row">
        <div class="brand-mark">◈</div>
        <div class="brand-name">CivicAI</div>
    </div>
    <div class="civic-eyebrow">Community reporting, made simple</div>
    <h1 class="civic-title">
        See a problem?<br><span class="title-accent">Let CivicAI spot it.</span>
    </h1>
    <p class="civic-subtitle">
        Turn a photo into a clear civic issue report. Upload an image and get
        an instant, AI-powered assessment in seconds.
    </p>
    <div class="upload-heading">Your details</div>
    <div class="upload-hint">Tell us who is reporting the issue</div>
    """
    )
)

name_column, contact_column = st.columns(2)
with name_column:
    full_name = st.text_input(
        "Full Name *",
        placeholder="Enter your full name",
    )
with contact_column:
    contact_number = st.text_input(
        "Contact Number *",
        placeholder="Enter your contact number",
    )

location = st.text_input(
    "Location *",
    placeholder="Street, landmark, or neighborhood",
)

st.html(
    dedent(
        """
    <div class="upload-heading">Upload your photo</div>
    <div class="upload-hint">JPEG or PNG · Choose a clear, well-lit image</div>
    """
    )
)

uploaded_image = st.file_uploader(
    "Upload a civic issue image",
    type=["jpg", "jpeg", "png"],
    help="Choose a clear JPEG or PNG image.",
    label_visibility="collapsed",
)

if uploaded_image is not None:
    upload_identity = f"{uploaded_image.name}:{uploaded_image.size}"
    if st.session_state.get("upload_identity") != upload_identity:
        st.session_state.upload_identity = upload_identity
        st.session_state.analysis = None
        st.session_state.submitted_details = None

    st.image(
        uploaded_image,
        caption="Uploaded image",
        use_container_width=True,
    )
elif st.session_state.get("upload_identity") is not None:
    st.session_state.pop("upload_identity", None)
    st.session_state.analysis = None
    st.session_state.submitted_details = None

analyze_clicked = st.button(
    "Analyze Image",
    type="primary",
    use_container_width=True,
    disabled=(
        uploaded_image is None
        or not full_name.strip()
        or not contact_number.strip()
        or not location.strip()
    ),
)

if analyze_clicked and uploaded_image is not None:
    citizen_details = {
        "full_name": full_name.strip(),
        "contact_number": contact_number.strip(),
        "location": location.strip(),
    }
    with st.spinner("Looking closely at the image…"):
        try:
            st.session_state.analysis = analyze_image(
                image_bytes=uploaded_image.getvalue(),
                filename=uploaded_image.name,
                content_type=uploaded_image.type or "application/octet-stream",
                **citizen_details,
            )
            st.session_state.submitted_details = citizen_details
            st.session_state.email_sent = False
        except ValueError as exc:
            st.session_state.analysis = None
            st.session_state.submitted_details = None
            st.warning(str(exc), icon="⚠️")
        except RuntimeError as exc:
            st.session_state.analysis = None
            st.session_state.submitted_details = None
            st.error(str(exc), icon="🛠️")

result = st.session_state.get("analysis")

if result is not None:

    citizen = result["citizen"]
    analysis = result["analysis"]
    department = result["department"]
    complaint = result["complaint"]

    confidence = analysis["confidence"]
    confidence_percentage = confidence * 100

    issue_type = html.escape(analysis["issue_type"])
    description = html.escape(analysis["description"])

    submitted_name = html.escape(citizen["full_name"])
    submitted_contact = html.escape(citizen["contact_number"])
    submitted_location = html.escape(citizen["location"])

    department_name = html.escape(department["department_name"])
    department_email = html.escape(department["email"])

    complaint_title = html.escape(complaint["title"])
    complaint_subject = html.escape(complaint["subject"])
    complaint_body = complaint["body"]

    st.html(
        dedent(
            f"""
        <div class="result-card">
            <div class="result-topline">
                <div class="result-heading">Analysis Complete</div>
                <div class="result-badge">✓ Ready</div>
            </div>

            <div class="result-label">Citizen Details</div>

            <div class="citizen-details">
                <div>
                    <div class="detail-label">Full Name</div>
                    <div class="detail-value">{submitted_name}</div>
                </div>

                <div>
                    <div class="detail-label">Contact Number</div>
                    <div class="detail-value">{submitted_contact}</div>
                </div>

                <div class="detail-location">
                    <div class="detail-label">Location</div>
                    <div class="detail-value">{submitted_location}</div>
                </div>
            </div>

            <div class="result-label">Detected Issue</div>

            <div class="result-value">
                {issue_type}
            </div>

            <div class="result-label">Description</div>

            <p class="result-description">
                {description}
            </p>

            <div class="confidence-box">
                <div class="confidence-row">
                    <div class="confidence-label">
                        AI Confidence
                    </div>

                    <div class="confidence-value">
                        {confidence_percentage:.0f}%
                    </div>
                </div>

                <div class="confidence-track">
                    <div class="confidence-fill"
                         style="width:{confidence_percentage:.1f}%">
                    </div>
                </div>
            </div>
        </div>
        """
        )
    )

    st.html(
        dedent(
            f"""
        <div class="section-heading">
            <span class="section-icon">🏢</span> Responsible Department
        </div>
        <div class="dept-card">
            <div class="dept-row">
                <div class="dept-key">Department</div>
                <div class="dept-val">{department_name}</div>
            </div>
            <div class="dept-row">
                <div class="dept-key">Email</div>
                <div class="dept-val">
                    <a href="mailto:{department_email}">{department_email}</a>
                </div>
            </div>
        </div>
        """
        )
    )

    send_col, _ = st.columns([1, 2])
    with send_col:
        if st.button(
            "📧 Send Report by Email",
            key="send_email",
            use_container_width=True,
        ):
            st.session_state.email_sent = True

    if st.session_state.get("email_sent"):
        st.success(
            "Thank you for your submission! Your report has been forwarded "
            f"to {department['department_name']}. They will be in touch shortly.",
            icon="✅",
        )

    st.html(
        dedent(
            f"""
        <div class="section-heading">
            <span class="section-icon">📝</span> Generated Complaint
        </div>
        <div class="complaint-card">
            <div class="complaint-head">
                <p class="complaint-title">{complaint_title}</p>
                <div class="complaint-subject">Subject: {complaint_subject}</div>
            </div>
            <div class="complaint-body">{html.escape(complaint_body)}</div>
        </div>
        """
        )
    )
