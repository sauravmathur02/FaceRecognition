"""ui/pages/settings.py — Settings page matching reference design."""

import os
import platform
import sqlite3
import sys
from datetime import datetime

import streamlit as st

import backend_api as api
from config import (
    ATTENDANCE_DB, CAMERA_ID, DB_NAME,
    IMAGE_FOLDER, LOG_LEVEL, MODEL_NAME, SIMILARITY_THRESHOLD,
)
from ui.components import topbar, sec_header, info_kv_table, kpi


def _db_size(path: str) -> str:
    try:
        return f"{os.path.getsize(path) / 1024:.1f} KB"
    except Exception:
        return "N/A"


def _db_row_count(db_path: str, table: str) -> int:
    try:
        conn   = sqlite3.connect(db_path)
        cur    = conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count  = cur.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


def render():
    st.markdown(topbar(
        "Settings",
        subtitle="Configure system preferences and parameters"
    ), unsafe_allow_html=True)

    cam_ok        = api.is_camera_available()
    faces_count   = api.get_user_count()
    att_count     = _db_row_count(ATTENDANCE_DB, "attendance")
    faces_size    = _db_size(DB_NAME)
    att_size      = _db_size(ATTENDANCE_DB)
    uptime        = datetime.now().strftime("%d %b %Y")


    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown("""
        <div class="stg-card">
            <div class="stg-card-hdr">
                <span class="stg-icon">⚙️</span>
                <div>
                    <div class="stg-title">General Settings</div>
                    <div class="stg-subtitle">Configure general system preferences</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div style="color:#475569;font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.4rem;">System Name</div>', unsafe_allow_html=True)
            st.markdown('<div style="background:rgba(10,15,28,0.6);border:1px solid rgba(255,255,255,0.06);border-radius:8px;padding:0.5rem 0.75rem;font-size:0.85rem;color:#94A3B8;margin-bottom:0.75rem;">Face Recognition Attendance System</div>', unsafe_allow_html=True)
            st.markdown(info_kv_table([
                ("Log Level",  LOG_LEVEL),
                ("Image Dir",  IMAGE_FOLDER),
                ("Python",     sys.version.split()[0]),
                ("Platform",   platform.system()),
            ]), unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.7rem;color:#1E293B;margin-top:0.75rem;">Edit config.py to change these values and restart the app.</div>', unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="stg-card">
            <div class="stg-card-hdr">
                <span class="stg-icon">🧠</span>
                <div>
                    <div class="stg-title">Recognition Settings</div>
                    <div class="stg-subtitle">Configure face recognition parameters</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.container(border=True):

            st.markdown(f"""
            <div style="margin-bottom:1rem;">
                <div style="display:flex;justify-content:space-between;font-size:0.72rem;color:#475569;margin-bottom:0.4rem;">
                    <span>Similarity Threshold</span>
                    <span style="color:#3B82F6;font-weight:700;">{SIMILARITY_THRESHOLD}%</span>
                </div>
                <div class="thresh-bar-track">
                    <div class="thresh-bar-fill" style="width:{SIMILARITY_THRESHOLD}%;"></div>
                </div>
                <div style="font-size:0.68rem;color:#1E293B;margin-top:0.3rem;">
                    Minimum similarity required to recognize a face.
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(info_kv_table([
                ("Model",         MODEL_NAME),
                ("Matching",      "Cosine similarity"),
                ("Embedding",     "512-D float32"),
                ("Strategy",      "Average + L2-normalize"),
                ("Attendance",    "Once per calendar day"),
                ("Detection",     "InsightFace buffalo_l"),
            ]), unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="stg-card">
            <div class="stg-card-hdr">
                <span class="stg-icon">📹</span>
                <div>
                    <div class="stg-title">Camera Settings</div>
                    <div class="stg-subtitle">Configure camera and capture settings</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(info_kv_table([
                ("Camera Source", f"Default Camera ({CAMERA_ID})"),
                ("Backend",       "OpenCV VideoCapture"),
                ("Status",        f'🟢 Online' if cam_ok else '🔴 Offline'),
                ("Frame Rate",    "~8 fps (Streamlit limit)"),
                ("Image Quality", "Original resolution"),
                ("Auto Exposure", "Enabled (hardware)"),
            ]), unsafe_allow_html=True)
            if cam_ok:
                st.success("📹 Camera is connected and available.")
            else:
                st.error(f"❌ Camera (ID={CAMERA_ID}) not found. Check config.py → CAMERA_ID.")

    st.markdown("<br>", unsafe_allow_html=True)


    d1, d2, d3 = st.columns(3, gap="medium")

    with d1:
        st.markdown("""
        <div class="stg-card">
            <div class="stg-card-hdr">
                <span class="stg-icon">🗄️</span>
                <div>
                    <div class="stg-title">Database Settings</div>
                    <div class="stg-subtitle">Configure database connections</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.container(border=True):

            db1, db2 = st.columns([3, 1])
            db1.markdown(f"""
            <div style="font-size:0.8rem;">
                <div style="font-weight:600;color:#CBD5E1;">Users Database</div>
                <div style="font-size:0.72rem;color:#334155;">{DB_NAME}</div>
            </div>
            """, unsafe_allow_html=True)
            db2.markdown('<span class="bdg bdg-green">Connected</span>', unsafe_allow_html=True)

            st.divider()


            adb1, adb2 = st.columns([3, 1])
            adb1.markdown(f"""
            <div style="font-size:0.8rem;">
                <div style="font-weight:600;color:#CBD5E1;">Attendance Database</div>
                <div style="font-size:0.72rem;color:#334155;">{ATTENDANCE_DB}</div>
            </div>
            """, unsafe_allow_html=True)
            adb2.markdown('<span class="bdg bdg-green">Connected</span>', unsafe_allow_html=True)

            st.divider()
            st.markdown(info_kv_table([
                ("Engine",       "SQLite 3"),
                ("Users",        f"{faces_count} records · {faces_size}"),
                ("Attendance",   f"{att_count} records · {att_size}"),
            ]), unsafe_allow_html=True)

    with d2:
        st.markdown("""
        <div class="stg-card">
            <div class="stg-card-hdr">
                <span class="stg-icon">ℹ️</span>
                <div>
                    <div class="stg-title">System Information</div>
                    <div class="stg-subtitle">View system status and information</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(info_kv_table([
                ("AI Model",            f'InsightFace (Buffalo_L)'),
                ("Model Status",        '<span class="bdg bdg-green">Loaded</span>'),
                ("Model Version",       "1.0"),
                ("Total Registered",    str(faces_count)),
                ("Total Attendance",    str(att_count)),
                ("System Date",         uptime),
                ("App Version",         "v2.0.0"),
                ("Programming",         f"Python {sys.version.split()[0]}"),
                ("Frameworks",          "Streamlit, InsightFace, OpenCV"),
                ("Database",            "SQLite"),
            ]), unsafe_allow_html=True)

    with d3:
        st.markdown("""
        <div class="stg-card">
            <div class="stg-card-hdr">
                <span class="stg-icon">🗃️</span>
                <div>
                    <div class="stg-title">Data Management</div>
                    <div class="stg-subtitle">Manage system data and records</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.container(border=True):

            st.markdown("""
            <div style="display:flex;align-items:center;gap:0.625rem;padding:0.5rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">
                <span style="font-size:1.1rem;">☁️</span>
                <div>
                    <div style="font-size:0.82rem;font-weight:600;color:#CBD5E1;">Backup All Data</div>
                    <div style="font-size:0.7rem;color:#334155;">Export users and attendance databases</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="display:flex;align-items:center;gap:0.625rem;padding:0.5rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">
                <span style="font-size:1.1rem;">📤</span>
                <div>
                    <div style="font-size:0.82rem;font-weight:600;color:#CBD5E1;">Export All Users</div>
                    <div style="font-size:0.7rem;color:#334155;">Export registered users to CSV</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("📋 Export Users CSV", use_container_width=True, type="secondary"):
                users = api.get_all_users()
                import pandas as pd, io as _io
                buf = _io.StringIO()
                pd.DataFrame(users, columns=["ID", "Name"]).to_csv(buf, index=False)
                st.download_button("⬇ Download", buf.getvalue().encode(), "users.csv", "text/csv", use_container_width=True)

            st.divider()


            st.markdown("""
            <div style="display:flex;align-items:center;gap:0.625rem;padding:0.4rem 0;">
                <span style="font-size:1.1rem;">🗑️</span>
                <div>
                    <div style="font-size:0.82rem;font-weight:600;color:#EF4444;">Reset All Data</div>
                    <div style="font-size:0.7rem;color:#7F1D1D;">⚠️ This action cannot be undone</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("⚠️ Clear All Attendance"):
                confirm = st.text_input("Type DELETE ALL:", placeholder="DELETE ALL", key="settings_clear")
                if st.button("🗑 Clear All Attendance", type="secondary", use_container_width=True):
                    if confirm.strip() == "DELETE ALL":
                        n = api.clear_all_attendance()
                        st.success(f"Cleared {n} records.")
                    else:
                        st.error("Type 'DELETE ALL' exactly.")
