"""ui/pages/registered_users.py — Registered Users management page."""

from datetime import date

import streamlit as st

import backend_api as api
from ui.components import topbar, sec_header, kpi, empty_state


def _get_today_present_set():
    """Query attendance ONCE and return a set of names present today. Fixes N+1 query."""
    records = api.get_attendance_records(filter_date=date.today().strftime("%Y-%m-%d"))
    return {r[1] for r in records}



@st.dialog("Confirm Deletion")
def confirm_delete_dialog(name):
    st.warning(f"⚠️ Delete **{name}**? This permanently removes their face embedding from the database.")
    ca, cb = st.columns(2)
    with ca:
        if st.button("✅ Confirm Delete", use_container_width=True, type="primary"):
            api.delete_user(name)
            st.rerun()
    with cb:
        if st.button("Cancel", use_container_width=True, type="secondary"):
            st.rerun()

def render():
    st.markdown(topbar(
        "Registered Users",
        subtitle="View, search, and manage all registered face profiles"
    ), unsafe_allow_html=True)

    users = api.get_all_users()


    today_present = _get_today_present_set()
    today_count   = len(today_present)
    total_records = len(api.get_attendance_records())

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(kpi("👥", len(users),  "Total Users",
                        sub=f"Face embeddings stored", color="blue"),
                    unsafe_allow_html=True)
    with k2:
        st.markdown(kpi("✅", today_count, "Present Today",
                        sub=f"{int(today_count/max(len(users),1)*100)}% of total", color="green"),
                    unsafe_allow_html=True)
    with k3:
        st.markdown(kpi("📋", total_records, "Total Attendance",
                        sub="All time records", color="purple"),
                    unsafe_allow_html=True)
    with k4:
        absent = max(len(users) - today_count, 0)
        st.markdown(kpi("❌", absent, "Absent Today",
                        sub="Not yet marked", color="orange"),
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not users:
        st.markdown(empty_state("👥", "No users registered yet. Go to Register User to add your first person."),
                    unsafe_allow_html=True)
        return


    main_col, side_col = st.columns([3, 1], gap="large")

    with main_col:
        sc1, sc2 = st.columns([3, 1])
        with sc1:
            search = st.text_input(
                "Search",
                placeholder="🔍  Search by name…",
                label_visibility="collapsed",
                key="user_search",
            )
        with sc2:
            sort_opt = st.selectbox(
                "Sort",
                ["Newest", "Oldest", "Name A→Z", "Name Z→A"],
                label_visibility="collapsed",
                key="user_sort",
            )


        filtered = [u for u in users if search.lower() in u[1].lower()] if search else list(users)
        if sort_opt == "Oldest":
            filtered.sort(key=lambda u: u[0])
        elif sort_opt == "Newest":
            filtered.sort(key=lambda u: u[0], reverse=True)
        elif sort_opt == "Name A→Z":
            filtered.sort(key=lambda u: u[1].lower())
        elif sort_opt == "Name Z→A":
            filtered.sort(key=lambda u: u[1].lower(), reverse=True)

        if search:
            st.caption(f"Showing {len(filtered)} of {len(users)} users")

        st.markdown("<br>", unsafe_allow_html=True)





        PER_PAGE = 8
        total_pages = max(1, (len(filtered) + PER_PAGE - 1) // PER_PAGE)
        if "user_page" not in st.session_state:
            st.session_state.user_page = 1
        if st.session_state.user_page > total_pages:
            st.session_state.user_page = 1

        page_start = (st.session_state.user_page - 1) * PER_PAGE
        page_users = filtered[page_start: page_start + PER_PAGE]

        if not page_users:
            st.markdown(empty_state("🔍", f"No users match '{search}'"), unsafe_allow_html=True)
        else:

            with st.container(border=True):
                h_cols = st.columns([0.4, 0.3, 2.5, 1.5, 1.5])
                for h, col in zip(["ID", "Photo", "Name", "Status", "Actions"], h_cols):
                    col.markdown(
                        f'<div style="font-size:0.65rem;font-weight:700;color:#1E293B;text-transform:uppercase;letter-spacing:0.08em;padding-bottom:0.4rem;">{h}</div>',
                        unsafe_allow_html=True,
                    )
                st.divider()

                for uid, name in page_users:
                    is_present = name in today_present
                    initials   = "".join(w[0].upper() for w in name.split()[:2]) or "?"

                    row = st.columns([0.4, 0.3, 2.5, 1.5, 1.5])


                    row[0].markdown(
                        f'<div style="font-size:0.78rem;color:#334155;padding:0.5rem 0;">{uid}</div>',
                        unsafe_allow_html=True,
                    )

                    row[1].markdown(f"""
                    <div style="padding:0.35rem 0;">
                        <div style="width:30px;height:30px;border-radius:50%;
                            background:linear-gradient(135deg,#3B82F6,#7C3AED);
                            display:flex;align-items:center;justify-content:center;
                            font-size:0.65rem;font-weight:700;color:white;">{initials}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    row[2].markdown(
                        f'<div style="font-size:0.875rem;font-weight:600;color:#E2E8F0;padding:0.5rem 0;">{name}</div>',
                        unsafe_allow_html=True,
                    )

                    badge_html = (
                        '<span class="bdg bdg-green">● Present</span>'
                        if is_present else
                        '<span class="bdg bdg-red">● Absent</span>'
                    )
                    row[3].markdown(f'<div style="padding:0.45rem 0;">{badge_html}</div>', unsafe_allow_html=True)


                    with row[4]:
                        a1, a2 = st.columns(2)
                        with a1:
                            if st.button("🗑", key=f"del_{uid}", use_container_width=True, type="secondary"):
                                confirm_delete_dialog(name)
                        with a2:
                            if st.button("✏️", key=f"edit_{uid}", use_container_width=True, type="secondary"):
                                st.session_state.current_page = "Register User"
                                st.session_state.reg_name_input = name
                                st.rerun()

                    st.markdown('<div style="border-top:1px solid rgba(255,255,255,0.03);"></div>', unsafe_allow_html=True)


            if total_pages > 1:
                st.markdown("<br>", unsafe_allow_html=True)
                pg1, pg2, pg3 = st.columns([1, 3, 1])
                with pg1:
                    if st.button("← Prev", use_container_width=True, type="secondary",
                                 disabled=st.session_state.user_page <= 1):
                        st.session_state.user_page -= 1
                        st.rerun()
                pg2.markdown(
                    f'<div style="text-align:center;color:#475569;font-size:0.8rem;padding-top:0.5rem;">'
                    f'Page {st.session_state.user_page} of {total_pages} '
                    f'· Showing {len(page_users)} of {len(filtered)} users</div>',
                    unsafe_allow_html=True,
                )
                with pg3:
                    if st.button("Next →", use_container_width=True, type="secondary",
                                 disabled=st.session_state.user_page >= total_pages):
                        st.session_state.user_page += 1
                        st.rerun()



    with side_col:
        st.markdown(sec_header("Quick Actions"), unsafe_allow_html=True)
        with st.container(border=True):
            if st.button("➕ Register New User", use_container_width=True):
                st.session_state.current_page = "Register User"
                st.rerun()
            st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)
            if st.button("📋 View Attendance", use_container_width=True, type="secondary"):
                st.session_state.current_page = "Attendance"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(sec_header("Overview"), unsafe_allow_html=True)
        with st.container(border=True):
            att_rate = int(today_count / max(len(users), 1) * 100)
            st.markdown(f"""
            <div style="text-align:center;padding:0.75rem 0;">
                <div style="font-size:2.5rem;font-weight:800;
                    background:linear-gradient(135deg,#3B82F6,#06B6D4);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;">{att_rate}%</div>
                <div style="font-size:0.7rem;color:#334155;text-transform:uppercase;
                    letter-spacing:0.08em;margin-top:0.25rem;">Attendance Rate Today</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(att_rate / 100)
            st.markdown(
                f'<div style="font-size:0.75rem;color:#475569;text-align:center;margin-top:0.5rem;">'
                f'{today_count} present of {len(users)} registered</div>',
                unsafe_allow_html=True,
            )
