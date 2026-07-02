"""ui/pages/attendance_page.py — Attendance log with filters, charts, export."""

import io
from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import backend_api as api
from ui.components import topbar, sec_header, kpi, empty_state


def _donut_chart(present: int, total: int) -> go.Figure:
    absent = max(total - present, 0)
    fig = go.Figure(go.Pie(
        values=[present, absent],
        labels=["Present", "Absent"],
        hole=0.72,
        marker=dict(colors=["#3B82F6", "#1E293B"]),
        textinfo="none",
        hovertemplate="%{label}: %{value}<extra></extra>",
    ))
    fig.add_annotation(
        text=f"<b>{present}</b>",
        x=0.5, y=0.55, font=dict(size=22, color="white", family="Inter"),
        showarrow=False,
    )
    fig.add_annotation(
        text="Total Marked",
        x=0.5, y=0.38, font=dict(size=9, color="#475569", family="Inter"),
        showarrow=False,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(font=dict(color="#64748B", size=10, family="Inter"),
                    bgcolor="rgba(0,0,0,0)", x=0.5, xanchor="center", y=-0.05, orientation="h"),
        margin=dict(l=0, r=0, t=10, b=0), height=180,
    )
    return fig


def _trend_chart(records: list) -> go.Figure:
    if not records:
        return None
    df    = pd.DataFrame(records, columns=["ID", "Name", "Date", "Time"])
    daily = df.groupby("Date").size().reset_index(name="Count")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["Count"],
        mode="lines+markers", fill="tozeroy",
        line=dict(color="#3B82F6", width=2, shape="spline"),
        marker=dict(size=4, color="#60A5FA"),
        fillcolor="rgba(59,130,246,0.06)",
        hovertemplate="<b>%{x}</b><br>%{y}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#475569", size=10),
        margin=dict(l=0, r=0, t=5, b=0), height=150,
        xaxis=dict(showgrid=False, zeroline=False, tickangle=-30, color="#334155"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False, tickformat="d"),
    )
    return fig


def _to_csv(records: list) -> bytes:
    return pd.DataFrame(records, columns=["ID", "Name", "Date", "Time"]).to_csv(index=False).encode("utf-8")


def _to_excel(records: list) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        pd.DataFrame(records, columns=["ID", "Name", "Date", "Time"]).to_excel(w, index=False)
    return buf.getvalue()


