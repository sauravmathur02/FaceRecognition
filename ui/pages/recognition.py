"""ui/pages/recognition.py — Live recognition page.

CAMERA DISPLAY FIX:
  The CORRECT pattern for Streamlit live video:
    1. Store the captured frame in st.session_state.current_frame_rgb
    2. Display it with st.image() at the TOP of the render cycle (in the column)
    3. The recognition loop updates session_state and calls st.rerun()

  Reason: st.empty() placeholders updated at the BOTTOM of the script are
  overwritten in the next rerun before the browser can render them.
  Storing in session_state means the image renders on every rerun naturally.
"""

import io
import time
from datetime import datetime

import cv2
from PIL import Image
import streamlit as st

import backend_api as api
from ui.components import (
    topbar, sec_header,
    recog_result_card, recog_history_item, info_kv_table
)
from config import SIMILARITY_THRESHOLD, MODEL_NAME


def _init():
    defaults = {
        "cam_active":          False,
        "current_frame_jpeg":  None,   # JPEG bytes — avoids MediaFileStorageError
        "recognition_history": [],
        "last_result":         None,
        "total_recognized":    0,
        "total_marked":        0,
        "session_start":       None,
        "frame_count":         0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render():
    _init()

    st.markdown(topbar(
        "Recognition",
        subtitle="Real-time face detection and automatic attendance marking"
    ), unsafe_allow_html=True)

    # ── 3-column layout ────────────────────────────────────────────────────
    left_col, center_col, right_col = st.columns([2.2, 1.8, 1.5], gap="large")

    # ── LEFT: Camera feed ─────────────────────────────────────────────────
    with left_col:
        st.markdown(sec_header("Live Camera"), unsafe_allow_html=True)

        # Controls
        ctrl1, ctrl2, ctrl3 = st.columns(3)
        with ctrl1:
            start_btn = st.button(
                "▶ Start", use_container_width=True,
                disabled=st.session_state.cam_active, key="recog_start",
            )
        with ctrl2:
            stop_btn = st.button(
                "⏹ Stop", use_container_width=True, type="secondary",
                disabled=not st.session_state.cam_active, key="recog_stop",
            )
        with ctrl3:
            clear_btn = st.button(
                "🗑 Clear", use_container_width=True, type="secondary",
                key="recog_clear",
            )

        if start_btn:
            if not api.open_camera():
                st.error("❌ Camera not available. Check CAMERA_ID in config.py.")
            else:
                st.session_state.cam_active          = True
                st.session_state.session_start       = datetime.now()
                st.session_state.frame_count         = 0
                st.session_state.current_frame_jpeg  = None
                st.rerun()

        if stop_btn:
            api.release_camera()
            st.session_state.cam_active         = False
            st.session_state.current_frame_jpeg = None
            st.rerun()

        if clear_btn:
            st.session_state.recognition_history = []
            st.session_state.total_recognized    = 0
            st.session_state.total_marked        = 0
            st.session_state.last_result         = None

        # ── Camera display ────────────────────────────────────────────────
        # Rendered HERE at the top so it's visible on every rerun
        if not st.session_state.cam_active:
            st.markdown("""
            <div style="background:rgba(10,15,28,0.6);
                        border:1px solid rgba(255,255,255,0.06);
                        border-radius:14px;padding:3rem 2rem;
                        text-align:center;
                        display:flex;flex-direction:column;
                        align-items:center;gap:0.75rem;margin-top:0.5rem;">
                <span style="font-size:2.5rem;">📹</span>
                <span style="font-size:0.9rem;font-weight:600;color:#64748B;">
                    Click ▶ Start to begin
                </span>
                <span style="font-size:0.75rem;color:#475569;">
                    Recognition starts automatically
                </span>
            </div>
            """, unsafe_allow_html=True)

        elif st.session_state.current_frame_jpeg is not None:
            # ✅ Show live frame as JPEG bytes (reliable, no MediaFileStorageError)
            st.image(
                st.session_state.current_frame_jpeg,
                width="stretch",
                caption=f"Frame #{st.session_state.frame_count}",
            )

        else:
            # Camera started but first frame not yet captured
            st.markdown("""
            <div style="background:rgba(10,15,28,0.7);
                        border:1px solid rgba(59,130,246,0.2);
                        border-radius:14px;height:220px;margin-top:0.5rem;
                        display:flex;flex-direction:column;
                        align-items:center;justify-content:center;gap:0.6rem;">
                <span style="font-size:1.5rem;">⏳</span>
                <span style="color:#64748B;font-size:0.85rem;font-weight:500;">
                    Opening camera…
                </span>
            </div>
            """, unsafe_allow_html=True)

        # Scanning badge
        if st.session_state.cam_active:
            st.markdown(
                '<div style="text-align:center;margin-top:0.4rem;">'
                '<span style="background:rgba(34,197,94,0.12);'
                'border:1px solid rgba(34,197,94,0.3);border-radius:100px;'
                'padding:0.2rem 0.75rem;font-size:0.72rem;font-weight:600;color:#22C55E;">'
                '⬤ SCANNING</span></div>',
                unsafe_allow_html=True,
            )

    # ── CENTER: Recognition result ──────────────────────────────────────────
    with center_col:
        st.markdown(sec_header("Recognition Result"), unsafe_allow_html=True)

        if not st.session_state.last_result:
            st.markdown("""
            <div style="background:rgba(10,15,28,0.6);
                        border:1px solid rgba(255,255,255,0.06);
                        border-radius:14px;padding:2.5rem 1rem;text-align:center;">
                <div style="font-size:3rem;margin-bottom:1rem;">🎭</div>
                <div style="font-size:0.9rem;font-weight:600;color:#64748B;">
                    Awaiting Detection
                </div>
                <div style="font-size:0.78rem;color:#475569;margin-top:0.5rem;">
                    Start the camera to begin
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            r = st.session_state.last_result
            st.markdown(
                recog_result_card(
                    r["name"], r["similarity"],
                    r["is_known"], r["time"], r["marked"]
                ),
                unsafe_allow_html=True,
            )

        # Session stats
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(sec_header("Session Stats"), unsafe_allow_html=True)
        with st.container(border=True):
            elapsed = "—"
            if st.session_state.session_start:
                secs    = int((datetime.now() - st.session_state.session_start).total_seconds())
                elapsed = f"{secs // 60:02d}:{secs % 60:02d}"
            st.markdown(info_kv_table([
                ("Status",       "🟢 Active" if st.session_state.cam_active else "⭕ Idle"),
                ("Frames",       str(st.session_state.frame_count)),
                ("Recognized",   str(st.session_state.total_recognized)),
                ("Marked Today", str(st.session_state.total_marked)),
                ("Session Time", elapsed),
            ]), unsafe_allow_html=True)

    # ── RIGHT: History + System Status ──────────────────────────────────────
    with right_col:
        history = st.session_state.recognition_history
        st.markdown(
            sec_header("Recognition Log", badge=str(len(history))),
            unsafe_allow_html=True,
        )

        if not history:
            st.markdown(
                '<div style="color:#475569;font-size:0.8rem;padding:0.5rem 0;">'
                'No recognitions yet.</div>',
                unsafe_allow_html=True,
            )
        else:
            html = ('<div style="background:rgba(13,19,33,0.8);'
                    'border:1px solid rgba(255,255,255,0.06);'
                    'border-radius:12px;padding:0.875rem 1rem;">')
            html += "".join(
                recog_history_item(r["name"], r["similarity"], r["time"])
                for r in history[:8]
            )
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(sec_header("System Status"), unsafe_allow_html=True)
        cam_ok = api.is_camera_available()
        with st.container(border=True):
            st.markdown(info_kv_table([
                ("Model",      MODEL_NAME),
                ("Threshold",  f"{SIMILARITY_THRESHOLD}%"),
                ("Camera",     "🟢 Online" if cam_ok else "🔴 Offline"),
                ("Database",   "🟢 Connected"),
                ("Attendance", "Once per day"),
            ]), unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # RECOGNITION LOOP — runs at the END of every render when camera is active
    # Updates session_state.current_frame_rgb then calls st.rerun()
    # On the NEXT render, the image at the TOP of left_col shows the new frame
    # ══════════════════════════════════════════════════════════════════════════
    if st.session_state.cam_active:
        frame = api.capture_single_frame()

        if frame is None:
            st.error("❌ Camera failed to grab frame.")
            api.release_camera()
            st.session_state.cam_active         = False
            st.session_state.current_frame_jpeg = None
        else:
            # Process frame through InsightFace
            try:
                annotated, results = api.recognize_faces_in_frame(frame)
                frame_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            except Exception:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results   = []

            # Encode as JPEG bytes — avoids Streamlit MediaFileStorageError
            # Using cv2.imencode is significantly faster than PIL
            try:
                # Need RGB to display correctly in Streamlit, so we use frame_rgb
                # Wait, cv2.imencode expects BGR by default, but since we already converted
                # to RGB (frame_rgb) for Streamlit, if we pass frame_rgb to imencode, 
                # it will treat it as BGR and the colors will be swapped. 
                # So we should pass 'annotated' (which is BGR) directly to imencode!
                success, buffer = cv2.imencode('.jpg', annotated if 'annotated' in locals() else frame)
                if success:
                    st.session_state.current_frame_jpeg = buffer.tobytes()
            except Exception:
                pass  # keep last good frame if encoding fails

            st.session_state.frame_count += 1

            # Process recognition results
            for r in results:
                is_known = r["recognized"]
                name     = r["name"]
                sim      = r["similarity"]
                ts       = datetime.now().strftime("%H:%M:%S")
                marked, _ = api.mark_attendance(name) if is_known else (False, "")

                entry = {
                    "name":       name,
                    "similarity": sim,
                    "is_known":   is_known,
                    "time":       ts,
                    "marked":     marked,
                }

                recent = [h["name"] for h in st.session_state.recognition_history[:3]]
                if name not in recent:
                    st.session_state.recognition_history.insert(0, entry)
                    st.session_state.total_recognized += 1
                    if marked:
                        st.session_state.total_marked += 1

                st.session_state.last_result = entry

        st.rerun()
