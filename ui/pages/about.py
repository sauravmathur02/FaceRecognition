"""ui/pages/about.py — About page matching reference design."""

import sys
import streamlit as st
from ui.components import topbar, sec_header, info_kv_table
from config import MODEL_NAME, SIMILARITY_THRESHOLD


def render():
    st.markdown(topbar(
        "About",
        subtitle="Learn more about the system and technology"
    ), unsafe_allow_html=True)

    # ── Hero Banner ────────────────────────────────────────────────────────
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(13,19,33,0.95) 0%, rgba(10,14,26,0.95) 100%);
        border: 1px solid rgba(59,130,246,0.15);
        border-radius: 20px;
        padding: 2.5rem 3rem;
        margin-bottom: 2rem;
        display: flex; gap: 3rem; align-items: center;
    ">
        <div style="
            width: 160px; height: 160px; flex-shrink: 0;
            background: radial-gradient(ellipse at center, rgba(59,130,246,0.15) 0%, transparent 70%);
            border: 1px solid rgba(59,130,246,0.2);
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 5rem;
            box-shadow: 0 0 40px rgba(59,130,246,0.1);
        ">🎭</div>
        <div style="flex: 1;">
            <h2 style="font-size:1.75rem;font-weight:800;color:#FFFFFF;margin:0 0 1rem;letter-spacing:-0.02em;">
                Face Recognition Attendance System
            </h2>
            <p style="color:#475569;font-size:0.9rem;line-height:1.7;margin:0 0 1.5rem;">
                A smart, secure, and efficient attendance management solution using advanced
                face recognition technology. The system automates the process of marking
                attendance, reduces manual effort, and ensures accurate records.
            </p>
            <div style="display:flex;gap:2rem;">
                <div style="text-align:center;">
                    <div style="font-size:1.5rem;margin-bottom:0.25rem;">🎯</div>
                    <div style="font-size:0.72rem;color:#475569;font-weight:600;">Accurate<br>Face Recognition</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.5rem;margin-bottom:0.25rem;">🛡️</div>
                    <div style="font-size:0.72rem;color:#475569;font-weight:600;">Secure<br>Data Protection</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.5rem;margin-bottom:0.25rem;">⚡</div>
                    <div style="font-size:0.72rem;color:#475569;font-weight:600;">Real-time<br>Processing</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.5rem;margin-bottom:0.25rem;">📊</div>
                    <div style="font-size:0.72rem;color:#475569;font-weight:600;">Smart<br>Analytics</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 3-column Info Row ──────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown(sec_header("System Information"), unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(info_kv_table([
                ("Application Name", "Face Recognition Attendance System"),
                ("Version",          "v2.0.0"),
                ("Build Date",       "01 July 2026"),
                ("Developer",        "FaceID Pro Team"),
                ("License",          "Academic Use Only"),
                ("Platform",         "Streamlit Web Application"),
                ("Programming",      f"Python {sys.version.split()[0]}"),
                ("Frameworks",       "Streamlit, InsightFace, OpenCV"),
                ("Database",         "SQLite"),
            ]), unsafe_allow_html=True)

    with col2:
        st.markdown(sec_header("Technology Stack"), unsafe_allow_html=True)
        with st.container(border=True):
            tech = [
                ("🧠", "InsightFace",    "State-of-the-art face recognition model"),
                ("📷", "OpenCV",         "Image processing and computer vision"),
                ("🌊", "Streamlit",      "Interactive web application framework"),
                ("🗄️", "SQLite",         "Lightweight and reliable database"),
                ("🔢", "NumPy",          "Numerical operations and processing"),
                ("📊", "Pandas",         "Data manipulation and analysis"),
                ("📈", "Plotly",         "Interactive charts and graphs"),
                ("⚡", "ONNX Runtime",   "Neural network inference engine"),
            ]
            for icon, name, desc in tech:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:0.75rem;padding:0.45rem 0;
                            border-bottom:1px solid rgba(255,255,255,0.04);">
                    <span style="font-size:1rem;width:20px;text-align:center;">{icon}</span>
                    <div style="flex:1;">
                        <span style="font-size:0.82rem;font-weight:600;color:#CBD5E1;">{name}</span>
                        <span style="font-size:0.72rem;color:#334155;margin-left:0.5rem;">{desc}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with col3:
        st.markdown(sec_header("Key Features"), unsafe_allow_html=True)
        with st.container(border=True):
            features = [
                "Real-time face detection and recognition",
                "Multi-face detection and tracking",
                "Automatic attendance marking",
                "Attendance reports and analytics",
                "User management and registration",
                "Secure data storage (SQLite)",
                "Export to CSV / Excel",
                "Responsive and modern UI",
                f"89% similarity threshold",
                "Once-per-day attendance rule",
            ]
            for f in features:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:0.5rem;padding:0.35rem 0;
                            border-bottom:1px solid rgba(255,255,255,0.03);">
                    <span style="color:#22C55E;font-size:0.75rem;">✓</span>
                    <span style="font-size:0.8rem;color:#94A3B8;">{f}</span>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Recognition Workflow ───────────────────────────────────────────────
    st.markdown(sec_header("Recognition Workflow"), unsafe_allow_html=True)
    wf_cols = st.columns(5)
    workflow = [
        ("1", "Camera Frame",   "OpenCV captures a BGR frame from the webcam device."),
        ("2", "Face Detection", "InsightFace detects face bounding boxes in the frame."),
        ("3", "Embedding",      "A 512-D float32 vector is extracted per face."),
        ("4", "Matching",       "Cosine similarity vs all stored embeddings. Best match wins."),
        ("5", "Attendance",     f"If similarity ≥ {SIMILARITY_THRESHOLD}%, mark once per day."),
    ]
    for col, (num, title, desc) in zip(wf_cols, workflow):
        with col:
            st.markdown(f"""
            <div class="sc">
                <div class="sc-num">Step {num}</div>
                <div class="sc-title">{title}</div>
                <div class="sc-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Footer Row ─────────────────────────────────────────────────────────
    f1, f2, f3, f4 = st.columns(4)
    footer_sections = [
        ("🎯", "Our Mission",
         "To provide innovative and intelligent solutions that simplify attendance management using AI technology, ensuring accuracy, security, and efficiency."),
        ("✉️", "Contact Us",
         "faceidpro@example.com\n+00 00000 00000"),
        ("👥", "Developed By",
         "FaceID Pro Team\nAI Research & Development"),
        ("❤️", "Acknowledgement",
         "Thanks to the open-source community — InsightFace, OpenCV, Streamlit — for their amazing contributions."),
    ]
    for col, (icon, title, text) in zip([f1, f2, f3, f4], footer_sections):
        with col:
            with st.container(border=True):
                st.markdown(f"""
                <div style="margin-bottom:0.5rem;">
                    <span style="font-size:1.1rem;">{icon}</span>
                    <span style="font-size:0.85rem;font-weight:700;color:#E2E8F0;margin-left:0.4rem;">{title}</span>
                </div>
                <div style="font-size:0.78rem;color:#475569;line-height:1.6;white-space:pre-line;">{text}</div>
                """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1rem;
                border-top:1px solid rgba(255,255,255,0.04);margin-top:1.5rem;
                font-size:0.78rem;color:#1E293B;">
        © 2026 FaceID Pro · InsightFace buffalo_l · SQLite · OpenCV · Streamlit
    </div>
    """, unsafe_allow_html=True)
