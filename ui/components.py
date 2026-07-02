"""
ui/components.py
----------------
Pure-HTML component builders — all return strings for st.markdown().
RULE: These functions NEVER contain Streamlit widgets.
      They are only for display-only content.
"""

from datetime import datetime


def topbar(page_name: str, subtitle: str = "") -> str:
    now = datetime.now()
    return f"""
    <div class="topbar">
        <div class="topbar-left">
            <h1>{page_name}</h1>
            <p>{subtitle}</p>
        </div>
        <div class="topbar-right">
            <div class="topbar-breadcrumb">
                <span>Dashboard</span> › {page_name}
            </div>
            <div class="topbar-datetime">
                📅 {now.strftime('%d %B %Y')} &nbsp;|&nbsp; {now.strftime('%I:%M %p')}
            </div>
        </div>
    </div>
    """


def kpi(icon: str, value, label: str, sub: str = "", color: str = "blue", sub_class: str = "") -> str:
    sub_html = f'<div class="kpi-sub {sub_class}">{sub}</div>' if sub else ""
    return f"""
    <div class="kpi {color}">
        <span class="kpi-icon">{icon}</span>
        <div class="kpi-val">{value}</div>
        <div class="kpi-label">{label}</div>
        {sub_html}
    </div>
    """


def sec_header(title: str, badge: str = "") -> str:
    badge_html = f'<span class="sec-hdr-badge">{badge}</span>' if badge else ""
    return f"""
    <div class="sec-hdr">
        <span class="sec-hdr-title">{title}</span>
        {badge_html}
    </div>
    """


def info_kv_table(rows: list) -> str:
    """
    Render key-value pairs.
    rows: list of (key, value) tuples.
    value can include raw HTML (e.g., badges).
    """
    inner = "".join(
        f'<div class="info-kv"><span class="info-k">{k}</span><span class="info-v">{v}</span></div>'
        for k, v in rows
    )
    return f'<div style="padding:0.1rem 0;">{inner}</div>'


def badge(text: str, color: str = "blue") -> str:
    return f'<span class="bdg bdg-{color}">{text}</span>'


def dot(color: str = "green") -> str:
    return f'<span class="dot dot-{color}"></span>'


def activity_item(name: str, date_str: str, time_str: str) -> str:
    initials = "".join(w[0].upper() for w in name.split()[:2]) or "?"
    return f"""
    <div class="act-row">
        <div class="act-av">{initials}</div>
        <div>
            <div class="act-name">{name}</div>
            <div class="act-meta">{date_str}</div>
        </div>
        <div class="act-time">{time_str}</div>
    </div>
    """


def recog_result_card(name: str, similarity: float, is_known: bool, time_str: str, marked: bool) -> str:
    initials = "".join(w[0].upper() for w in name.split()[:2]) if is_known else "?"
    status_color = "#22C55E" if marked else "#3B82F6"
    status_text  = "Attendance Marked" if marked else ("Present — Already Marked" if is_known else "Unknown Person")
    status_icon  = "✅" if marked else ("🔁" if is_known else "❌")

    conf_color   = "#22C55E" if similarity >= 92 else ("#F59E0B" if similarity >= 89 else "#EF4444")
    border_color = "#22C55E" if is_known else "#EF4444"

    return f"""
    <div class="recog-result" style="border:1px solid {border_color}22;">
        <div class="recog-avatar" style="{'background:linear-gradient(135deg,#22C55E,#06B6D4)' if is_known else 'background:linear-gradient(135deg,#EF4444,#F59E0B)'}">
            {initials}
        </div>
        <div class="recog-name">{name}</div>
        <div class="recog-conf">{time_str}</div>
        <div style="display:flex;justify-content:center;margin-bottom:1rem;">
            <span style="background:rgba(255,255,255,0.1);border:1px solid {border_color}44;border-radius:100px;
                         padding:0.2rem 0.75rem;font-size:0.75rem;color:{border_color};font-weight:600;">
                {status_icon} {status_text}
            </span>
        </div>
        <div class="recog-stats">
            <div style="text-align:center;">
                <div class="recog-stat-val" style="color:{conf_color};">{similarity:.1f}%</div>
                <div class="recog-stat-lbl">Confidence</div>
            </div>
            <div style="text-align:center;border-left:1px solid rgba(255,255,255,0.2);padding-left:1.5rem;">
                <div class="recog-stat-val" style="color:#A0AEC0;">89%</div>
                <div class="recog-stat-lbl">Threshold</div>
            </div>
        </div>
    </div>
    """


def recog_history_item(name: str, similarity: float, time_str: str) -> str:
    """Single-line HTML — no indentation to avoid Streamlit markdown code-block rendering."""
    initials  = "".join(w[0].upper() for w in name.split()[:2]) if name != "Unknown" else "?"
    known     = name != "Unknown"
    sim_color = "#22C55E" if known else "#EF4444"
    av_grad   = "background:linear-gradient(135deg,#22C55E,#06B6D4)" if known else "background:linear-gradient(135deg,#EF4444,#F59E0B)"
    return (
        f'<div class="rh-item">'
        f'<div class="rh-av" style="{av_grad};">{initials}</div>'
        f'<div><div class="rh-name">{name}</div>'
        f'<div class="rh-sim" style="color:{sim_color};">{similarity:.1f}%</div></div>'
        f'<div class="rh-time" style="font-size:0.65rem;color:#64748B;margin-left:auto;">{time_str}</div>'
        f'</div>'
    )


def system_overview_html(model_ok: bool, db_ok: bool, att_db_ok: bool, cam_ok: bool) -> str:
    def check(ok): return f'<span class="sys-check-ok">✓</span>' if ok else f'<span class="sys-check-fail">✗</span>'
    all_ok = model_ok and db_ok and att_db_ok
    overall = '<span style="color:#22C55E;font-size:0.75rem;font-weight:600;">● All Systems Operational</span>'
    if not all_ok:
        overall = '<span style="color:#EF4444;font-size:0.75rem;font-weight:600;">● System Issue Detected</span>'
    return f"""
    <div class="sys-ov">
        <div class="sys-face-ring">
            <div class="sys-face-inner">🎭</div>
        </div>
        <div style="width:100%;">
            <div class="sys-check-item"><span class="sys-check-label">🧠 AI Model — InsightFace</span>{check(model_ok)}</div>
            <div class="sys-check-item"><span class="sys-check-label">🗄️ Database</span>{check(db_ok)}</div>
            <div class="sys-check-item"><span class="sys-check-label">📋 Attendance DB</span>{check(att_db_ok)}</div>
            <div class="sys-check-item"><span class="sys-check-label">📹 Camera</span>{check(cam_ok)}</div>
        </div>
        <div style="margin-top:1rem;">{overall}</div>
    </div>
    """


def empty_state(icon: str, message: str) -> str:
    return f"""
    <div class="empty-state">
        <span class="empty-state-icon">{icon}</span>
        <div class="empty-state-msg">{message}</div>
    </div>
    """