def render():
    st.markdown(topbar(
        "Attendance",
        subtitle="View and manage all attendance records"
    ), unsafe_allow_html=True)


    f1, f2, f3, f4 = st.columns([1.2, 1.5, 2.5, 1.2])
    with f1:
        filter_date_val = st.date_input("Select Date", value=date.today(),
                                        label_visibility="visible", key="att_date")
    with f2:
        range_mode = st.selectbox("Range", ["Custom Date", "Today", "Last 7 Days", "Last 30 Days", "All Time"],
                                  label_visibility="visible", key="att_range")
    with f3:
        search_name = st.text_input("Search", placeholder="🔍  Search by name or department…",
                                    label_visibility="visible", key="att_search")
    with f4:
        st.markdown("<div style='height:1.7rem;'></div>", unsafe_allow_html=True)
        export_btn = st.button("⬇ Export", use_container_width=True)


    all_records = api.get_attendance_records()


    if range_mode == "Today":
        records = api.get_attendance_records(filter_date=date.today().strftime("%Y-%m-%d"))
    elif range_mode == "Last 7 Days":
        cutoff  = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        records = [r for r in all_records if r[2] >= cutoff]
    elif range_mode == "Last 30 Days":
        cutoff  = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
        records = [r for r in all_records if r[2] >= cutoff]
    elif range_mode == "Custom Date":
        records = api.get_attendance_records(filter_date=str(filter_date_val))
    else:
        records = all_records


    if search_name:
        records = [r for r in records if search_name.lower() in r[1].lower()]


    if export_btn and records:
        ex1, ex2 = st.columns(2)
        with ex1:
            st.download_button("⬇ Download CSV", _to_csv(records),
                               f"attendance_{date.today()}.csv", "text/csv",
                               use_container_width=True)
        with ex2:
            st.download_button("⬇ Download Excel", _to_excel(records),
                               f"attendance_{date.today()}.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)


    total_users  = api.get_user_count()
    today_count  = api.get_today_count()
    att_rate     = int(today_count / max(total_users, 1) * 100)
    unique_people = len(set(r[1] for r in records))
    first_time   = min((r[3] for r in records), default="—")
    last_time    = max((r[3] for r in records), default="—")

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(kpi("✅", today_count, "Total Marked",
                        sub=f"+{today_count} from yesterday", color="green", sub_class="pos"),
                    unsafe_allow_html=True)
    with k2:
        st.markdown(kpi("👤", unique_people, "Unique Individuals",
                        sub="In current filter", color="blue"),
                    unsafe_allow_html=True)
    with k3:
        st.markdown(kpi("📊", f"{att_rate}%", "Attendance Rate",
                        sub=f"vs {total_users} registered", color="purple"),
                    unsafe_allow_html=True)
    with k4:
        st.markdown(kpi("🕐", first_time if first_time != "—" else "--:--", "First Marked",
                        sub="Today's first entry", color="cyan"),
                    unsafe_allow_html=True)
    with k5:
        st.markdown(kpi("🕕", last_time if last_time != "—" else "--:--", "Last Marked",
                        sub="Most recent entry", color="orange"),
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


    table_col, panel_col = st.columns([2.2, 1], gap="large")

    with table_col:
        st.markdown(
            sec_header("Attendance Records", badge=f"{len(records)} records"),
            unsafe_allow_html=True,
        )

        if not records:
            with st.container(border=True):
                st.markdown(empty_state("📋", "No records match the current filter."), unsafe_allow_html=True)
        else:
            with st.container(border=True):
                df = pd.DataFrame(records, columns=["ID", "Name", "Date", "Time"])
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "ID":   st.column_config.NumberColumn("ID",   width="small"),
                        "Name": st.column_config.TextColumn("Name",   width="medium"),
                        "Date": st.column_config.TextColumn("Date",   width="medium"),
                        "Time": st.column_config.TextColumn("Time",   width="medium"),
                    },
                    height=min(450, 36 + len(df) * 35),
                )
                st.markdown(
                    f'<div style="font-size:0.75rem;color:#334155;padding:0.4rem 0;">Showing {len(records)} of {len(all_records)} total records</div>',
                    unsafe_allow_html=True,
                )

    with panel_col:

        st.markdown(sec_header("Attendance Overview", badge="Today"), unsafe_allow_html=True)
        with st.container(border=True):
            absent = max(total_users - today_count, 0)
            st.plotly_chart(_donut_chart(today_count, total_users),
                            use_container_width=True, config={"displayModeBar": False})
            dc1, dc2 = st.columns(2)
            dc1.markdown(f'<div style="text-align:center;font-size:0.72rem;"><div style="color:#3B82F6;font-weight:700;">{today_count}</div><div style="color:#334155;">Present ({att_rate}%)</div></div>', unsafe_allow_html=True)
            dc2.markdown(f'<div style="text-align:center;font-size:0.72rem;"><div style="color:#EF4444;font-weight:700;">{absent}</div><div style="color:#334155;">Absent</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)


        st.markdown(sec_header("Attendance Trend", badge="Last 7 Days"), unsafe_allow_html=True)
        with st.container(border=True):
            chart = _trend_chart(all_records)
            if chart:
                st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})
            else:
                st.markdown(empty_state("📈", "No trend data yet"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)


        st.markdown(sec_header("Quick Actions"), unsafe_allow_html=True)
        with st.container(border=True):
            if records:
                st.download_button(
                    "⬇ Export Today's CSV",
                    _to_csv(api.get_attendance_records(filter_date=date.today().strftime("%Y-%m-%d"))),
                    f"attendance_today_{date.today()}.csv",
                    "text/csv",
                    use_container_width=True,
                )
            st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)


        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(sec_header("Recent Activity"), unsafe_allow_html=True)
        with st.container(border=True):
            recent = all_records[-5:][::-1] if all_records else []
            if recent:
                for _, name, d, t in recent:
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:0.5rem;
                                padding:0.4rem 0;border-bottom:1px solid rgba(255,255,255,0.03);">
                        <span style="color:#22C55E;font-size:0.6rem;">●</span>
                        <div>
                            <div style="font-size:0.75rem;font-weight:600;color:#CBD5E1;">Attendance marked for {name}</div>
                            <div style="font-size:0.68rem;color:#334155;">{t} · {d}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#1E293B;font-size:0.8rem;">No activity.</div>', unsafe_allow_html=True)


    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("⚠️  Danger Zone — Clear All Attendance"):
        st.warning("This will permanently delete ALL attendance records across all dates. This cannot be undone.")
        confirm = st.text_input("Type **DELETE ALL** to confirm:", placeholder="DELETE ALL", key="att_confirm_clear")
        if st.button("🗑 Clear All Attendance Records", type="secondary"):
            if confirm.strip() == "DELETE ALL":
                deleted = api.clear_all_attendance()
                st.success(f"✅ Cleared {deleted} attendance record(s).")
                st.rerun()
            else:
                st.error("You must type 'DELETE ALL' exactly to proceed.")
