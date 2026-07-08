"""
streamlit_app.py — Face Recognition Attendance System main entry point.

SIDEBAR TOGGLE:
  Pure session_state approach.
  - session_state.sidebar_open controls visibility.
  - Close: a [✕ Close] button at the TOP of the sidebar.
  - Open : a [☰ Menu] button at the TOP of the main content area when closed.
  - No st.columns inside sidebar (causes invisible-content bugs in Streamlit 1.50).
  - No floating-CSS tricks (unreliable across Streamlit versions).
"""

import streamlit as st

st.set_page_config(
    page_title="Face Recognition Attendance System",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Face Recognition Attendance System"},
)

from ui.styles import CSS
st.markdown(CSS, unsafe_allow_html=True)

import backend_api as api
from ui.pages import dashboard, recognition, register_user
from ui.pages import registered_users, attendance_page, settings, about


defaults = {
    "current_page": "Dashboard",
    "page_history":  [],
    "cam_active":    False,
    "sidebar_open":  True,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def _navigate(target: str):
    cur = st.session_state.current_page
    if cur == target:
        return
    if cur == "Recognition":
        st.session_state.cam_active = False
    st.session_state.page_history.append(cur)
    st.session_state.current_page = target
    st.rerun()

def _go_back():
    if st.session_state.page_history:
        prev = st.session_state.page_history.pop()
        if st.session_state.current_page == "Recognition":
            st.session_state.cam_active = False
        st.session_state.current_page = prev
        st.rerun()


NAV = [
    ("🏠", "Dashboard",        "Dashboard"),
    ("➕", "Register User",    "Register User"),
    ("🎯", "Recognition",      "Recognition"),
    ("👥", "Registered Users", "Registered Users"),
    ("📋", "Attendance",       "Attendance"),
    ("⚙️", "Settings",         "Settings"),
    ("ℹ️", "About",            "About"),
]





if st.session_state.sidebar_open:
    st.markdown("""<style>
    /* Force sidebar back on-screen — overrides Streamlit's native collapse transform */
    section[data-testid="stSidebar"] {
        transform: none !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        min-width: 260px !important;
        max-width: 260px !important;
        width: 260px !important;
    }
    </style>""", unsafe_allow_html=True)
else:
    st.markdown("""<style>
    section[data-testid="stSidebar"] { display: none !important; }
    </style>""", unsafe_allow_html=True)


with st.sidebar:


    st.markdown("""<div style="padding:1.2rem 1rem 1rem;
                               border-bottom:1px solid rgba(255,255,255,0.08);
                               display:flex;align-items:center;gap:0.6rem;">
        <div style="width:36px;height:36px;border-radius:9px;flex-shrink:0;
                    background:linear-gradient(135deg,#3B82F6,#7C3AED);
                    display:flex;align-items:center;justify-content:center;
                    font-size:1.1rem;">🎭</div>
        <div>
            <div style="font-size:0.85rem;font-weight:700;color:#F1F5F9;
                        letter-spacing:-0.01em;line-height:1.2;">Face Recognition</div>
            <div style="font-size:0.68rem;color:#64748B;margin-top:0.05rem;">
                Attendance System</div>
        </div>
    </div>""", unsafe_allow_html=True)


    if st.button("✕  Close Sidebar", key="sidebar_close", use_container_width=True):
        st.session_state.sidebar_open = False
        st.rerun()


    st.markdown("""<div style="font-size:0.62rem;font-weight:700;color:#475569;
                               text-transform:uppercase;letter-spacing:0.13em;
                               padding:0.6rem 1rem 0.3rem;">MAIN MENU</div>""",
                unsafe_allow_html=True)


    current = st.session_state.current_page
    for icon, label, page in NAV:
        if current == page:

            st.markdown(
                f'<div style="margin:0 0.5rem 2px;padding:0.6rem 0.85rem;'
                f'background:rgba(59,130,246,0.2);'
                f'border:1px solid rgba(59,130,246,0.35);'
                f'border-left:3px solid #3B82F6;border-radius:10px;'
                f'color:#60A5FA;font-weight:600;font-size:0.875rem;'
                f'display:flex;align-items:center;gap:0.6rem;">'
                f'<span>{icon}</span><span>{label}</span></div>',
                unsafe_allow_html=True,
            )
        else:
            if st.button(f"{icon}  {label}", key=f"nav_{page}", use_container_width=True):
                _navigate(page)


    cam_ok  = api.is_camera_available()
    cam_dot = "#22C55E" if cam_ok else "#EF4444"
    cam_lbl = "Online" if cam_ok else "Offline"

    st.markdown(
        '<div style="border-top:1px solid rgba(255,255,255,0.07);'
        'margin-top:0.5rem;padding:0.5rem 0 0.1rem;"></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-size:0.62rem;font-weight:700;color:#475569;'
        'text-transform:uppercase;letter-spacing:0.13em;'
        'margin:0 0 0.3rem;padding:0 0.5rem;">SYSTEM STATUS</p>',
        unsafe_allow_html=True,
    )

    def _row(icon, label, color):
        return (
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:0.18rem 0.5rem;font-size:0.75rem;color:#94A3B8;">'
            f'<span>{icon} {label}</span>'
            f'<span style="color:{color};font-weight:700;font-size:0.55rem;">⬤</span></div>'
        )

    st.markdown(
        _row("🧠", "AI Model",       "#22C55E") +
        _row("🗄️", "Database",       "#22C55E") +
        _row("📹", f"Camera ({cam_lbl})", cam_dot) +
        _row("📋", "Attendance DB",  "#22C55E"),
        unsafe_allow_html=True,
    )


    if st.session_state.page_history:
        prev = st.session_state.page_history[-1]
        st.markdown(
            '<div style="border-top:1px solid rgba(255,255,255,0.06);margin-top:0.4rem;'
            'padding-top:0.3rem;"></div>',
            unsafe_allow_html=True,
        )
        if st.button(f"← Back to {prev}", key="back_btn", use_container_width=True):
            _go_back()


    st.markdown("""<div style="border-top:1px solid rgba(255,255,255,0.07);
                               margin-top:0.6rem;padding:0.85rem 1rem;
                               display:flex;align-items:center;gap:0.6rem;">
        <div style="width:34px;height:34px;border-radius:50%;flex-shrink:0;
                    background:linear-gradient(135deg,#3B82F6,#7C3AED);
                    display:flex;align-items:center;justify-content:center;
                    font-size:0.75rem;font-weight:800;color:white;">A</div>
        <div>
            <div style="font-size:0.82rem;font-weight:700;color:#E2E8F0;">Admin</div>
            <div style="font-size:0.7rem;color:#64748B;">System Administrator</div>
            <div style="font-size:0.65rem;color:#22C55E;margin-top:0.1rem;">● Online</div>
        </div>
    </div>""", unsafe_allow_html=True)



if not st.session_state.sidebar_open:
    if st.button("☰  Open Menu", key="sidebar_open_btn"):
        st.session_state.sidebar_open = True
        st.rerun()
    st.divider()


page = st.session_state.current_page

if   page == "Dashboard":        dashboard.render()
elif page == "Recognition":       recognition.render()
elif page == "Register User":     register_user.render()
elif page == "Registered Users":  registered_users.render()
elif page == "Attendance":        attendance_page.render()
elif page == "Settings":          settings.render()
elif page == "About":             about.render()
