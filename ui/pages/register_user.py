"""ui/pages/register_user.py — User registration page."""

import io
import os

import cv2
import numpy as np
import streamlit as st
from PIL import Image

import backend_api as api
from ui.components import topbar, sec_header, kpi, info_kv_table


def _pil_to_bgr(pil_img) -> np.ndarray:
    return cv2.cvtColor(np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2BGR)


def _init():
    defaults = {
        "reg_images": [],
        "reg_result": None,
        "existing_images": [],
        "reg_delete_paths": [],
        "last_person_name": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render():
    _init()

    st.markdown(topbar(
        "Register User",
        subtitle="Add a new person or update an existing face profile"
    ), unsafe_allow_html=True)

    left_col, right_col = st.columns([2, 1], gap="large")

    with left_col:

        # ── Person name ────────────────────────────────────────────────────
        st.markdown(sec_header("Person Details"), unsafe_allow_html=True)
        with st.container(border=True):
            person_name = st.text_input(
                "Full Name",
                placeholder="e.g. John Doe",
                key="reg_name_input",
            )
            
            p_name = person_name.strip()
            if p_name != st.session_state.last_person_name:
                st.session_state.last_person_name = p_name
                st.session_state.existing_images = api.get_registration_images(p_name) if p_name else []
                st.session_state.reg_delete_paths = []
                st.session_state.reg_images = []
                st.session_state.reg_result = None

            exists = False
            if p_name:
                exists = api.user_exists(p_name)
                if exists:
                    st.warning(f"⚠️ '{p_name}' already exists — you are in UPDATE mode.")
                else:
                    st.success(f"✅ New user — will be created.")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Existing Images ────────────────────────────────────────────────
        if exists and st.session_state.existing_images:
            st.markdown(sec_header("Existing Registration Images"), unsafe_allow_html=True)
            st.caption("Select poor-quality images to delete them from the database.")
            
            with st.container(border=True):
                cols = st.columns(4)
                for i, img_path in enumerate(st.session_state.existing_images):
                    col = cols[i % 4]
                    with col:
                        # Load and show
                        bgr = cv2.imread(img_path)
                        if bgr is not None:
                            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                            st.image(rgb, use_container_width=True)
                            is_deleted = img_path in st.session_state.reg_delete_paths
                            if st.checkbox("Delete", key=f"del_{i}", value=is_deleted):
                                if img_path not in st.session_state.reg_delete_paths:
                                    st.session_state.reg_delete_paths.append(img_path)
                            else:
                                if img_path in st.session_state.reg_delete_paths:
                                    st.session_state.reg_delete_paths.remove(img_path)

            st.markdown("<br>", unsafe_allow_html=True)

        # ── Image Source ───────────────────────────────────────────────────
        st.markdown(sec_header("Capture New Images"), unsafe_allow_html=True)

        tab_cam, tab_upload = st.tabs(["📸  Live Camera", "📁  Upload Files"])

        with tab_cam:
            st.caption("Take multiple shots from different angles for best accuracy.")
            snapshot = st.camera_input("Take photo", label_visibility="collapsed", key="cam_snap")

            btn_add, btn_clear = st.columns(2)
            with btn_add:
                if st.button("➕ Add to Batch", use_container_width=True, disabled=snapshot is None):
                    if snapshot:
                        img = Image.open(io.BytesIO(snapshot.getvalue()))
                        bgr_img = _pil_to_bgr(img)
                        # Validate before adding
                        is_valid, msg, _ = api.validate_face_image(bgr_img)
                        if is_valid:
                            st.session_state.reg_images.append(bgr_img)
                            st.success(f"Added image {len(st.session_state.reg_images)} to batch.")
                        else:
                            st.error(f"❌ Rejected: {msg}")

            with btn_clear:
                if st.button("🗑 Clear Batch", use_container_width=True, type="secondary"):
                    st.session_state.reg_images = []
                    st.session_state.reg_result = None
                    st.rerun()

        with tab_upload:
            st.caption("Upload clear face photos (.jpg / .png).")
            uploaded = st.file_uploader(
                "Choose images",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                label_visibility="collapsed",
                key="reg_upload",
            )
            if uploaded and st.button("📥 Load Uploaded Images", use_container_width=True):
                added = 0
                for f in uploaded:
                    bgr_img = _pil_to_bgr(Image.open(io.BytesIO(f.read())))
                    is_valid, msg, _ = api.validate_face_image(bgr_img)
                    if is_valid:
                        st.session_state.reg_images.append(bgr_img)
                        added += 1
                    else:
                        st.error(f"❌ Rejected '{f.name}': {msg}")
                if added > 0:
                    st.success(f"Loaded {added} valid image(s) into batch.")

        # ── Batch Preview ──────────────────────────────────────────────────
        if st.session_state.reg_images:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                sec_header("New Image Batch", badge=f"{len(st.session_state.reg_images)} captured"),
                unsafe_allow_html=True,
            )

            # Thumbnail row (up to 5)
            thumbs = st.columns(min(len(st.session_state.reg_images), 5))
            for i, (col, frame) in enumerate(zip(thumbs, st.session_state.reg_images[:5])):
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                col.image(rgb, use_container_width=True, caption=f"#{i+1}")

            if len(st.session_state.reg_images) > 5:
                st.caption(f"... and {len(st.session_state.reg_images) - 5} more image(s) in batch")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Register Button ────────────────────────────────────────────────
        existing_count = len(st.session_state.existing_images)
        delete_count = len(st.session_state.reg_delete_paths)
        new_count = len(st.session_state.reg_images)
        final_count = existing_count - delete_count + new_count
        
        can_register = bool(p_name) and final_count >= 3
        
        if final_count < 3 and p_name:
            st.warning(f"⚠️ You must have at least 3 valid images in total. Currently you will have {final_count}.")

        btn_text = "🚀  Update Face Profile" if exists else "🚀  Register New Face"
        if st.button(
            btn_text,
            use_container_width=True,
            disabled=not can_register,
        ):
            with st.spinner("Processing..."):
                success, msg = api.update_user_faces(
                    p_name, st.session_state.reg_images, st.session_state.reg_delete_paths
                )
            st.session_state.reg_result = (success, msg)
            if success:
                st.session_state.reg_images = []
                st.session_state.reg_delete_paths = []
                st.session_state.existing_images = api.get_registration_images(p_name)
                # Re-run after a small delay to clear the UI correctly or just show success
                # st.rerun() is better here to refresh the grid
                # But we want to show the success message first.
                # It will show because we set reg_result.

        # ── Result ─────────────────────────────────────────────────────────
        if st.session_state.reg_result:
            ok, msg = st.session_state.reg_result
            if ok:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")

    # ── Right: Tips + Stats ────────────────────────────────────────────────
    with right_col:
        st.markdown(sec_header("Photo Tips"), unsafe_allow_html=True)
        with st.container(border=True):
            tips = [
                ("📸 Images",    "3–15 photos recommended"),
                ("💡 Lighting",  "Even, bright light"),
                ("🔄 Angles",    "Vary head angles slightly"),
                ("😐 Expression","Natural, relaxed"),
                ("📏 Distance",  "Face fills ~40% of frame"),
                ("🚫 Avoid",     "Glasses, hats, blur"),
            ]
            st.markdown(info_kv_table(tips), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(sec_header("How It Works"), unsafe_allow_html=True)
        with st.container(border=True):
            steps = [
                "Images are validated (exactly 1 face, high confidence).",
                "Images are saved permanently to disk.",
                "InsightFace extracts a 512-D embedding from all images.",
                "All embeddings are averaged into one vector.",
                "The final vector is stored in **faces.db**.",
            ]
            for i, s in enumerate(steps, 1):
                st.markdown(
                    f'<div style="display:flex;gap:0.5rem;padding:0.35rem 0;font-size:0.8rem;color:#64748B;">'
                    f'<span style="color:#3B82F6;font-weight:700;flex-shrink:0;">{i}.</span>'
                    f'<span>{s}</span></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)
        total = api.get_user_count()
        st.markdown(kpi("👥", total, "Total Registered", sub="Across all users", color="blue"),
                    unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(kpi("📸", final_count if p_name else 0, "Valid Images",
                        sub="For current user", color="purple"),
                    unsafe_allow_html=True)
