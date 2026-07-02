"""ui/pages/dashboard.py — Dashboard page."""

import streamlit as st
import plotly.graph_objects as go
from datetime import date, timedelta

import backend_api as api
from ui.components import (
    topbar, kpi, sec_header, activity_item,
    system_overview_html, empty_state
)


@st.cache_data(ttl=15, show_spinner=False)
def _load_stats():
    return api.get_dashboard_stats()


def _attendance_line_chart(records_by_date: list) -> go.Figure:
    """Area line chart for attendance trend."""
    if not records_by_date:
        x, y = [], []
    else:
        x = [r[0] for r in records_by_date]
        y = [r[1] for r in records_by_date]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines+markers",
        fill="tozeroy",
        line=dict(color="#3B82F6", width=2.5, shape="spline"),
        marker=dict(size=5, color="#60A5FA"),
        fillcolor="rgba(59,130,246,0.08)",
        hovertemplate="<b>%{x}</b><br>%{y} attendees<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#475569", size=11),
        margin=dict(l=0, r=0, t=8, b=0), height=220,
        xaxis=dict(showgrid=False, zeroline=False, tickangle=-30, color="#334155"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False, color="#334155", tickformat="d"),
        hoverlabel=dict(bgcolor="#111827", bordercolor="#3B82F6", font=dict(color="white", family="Inter")),
    )
    return fig


