"""
ui/styles.py  –  Premium CSS for FaceID Pro Streamlit UI
All Streamlit overrides + custom HTML component classes.
Injected once per session via st.markdown(CSS, unsafe_allow_html=True).
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ══════════════════════════════════════════════════════════
   RESET & GLOBAL
══════════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #050816 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #FFFFFF !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header         { visibility: hidden !important; }
.stDeployButton                    { display: none !important; }
[data-testid="stToolbar"]          { display: none !important; }
[data-testid="stDecoration"]       { display: none !important; }
[data-testid="stStatusWidget"]     { display: none !important; }

/* Main container padding */
.main .block-container {
    padding: 1.5rem 2rem 3rem !important;
    max-width: 1500px !important;
}

/* ══════════════════════════════════════════════════════════
   SIDEBAR — beautiful styling + native toggle works
══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"],
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060b1a 0%, #091020 60%, #0a1228 100%) !important;
    border-right: 1px solid rgba(59,130,246,0.12) !important;
    min-width: 260px !important;
    max-width: 260px !important;
    width: 260px !important;
}
section[data-testid="stSidebar"] > div {
    min-width: 260px !important;
    width: 260px !important;
    background: transparent !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
[data-testid="stSidebarContent"]            { padding: 0 !important; }

/* Hide Streamlit's native << >> toggle (we use our own Python-based toggle) */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] { display: none !important; }

/* No radio navigation */
div[data-testid="stSidebarContent"] .stRadio [data-baseweb="radio"] { display: none !important; }


/* ══════════════════════════════════════════════════════════
   BORDERED CONTAINERS → GLASS CARDS
   Targets st.container(border=True)
══════════════════════════════════════════════════════════ */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(145deg, rgba(13,19,33,0.95) 0%, rgba(10,14,26,0.98) 100%) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.04) !important;
    overflow: visible !important;
}

/* ══════════════════════════════════════════════════════════
   SIDEBAR BUTTONS  (nav items + back button)
   These are the INACTIVE nav items rendered as st.button().
   Active nav item is rendered as HTML, not a button.
══════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #94A3B8 !important;
    border-radius: 10px !important;
    padding: 0.65rem 0.875rem !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    transition: all 0.15s ease !important;
    text-align: left !important;
    justify-content: flex-start !important;
    letter-spacing: 0.01em !important;
    width: 100% !important;
    transform: none !important;
    margin: 0 0 2px !important;
    line-height: 1.4 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(59,130,246,0.1) !important;
    border-color: rgba(59,130,246,0.15) !important;
    color: #E2E8F0 !important;
    transform: none !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton > button:active,
[data-testid="stSidebar"] .stButton > button:active {
    background: rgba(59,130,246,0.15) !important;
    transform: none !important;
}

/* Remove the padding that Streamlit adds around sidebar buttons */
section[data-testid="stSidebar"] [data-testid="stButton"] {
    padding: 0 0.75rem !important;
}


/* ══════════════════════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.25rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(59,130,246,0.25) !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
    box-shadow: 0 6px 20px rgba(59,130,246,0.4) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Secondary */
.stButton > button[kind="secondary"] {
    background: rgba(15,23,42,0.8) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #94A3B8 !important;
    box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(30,41,59,0.9) !important;
    border-color: rgba(255,255,255,0.14) !important;
    color: #E2E8F0 !important;
    box-shadow: none !important;
    transform: none !important;
}

/* Download button */
.stDownloadButton > button {
    background: rgba(59,130,246,0.1) !important;
    border: 1px solid rgba(59,130,246,0.25) !important;
    color: #60A5FA !important;
    box-shadow: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
}
.stDownloadButton > button:hover {
    background: rgba(59,130,246,0.18) !important;
    border-color: rgba(59,130,246,0.4) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ══════════════════════════════════════════════════════════
   INPUTS
══════════════════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stTimeInput > div > div > input {
    background: rgba(10,15,28,0.9) !important;
    border: 1px solid rgba(59,130,246,0.15) !important;
    border-radius: 10px !important;
    color: #E2E8F0 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.5rem 0.875rem !important;
    font-size: 0.875rem !important;
}
.stTextInput > div > div > input:focus { border-color: #3B82F6 !important; box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important; }

/* Selectbox */
.stSelectbox > div > div { background: rgba(10,15,28,0.9) !important; border: 1px solid rgba(59,130,246,0.15) !important; border-radius: 10px !important; }

/* Textarea */
.stTextArea > div > div > textarea { background: rgba(10,15,28,0.9) !important; border: 1px solid rgba(59,130,246,0.15) !important; border-radius: 10px !important; color: #E2E8F0 !important; }

/* Labels */
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stDateInput label, .stSlider label, .stTextArea label,
.stCheckbox label { color: #64748B !important; font-size: 0.75rem !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.07em !important; }

/* ══════════════════════════════════════════════════════════
   NATIVE METRICS
══════════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
    background: rgba(13,19,33,0.9) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    padding: 1.1rem 1.25rem !important;
}
[data-testid="stMetricValue"] { font-size: 1.9rem !important; font-weight: 800 !important; color: #FFFFFF !important; }
[data-testid="stMetricLabel"] { color: #475569 !important; font-size: 0.7rem !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; }
[data-testid="stMetricDelta"] { font-size: 0.78rem !important; font-weight: 600 !important; }

/* ══════════════════════════════════════════════════════════
   TABS
══════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(10,15,28,0.6) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 2px !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
}
.stTabs [data-baseweb="tab"] {
    color: #475569 !important; border-radius: 8px !important;
    font-weight: 500 !important; font-size: 0.85rem !important;
    padding: 0.4rem 1rem !important; border: none !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] { background: rgba(59,130,246,0.15) !important; color: #60A5FA !important; font-weight: 600 !important; }

/* ══════════════════════════════════════════════════════════
   DATAFRAME
══════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
}

/* ══════════════════════════════════════════════════════════
   EXPANDER
══════════════════════════════════════════════════════════ */
.stExpander {
    background: rgba(13,19,33,0.8) !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: 12px !important;
}
.stExpander summary { color: #94A3B8 !important; font-weight: 600 !important; }

/* Progress bar */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #3B82F6, #06B6D4) !important;
    border-radius: 10px !important;
}
.stProgress > div > div > div {
    background: rgba(10,15,28,0.8) !important; border-radius: 10px !important;
}

/* Alerts */
[data-testid="stAlert"] { border-radius: 10px !important; font-family: 'Inter', sans-serif !important; }

/* Divider */
hr { border: none !important; border-top: 1px solid rgba(255,255,255,0.04) !important; margin: 1.25rem 0 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.2); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(59,130,246,0.4); }

/* Camera input */
[data-testid="stCameraInput"] { border-radius: 14px !important; overflow: hidden !important; }

/* ══════════════════════════════════════════════════════════
   CUSTOM HTML COMPONENT CLASSES
   Used exclusively inside st.markdown(unsafe_allow_html=True).
   NEVER wrap Streamlit widgets inside these divs.
══════════════════════════════════════════════════════════ */

/* Top bar */
.topbar {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 0 0 1.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    margin-bottom: 2rem;
}
.topbar-left h1 {
    font-size: 1.85rem; font-weight: 800;
    color: #FFFFFF; letter-spacing: -0.03em;
    line-height: 1.1; margin: 0 0 0.25rem;
}
.topbar-left p { font-size: 0.85rem; color: #475569; margin: 0; }
.topbar-right { display: flex; flex-direction: column; align-items: flex-end; gap: 0.5rem; }
.topbar-breadcrumb { font-size: 0.75rem; color: #334155; }
.topbar-breadcrumb span { color: #3B82F6; }
.topbar-datetime {
    font-size: 0.78rem; color: #475569;
    background: rgba(10,15,28,0.6);
    border: 1px solid rgba(255,255,255,0.05);
    padding: 0.3rem 0.75rem; border-radius: 8px;
}

/* Sidebar logo */
.sb-logo {
    padding: 1.25rem 1.1rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    margin-bottom: 0.5rem;
    display: flex; align-items: center; gap: 0.6rem;
}
.sb-logo-icon {
    width: 34px; height: 34px; border-radius: 8px;
    background: linear-gradient(135deg, #3B82F6, #7C3AED);
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
}
.sb-logo-text { font-size: 0.8rem; font-weight: 700; color: #CBD5E1; line-height: 1.25; }
.sb-logo-text small { font-size: 0.65rem; color: #64748B; font-weight: 400; display: block; }

/* Sidebar section label */
.sb-section-label {
    font-size: 0.65rem; font-weight: 700; color: #475569;
    text-transform: uppercase; letter-spacing: 0.12em;
    padding: 0.75rem 1.1rem 0.4rem;
}

/* Sidebar system status */
.sb-status {
    border-top: 1px solid rgba(255,255,255,0.06);
    padding: 0.875rem 1.1rem 0.5rem;
    margin-top: 0.5rem;
}
.sb-status-title { font-size: 0.65rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 0.625rem; }
.sb-status-item { display: flex; align-items: center; justify-content: space-between; padding: 0.3rem 0; }
.sb-status-name { font-size: 0.75rem; color: #94A3B8; }
.sb-status-name small { display: block; font-size: 0.65rem; color: #64748B; }
.sb-status-dot { width: 7px; height: 7px; border-radius: 50%; }
.sb-dot-green  { background: #22C55E; box-shadow: 0 0 5px #22C55E55; }
.sb-dot-red    { background: #EF4444; }
.sb-dot-yellow { background: #F59E0B; }

/* Sidebar admin profile */
.sb-profile {
    border-top: 1px solid rgba(255,255,255,0.06);
    padding: 0.875rem 1.1rem;
    display: flex; align-items: center; gap: 0.625rem;
    background: rgba(5,8,22,0.4);
    margin-top: auto;
}
.sb-avatar {
    width: 34px; height: 34px; border-radius: 50%;
    background: linear-gradient(135deg, #3B82F6, #7C3AED);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 700; color: white; flex-shrink: 0;
}
.sb-profile-name { font-size: 0.8rem; font-weight: 700; color: #CBD5E1; }
.sb-profile-role { font-size: 0.68rem; color: #64748B; }
.sb-online { font-size: 0.65rem; color: #22C55E; margin-top: 0.1rem; }

/* ══════════════════════════════════════════════════════════
   TOP BAR  (page header inside each page)
══════════════════════════════════════════════════════════ */
.topbar {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 1.75rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.topbar-left h1 {
    font-size: 1.75rem;
    font-weight: 800;
    color: #F1F5F9;
    letter-spacing: -0.03em;
    margin: 0 0 0.2rem;
    line-height: 1.1;
}
.topbar-left p {
    font-size: 0.85rem;
    color: #475569;
    margin: 0;
}
.topbar-right { text-align: right; flex-shrink: 0; }
.topbar-breadcrumb {
    font-size: 0.72rem;
    color: #3B82F6;
    font-weight: 500;
    margin-bottom: 0.25rem;
}
.topbar-breadcrumb span { color: #334155; }
.topbar-datetime {
    font-size: 0.8rem;
    color: #475569;
    font-weight: 500;
}

/* KPI card */
.kpi {
    background: linear-gradient(145deg, rgba(13,19,33,0.97) 0%, rgba(10,14,26,0.97) 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.25rem 1.4rem;
    position: relative; overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    height: 100%;
}
.kpi::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    border-radius: 16px 16px 0 0;
}
.kpi.blue::before   { background: linear-gradient(90deg,#3B82F6,#06B6D4); }
.kpi.purple::before { background: linear-gradient(90deg,#7C3AED,#3B82F6); }
.kpi.green::before  { background: linear-gradient(90deg,#22C55E,#06B6D4); }
.kpi.orange::before { background: linear-gradient(90deg,#F59E0B,#EF4444); }
.kpi.cyan::before   { background: linear-gradient(90deg,#06B6D4,#3B82F6); }
.kpi.red::before    { background: linear-gradient(90deg,#EF4444,#F59E0B); }

.kpi-icon  { font-size: 1.4rem; margin-bottom: 0.625rem; display: block; }
.kpi-val   { font-size: 2.1rem; font-weight: 800; color: #F1F5F9; line-height: 1; letter-spacing: -0.03em; margin-bottom: 0.3rem; }
.kpi-label { font-size: 0.68rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.09em; margin-bottom: 0.35rem; }
.kpi-sub   { font-size: 0.78rem; color: #64748B; font-weight: 500; }
.kpi-sub.pos { color: #22C55E; }
.kpi-sub.neg { color: #EF4444; }
.kpi-sub.neu { color: #60A5FA; }

/* Section header */
.sec-hdr {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1rem; padding-bottom: 0.625rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.sec-hdr-title { font-size: 0.9rem; font-weight: 700; color: #E2E8F0; letter-spacing: -0.01em; }
.sec-hdr-badge {
    font-size: 0.65rem; font-weight: 700; padding: 0.15rem 0.5rem;
    border-radius: 100px; text-transform: uppercase; letter-spacing: 0.05em;
    background: rgba(59,130,246,0.1); color: #3B82F6;
    border: 1px solid rgba(59,130,246,0.2);
}

/* Info key-value */
.info-kv { padding: 0.6rem 0; border-bottom: 1px solid rgba(255,255,255,0.04); display: flex; justify-content: space-between; align-items: center; font-size: 0.82rem; }
.info-kv:last-child { border-bottom: none; }
.info-k { color: #64748B; font-weight: 500; }
.info-v { color: #CBD5E1; font-weight: 600; font-size: 0.82rem; }

/* Badge */
.bdg { display:inline-flex;align-items:center;gap:0.25rem;padding:0.18rem 0.55rem;border-radius:100px;font-size:0.68rem;font-weight:700;letter-spacing:0.04em; }
.bdg-green  { background:rgba(34,197,94,0.1); color:#22C55E; border:1px solid rgba(34,197,94,0.2); }
.bdg-blue   { background:rgba(59,130,246,0.1); color:#60A5FA; border:1px solid rgba(59,130,246,0.2); }
.bdg-red    { background:rgba(239,68,68,0.1);  color:#F87171; border:1px solid rgba(239,68,68,0.2); }
.bdg-yellow { background:rgba(245,158,11,0.1); color:#FCD34D; border:1px solid rgba(245,158,11,0.2); }
.bdg-purple { background:rgba(124,58,237,0.1); color:#A78BFA; border:1px solid rgba(124,58,237,0.2); }

/* Status dot inline */
.dot { display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:5px;vertical-align:middle; }
.dot-green  { background:#22C55E; box-shadow:0 0 5px #22C55E66; }
.dot-red    { background:#EF4444; }
.dot-blue   { background:#3B82F6; box-shadow:0 0 5px #3B82F666; }
.dot-yellow { background:#F59E0B; }

/* Activity row */
.act-row { display:flex;align-items:center;gap:0.75rem;padding:0.55rem 0;border-bottom:1px solid rgba(255,255,255,0.03);font-size:0.8rem; }
.act-row:last-child { border-bottom:none; }
.act-av { width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#3B82F6,#7C3AED);display:flex;align-items:center;justify-content:center;font-size:0.65rem;font-weight:700;color:white;flex-shrink:0; }
.act-name { font-weight:600;color:#CBD5E1;font-size:0.8rem; }
.act-meta { color:#64748B;font-size:0.7rem; }
.act-time { color:#64748B;font-size:0.7rem;margin-left:auto;white-space:nowrap; }

/* Recognition result */
.recog-result {
    background: linear-gradient(135deg, rgba(13,19,33,0.95), rgba(10,14,26,0.95));
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 1.5rem; text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.recog-avatar {
    width: 72px; height: 72px; border-radius: 50%;
    background: linear-gradient(135deg, #3B82F6, #7C3AED);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.75rem; font-weight: 800; color: white;
    margin: 0 auto 1rem;
    box-shadow: 0 0 24px rgba(59,130,246,0.3);
}
.recog-name { font-size: 1.4rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.25rem; }
.recog-conf { font-size: 0.875rem; color: #64748B; margin-bottom: 1rem; }
.recog-stats { display: flex; justify-content: center; gap: 1.5rem; }
.recog-stat-val { font-size: 1.1rem; font-weight: 700; color: #FFFFFF; }
.recog-stat-lbl { font-size:0.65rem; color:#94A3B8; text-transform: uppercase; letter-spacing: 0.08em; }

/* Recog history item */
.rh-item {
    display:flex;align-items:center;gap:0.625rem;
    padding:0.5rem 0;border-bottom:1px solid rgba(255,255,255,0.03);
}
.rh-item:last-child { border-bottom:none; }
.rh-av { width:26px;height:26px;border-radius:50%;background:linear-gradient(135deg,#3B82F6,#7C3AED);display:flex;align-items:center;justify-content:center;font-size:0.6rem;font-weight:700;color:white;flex-shrink:0; }
.rh-name { font-size:0.78rem;font-weight:600;color:#CBD5E1; }
.rh-sim  { font-size:0.68rem;color:#22C55E; }
.rh-time { font-size:0.65rem;color:#64748B;margin-left:auto; }

/* System overview visual */
.sys-ov {
    background: radial-gradient(ellipse at center, rgba(59,130,246,0.08) 0%, transparent 70%);
    border: 1px solid rgba(59,130,246,0.1);
    border-radius: 16px; padding: 1.5rem;
    display: flex; flex-direction: column; align-items: center;
}
.sys-face-ring {
    width: 120px; height: 120px; border-radius: 50%;
    border: 2px solid rgba(59,130,246,0.4);
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 1.25rem;
    box-shadow: 0 0 30px rgba(59,130,246,0.15), inset 0 0 20px rgba(59,130,246,0.05);
    position: relative;
}
.sys-face-inner {
    width: 90px; height: 90px; border-radius: 50%;
    border: 1px solid rgba(59,130,246,0.25);
    display: flex; align-items: center; justify-content: center;
    font-size: 2.5rem;
}
.sys-check-item {
    display:flex;align-items:center;justify-content:space-between;
    width:100%;padding:0.4rem 0;border-bottom:1px solid rgba(255,255,255,0.03);
    font-size:0.8rem;
}
.sys-check-item:last-child { border-bottom:none; }
.sys-check-label { color:#64748B;display:flex;align-items:center;gap:0.5rem; }
.sys-check-ok  { color:#22C55E;font-weight:700; }
.sys-check-fail { color:#EF4444;font-weight:700; }

/* Tech card */
.tc { background:rgba(13,19,33,0.7);border:1px solid rgba(255,255,255,0.05);border-radius:12px;padding:1rem;text-align:center;transition:all 0.2s; }
.tc:hover { border-color:rgba(59,130,246,0.25);background:rgba(59,130,246,0.05); }
.tc-em { font-size:1.6rem;display:block;margin-bottom:0.4rem; }
.tc-name { font-size:0.78rem;font-weight:700;color:#E2E8F0;margin-bottom:0.2rem; }
.tc-desc { font-size:0.68rem;color:#64748B; }

/* Step card */
.sc { background:rgba(13,19,33,0.7);border:1px solid rgba(255,255,255,0.05);border-radius:12px;padding:1.1rem; }
.sc-num { font-size:0.6rem;font-weight:800;color:#3B82F6;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.35rem; }
.sc-title { font-size:0.82rem;font-weight:700;color:#E2E8F0;margin-bottom:0.2rem; }
.sc-desc { font-size:0.73rem;color:#64748B;line-height:1.5; }

/* Camera glow border */
.cam-glow {
    border-radius:14px; overflow:hidden;
    border:1px solid rgba(59,130,246,0.25);
    box-shadow:0 0 24px rgba(59,130,246,0.1),0 4px 32px rgba(0,0,0,0.5);
}

/* Camera idle placeholder */
.cam-idle {
    background: linear-gradient(135deg, rgba(13,19,33,0.9), rgba(10,14,26,0.9));
    border: 1px solid rgba(59,130,246,0.15);
    border-radius: 14px; height: 340px;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    gap: 0.875rem; color: #1E293B;
}

/* Scanning badge */
.scanning-badge {
    display:inline-flex;align-items:center;gap:0.4rem;
    padding:0.2rem 0.6rem;border-radius:100px;
    background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.2);
    font-size:0.68rem;font-weight:700;color:#22C55E;
    text-transform:uppercase;letter-spacing:0.06em;
}

/* Settings card */
.stg-card {
    background: linear-gradient(145deg, rgba(13,19,33,0.95), rgba(10,14,26,0.98));
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px; padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    height: 100%;
}
.stg-card-hdr { display:flex;align-items:flex-start;gap:0.75rem;margin-bottom:1.25rem; }
.stg-icon { font-size:1.5rem;flex-shrink:0;margin-top:0.1rem; }
.stg-title { font-size:0.95rem;font-weight:700;color:#E2E8F0; }
.stg-subtitle { font-size:0.75rem;color:#334155; }

/* Threshold bar */
.thresh-bar-wrap { margin:0.75rem 0; }
.thresh-bar-labels { display:flex;justify-content:space-between;font-size:0.72rem;color:#334155;margin-bottom:0.3rem; }
.thresh-bar-track { background:rgba(10,15,28,0.8);border-radius:100px;height:5px;overflow:hidden; }
.thresh-bar-fill  { height:100%;background:linear-gradient(90deg,#3B82F6,#06B6D4);border-radius:100px; }

/* About hero */
.about-hero {
    background: linear-gradient(135deg, rgba(59,130,246,0.07) 0%, rgba(124,58,237,0.07) 100%);
    border: 1px solid rgba(59,130,246,0.12);
    border-radius: 20px; padding: 2.5rem;
    display: flex; gap: 2rem; align-items: center;
    margin-bottom: 2rem;
}

/* Gradient text */
.grad-text { background:linear-gradient(135deg,#3B82F6,#06B6D4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text; }
.grad-text-purple { background:linear-gradient(135deg,#7C3AED,#3B82F6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text; }

/* Empty state */
.empty-state { padding:3rem;text-align:center;color:#475569; }
.empty-state-icon { font-size:2.5rem;display:block;margin-bottom:0.75rem; }
.empty-state-msg { font-size:0.875rem;font-weight:500;color:#475569; }

/* Pulse animation for scanning dot */
@keyframes pulse { 0%,100%{opacity:1}50%{opacity:0.4} }
.pulse { animation: pulse 1.5s ease-in-out infinite; }

</style>
"""