def render():
    stats  = _load_stats()
    cam_ok = api.is_camera_available()

    st.markdown(topbar(
        "Dashboard",
        subtitle="Welcome! Here's what's happening today."
    ), unsafe_allow_html=True)

    # ── KPI Row ────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5, k6 = st.columns(6)

    total_users   = stats["total_users"]
    today_att     = stats["today_attendance"]
    att_rate      = stats["attendance_rate"]
    total_records = stats["total_records"]

    with k1:
        st.markdown(kpi("👥", total_users,  "Total Registered Users",
                        sub=f"+{max(total_users-1,0)} registered", color="blue", sub_class="pos"),
                    unsafe_allow_html=True)
    with k2:
        st.markdown(kpi("✅", today_att, "Today's Attendance",
                        sub=f"+{today_att} today", color="green", sub_class="pos"),
                    unsafe_allow_html=True)
    with k3:
        status_text = "Active" if cam_ok else "Inactive"
        dot_icon    = "🟢" if cam_ok else "🔴"
        st.markdown(kpi("🎯", status_text, "Recognition Status",
                        sub="System Running" if cam_ok else "Camera Offline",
                        color="cyan" if cam_ok else "orange"),
                    unsafe_allow_html=True)
    with k4:
        st.markdown(kpi("📹", "Live" if cam_ok else "Offline", "Camera Status",
                        sub="Camera is Active" if cam_ok else "Check connection",
                        color="cyan" if cam_ok else "red"),
                    unsafe_allow_html=True)
    with k5:
        st.markdown(kpi("🗄️", "Connected", "Attendance DB",
                        sub="SQLite Connected", color="purple"),
                    unsafe_allow_html=True)
    with k6:
        rate_color = "green" if att_rate >= 75 else ("orange" if att_rate >= 40 else "red")
        st.markdown(kpi("📊", f"{att_rate}%", "Attendance Rate",
                        sub=f"of {total_users} registered", color=rate_color),
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── System Overview | Today's Attendance ───────────────────────────────
    ov_col, chart_col = st.columns([1, 1.6], gap="large")

    with ov_col:
        st.markdown(sec_header("System Overview"), unsafe_allow_html=True)
        st.markdown(
            system_overview_html(
                model_ok=True, db_ok=True, att_db_ok=True, cam_ok=cam_ok
            ),
            unsafe_allow_html=True,
        )

    with chart_col:
        st.markdown(
            sec_header("Today's Attendance Overview", badge="Last 14 Days"),
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            if stats["attendance_by_date"]:
                st.plotly_chart(
                    _attendance_line_chart(stats["attendance_by_date"]),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
            else:
                st.markdown(empty_state("📊", "No attendance data yet"), unsafe_allow_html=True)

            # Sub-stats row
            absent = max(total_users - today_att, 0)
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Total Marked",        today_att)
            s2.metric("Unique Individuals",  today_att)
            s3.metric("Attendance Rate",     f"{att_rate}%")
            s4.metric("Remaining",           absent)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Bottom Row: Recent Attendance | System Activity (Quick Actions → sidebar) ──
    bot1, bot3 = st.columns([2.8, 1.6], gap="large")

    with bot1:
        st.markdown(sec_header("Recent Attendance", badge=f"{len(stats['recent_records'])}"),
                    unsafe_allow_html=True)
        with st.container(border=True):
            if stats["recent_records"]:
                # Table header
                hcols = st.columns([2.5, 1.2, 1.2, 1.2])
                for h, col in zip(["Person", "Date", "Time", "Status"], hcols):
                    col.markdown(
                        f'<div style="font-size:0.68rem;font-weight:700;color:#1E293B;'
                        f'text-transform:uppercase;letter-spacing:0.07em;padding:0 0 0.4rem;">{h}</div>',
                        unsafe_allow_html=True,
                    )

                for name, d, t in stats["recent_records"][:6]:
                    initials = "".join(w[0].upper() for w in name.split()[:2])
                    rc = st.columns([2.5, 1.2, 1.2, 1.2])
                    rc[0].markdown(f"""
                    <div style="display:flex;align-items:center;gap:0.5rem;padding:0.4rem 0;
                                border-bottom:1px solid rgba(255,255,255,0.03);">
                        <div style="width:26px;height:26px;border-radius:50%;
                                    background:linear-gradient(135deg,#3B82F6,#7C3AED);
                                    display:flex;align-items:center;justify-content:center;
                                    font-size:0.6rem;font-weight:700;color:white;flex-shrink:0;">{initials}</div>
                        <span style="font-size:0.82rem;font-weight:600;color:#CBD5E1;">{name}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    rc[1].markdown(f'<div style="font-size:0.8rem;color:#64748B;padding:0.4rem 0;">{d}</div>', unsafe_allow_html=True)
                    rc[2].markdown(f'<div style="font-size:0.8rem;color:#64748B;padding:0.4rem 0;">{t}</div>', unsafe_allow_html=True)
                    rc[3].markdown(f'<div style="padding:0.4rem 0;"><span class="bdg bdg-green" style="font-size:0.65rem;">● Marked</span></div>', unsafe_allow_html=True)
            else:
                st.markdown(empty_state("📋", "No attendance records yet"), unsafe_allow_html=True)

    with bot3:
        st.markdown(sec_header("System Activity"), unsafe_allow_html=True)
        with st.container(border=True):
            activities = [
                ("System started successfully", "All services running"),
                ("Model loaded",               "buffalo_l ready"),
                ("Database connected",         "faces.db active"),
                ("Attendance DB ready",        "attendance.db active"),
            ]
            for title, sub in activities:
                st.markdown(f"""
                <div style="display:flex;align-items:flex-start;gap:0.625rem;padding:0.45rem 0;
                            border-bottom:1px solid rgba(255,255,255,0.03);">
                    <span style="color:#3B82F6;font-size:0.5rem;margin-top:0.45rem;flex-shrink:0;">●</span>
                    <div>
                        <div style="font-size:0.78rem;font-weight:600;color:#CBD5E1;">{title}</div>
                        <div style="font-size:0.7rem;color:#334155;">{sub}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Tip about sidebar shortcuts
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(59,130,246,0.06);border:1px solid rgba(59,130,246,0.1);
                    border-radius:10px;padding:0.75rem 1rem;font-size:0.75rem;color:#475569;">
            💡 <strong style="color:#60A5FA;">Tip:</strong> Use the
            <strong style="color:#CBD5E1;">Quick Actions</strong> in the sidebar
            to jump to any feature instantly.
        </div>
        """, unsafe_allow_html=True)
