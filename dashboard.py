"""
Module 6 — dashboard.py
Streamlit‑based UI for the Future Regret Prediction AI Agent.

Run:  streamlit run dashboard.py
"""

import json
import streamlit as st
import streamlit.components.v1
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

from config import CAREER_OPTIONS, REGRET_THRESHOLDS
from user_input import build_profile, UserProfile
from analyzer import analyze, AnalysisResult
from regret_engine import compute_regret, RegretResult
from predictor import predict, PredictionReport
from recommendation import recommend, Recommendation
from database import (upsert_user, save_snapshot, get_user_snapshots,
                      get_user, create_account, authenticate)

matplotlib.rcParams["font.size"] = 10

# ── Page config ─────────────────────────────────────────────
st.set_page_config(
    page_title="Future Regret Prediction AI Agent",
    page_icon="🔮",
    layout="wide",
)

# ── Custom CSS ──────────────────────────────────────────────
st.markdown("""
<style>
    .main {background-color: #0e1117;}
    .score-card {
        padding: 1.5rem; border-radius: 1rem; text-align: center;
        color: #fff; margin-bottom: 1rem;
    }
    .score-low      {background: linear-gradient(135deg, #1b8a5a, #2ecc71);}
    .score-moderate {background: linear-gradient(135deg, #d4a017, #f1c40f);}
    .score-high     {background: linear-gradient(135deg, #d35400, #e67e22);}
    .score-critical {background: linear-gradient(135deg, #c0392b, #e74c3c);}
    .metric-box {
        background: #1a1a2e; border-radius: 0.75rem;
        padding: 1rem; margin: 0.3rem 0; border-left: 4px solid #3498db;
    }
    .stop-action  {border-left-color: #e74c3c !important;}
    .start-action {border-left-color: #2ecc71 !important;}
    .section-hdr  {border-bottom: 2px solid #3498db; padding-bottom: 0.3rem;}
    /* Login page styles */
    .login-container {
        max-width: 420px; margin: 2rem auto; padding: 2.5rem;
        background: #1a1a2e; border-radius: 1.2rem;
        border: 1px solid #2d2d44;
    }
    .login-title {
        text-align: center; font-size: 1.8rem; margin-bottom: 0.2rem; color: #fff;
    }
    .login-sub {
        text-align: center; color: #888; font-size: 0.95rem; margin-bottom: 1.5rem;
    }
    .welcome-bar {
        background: linear-gradient(90deg, #1a1a2e, #16213e);
        padding: 0.6rem 1.2rem; border-radius: 0.6rem;
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 0.5rem; border: 1px solid #2d2d44;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================
# LOGIN / SIGNUP GATE
# =============================================================

def _show_login_page():
    """Render the login / sign‑up form."""

    st.markdown(
        "<h1 style='text-align:center; margin-top:1.5rem;'>"
        "🔮 Future Regret Prediction AI Agent</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='login-sub'>Sign in to analyze your lifestyle and predict future regret</p>",
        unsafe_allow_html=True,
    )

    # Toggle between Login / Sign Up
    mode = st.radio("Auth Mode", ["Login", "Sign Up"], horizontal=True,
                    label_visibility="collapsed", key="auth_mode")

    if mode == "Login":
        with st.form("login_form"):
            st.markdown("#### 🔑 Login")
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password",
                                     placeholder="Enter your password")
            submitted = st.form_submit_button("Login", use_container_width=True,
                                              type="primary")
            if submitted:
                if not email or not password:
                    st.error("Please fill in both fields.")
                elif "@" not in email:
                    st.error("Please enter a valid email address.")
                else:
                    account = authenticate(email, password)
                    if account:
                        st.session_state["logged_in"] = True
                        st.session_state["account"]   = account
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
    else:
        with st.form("signup_form"):
            st.markdown("#### 📝 Create Account")
            new_email = st.text_input("Email", placeholder="you@example.com")
            new_user  = st.text_input("Display name (optional)", placeholder="e.g. Aditya")
            new_pw    = st.text_input("Password", type="password",
                                      placeholder="Min 4 characters")
            new_pw2   = st.text_input("Confirm password", type="password",
                                      placeholder="Re‑enter password")
            submitted = st.form_submit_button("Create Account",
                                              use_container_width=True, type="primary")
            if submitted:
                if not new_email or not new_pw:
                    st.error("Email and password are required.")
                elif "@" not in new_email:
                    st.error("Please enter a valid email address.")
                elif len(new_pw) < 4:
                    st.error("Password must be at least 4 characters.")
                elif new_pw != new_pw2:
                    st.error("Passwords do not match.")
                else:
                    ok = create_account(new_email, new_pw, new_user)
                    if ok:
                        st.success("Account created! Switch to **Login** to sign in.")
                    else:
                        st.error("Email already registered — try logging in instead.")

    st.markdown("---")
    st.markdown(
        "<p style='text-align:center;color:#555;font-size:0.8rem;'>"
        "Your data is stored locally in SQLite. No cloud. No tracking.</p>",
        unsafe_allow_html=True,
    )


# ── Auth gate: show login or main app ───────────────────────
if not st.session_state.get("logged_in"):
    _show_login_page()
    st.stop()

# ── Logged‑in: show welcome bar + logout button ────────────
_acct = st.session_state["account"]
_display_name = _acct.get('username') or _acct['email'].split('@')[0]
_cols = st.columns([6, 1])
with _cols[0]:
    st.markdown(
        f"<div class='welcome-bar'>👋 Welcome back, "
        f"<b>{_display_name}</b></div>",
        unsafe_allow_html=True,
    )
with _cols[1]:
    if st.button("🚪 Logout", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ── Title ───────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center;'>🔮 Future Regret Prediction AI Agent</h1>"
    "<p style='text-align:center; color:#aaa;'>"
    "Analyze your lifestyle • Predict future regret • Get a corrective action plan"
    "</p>", unsafe_allow_html=True,
)

# ── Tabs ────────────────────────────────────────────────────
# Determine which tab to show after analysis
_tab_names = ["📝 Input Your Data", "📊 Analysis & Report", "📈 Weekly Tracking"]
_jump = st.session_state.pop("_jump_to_results", False)

tab_input, tab_results, tab_history = st.tabs(_tab_names)

# Inject JS to auto-click the "Analysis & Report" tab after analysis
if _jump:
    st.components.v1.html("""
        <script>
        const tabs = window.parent.document.querySelectorAll('button[data-baseweb="tab"]');
        if (tabs.length >= 2) { tabs[1].click(); }
        </script>
    """, height=0)

# =========================================================
# TAB 1 — User Input Form
# =========================================================
with tab_input:
    st.markdown("### 👤 Basic Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Name", placeholder="e.g. Aditya")
    with col2:
        age = st.number_input("Age", min_value=10, max_value=100, value=21)
    with col3:
        career_goal = st.selectbox("Career Goal", CAREER_OPTIONS)

    st.markdown("---")
    st.markdown("### ⏰ Daily Routine (hours per day)")
    c1, c2, c3 = st.columns(3)
    with c1:
        study_hours = st.slider("Study / Learning", 0.0, 16.0, 2.0, 0.5)
        screen_time = st.slider("Total Screen Time", 0.0, 16.0, 5.0, 0.5)
    with c2:
        sleep_hours = st.slider("Sleep", 0.0, 14.0, 7.0, 0.5)
        skill_learning = st.slider("Hands‑on Skill Practice", 0.0, 10.0, 1.0, 0.5)
    with c3:
        exercise = st.slider("Exercise", 0.0, 5.0, 0.5, 0.25)
        distraction = st.slider("Distraction (social media / gaming)", 0.0, 10.0, 2.0, 0.5)

    st.markdown("---")
    st.markdown("### 📅 Weekly Productivity")
    w1, w2, w3, w4 = st.columns(4)
    with w1:
        projects = st.number_input("Projects building", 0, 20, 0)
    with w2:
        courses = st.number_input("Courses learning", 0, 20, 1)
    with w3:
        consistency = st.slider("Consistency (1‑10)", 1, 10, 5)
    with w4:
        focus = st.slider("Focus level (1‑10)", 1, 10, 5)

    st.markdown("---")
    st.markdown("### 🪞 Self Reflection")
    r1, r2 = st.columns(2)
    with r1:
        doing_well = st.text_area("What are you doing well?", height=80)
        biggest_distraction = st.text_input("Biggest distraction")
    with r2:
        avoiding = st.text_area("What are you avoiding?", height=80)
        biggest_goal = st.text_input("Biggest goal")

    st.markdown("---")
    analyze_btn = st.button("🔍  Analyze My Future", type="primary", use_container_width=True)

# =========================================================
# Processing pipeline
# =========================================================
if analyze_btn:
    if not name.strip():
        st.error("Please enter your name.")
        st.stop()

    # Build profile
    profile = build_profile(
        name=name, age=age, career_goal=career_goal,
        study_hours=study_hours, screen_time=screen_time,
        sleep_hours=sleep_hours, skill_learning_hours=skill_learning,
        exercise_hours=exercise, distraction_hours=distraction,
        projects_building=projects, courses_learning=courses,
        consistency_level=consistency, focus_level=focus,
        doing_well=doing_well, avoiding=avoiding,
        biggest_distraction=biggest_distraction, biggest_goal=biggest_goal,
    )

    # Run pipeline
    analysis: AnalysisResult   = analyze(profile)
    regret:   RegretResult     = compute_regret(analysis)
    preds:    PredictionReport = predict(profile, regret)
    recs:     Recommendation   = recommend(profile, analysis, regret)

    # Persist
    uid = upsert_user(name, age, career_goal)
    save_snapshot(
        user_id=uid,
        daily=profile.to_dict()["daily"],
        weekly=profile.to_dict()["weekly"],
        reflection=profile.to_dict()["reflection"],
        result={
            "regret": regret.to_dict(),
            "analysis": analysis.to_dict(),
            "predictions": preds.to_dict(),
            "recommendations": recs.to_dict(),
        },
    )

    # Store in session for tab switching
    st.session_state["profile"]   = profile
    st.session_state["analysis"]  = analysis
    st.session_state["regret"]    = regret
    st.session_state["preds"]     = preds
    st.session_state["recs"]      = recs
    st.session_state["uid"]       = uid
    st.session_state["ran"]       = True
    st.session_state["_jump_to_results"] = True
    st.rerun()

# =========================================================
# TAB 2 — Results
# =========================================================
with tab_results:
    if not st.session_state.get("ran"):
        st.info("Fill in your data in the **Input** tab and click **Analyze My Future**.")
    else:
        profile:  UserProfile       = st.session_state["profile"]
        analysis: AnalysisResult    = st.session_state["analysis"]
        regret:   RegretResult      = st.session_state["regret"]
        preds:    PredictionReport  = st.session_state["preds"]
        recs:     Recommendation    = st.session_state["recs"]

        # ── Overall score card ──────────────────────────────
        sev = regret.overall_severity.lower()
        st.markdown(
            f"<div class='score-card score-{sev}'>"
            f"<h1 style='margin:0;font-size:3.5rem;'>{regret.overall_score:.0f}%</h1>"
            f"<h3 style='margin:0;'>Future Regret Score — {regret.overall_severity}</h3>"
            f"</div>", unsafe_allow_html=True,
        )

        # ── Sub‑scores radar chart ─────────────────────────
        st.markdown("<h3 class='section-hdr'>🎯 Sub‑Score Breakdown</h3>",
                    unsafe_allow_html=True)
        labels = list(analysis.sub_scores.keys())
        values = [analysis.sub_scores[l] for l in labels]
        labels_display = [l.replace("_", " ").title() for l in labels]

        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
        fig.patch.set_facecolor("#0e1117")
        ax.set_facecolor("#0e1117")
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        values_plot = values + [values[0]]
        angles += angles[:1]
        ax.fill(angles, values_plot, color="#3498db", alpha=0.25)
        ax.plot(angles, values_plot, color="#3498db", linewidth=2)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels_display, color="#ccc", fontsize=9)
        ax.set_ylim(0, 1)
        ax.tick_params(colors="#666")
        ax.spines["polar"].set_color("#333")
        ax.grid(color="#333")
        col_r1, col_r2 = st.columns([1, 1])
        with col_r1:
            st.pyplot(fig)
        with col_r2:
            for lbl, val in zip(labels_display, values):
                pct = val * 100
                color = "#2ecc71" if pct >= 70 else "#f1c40f" if pct >= 40 else "#e74c3c"
                st.markdown(
                    f"<div class='metric-box'>"
                    f"<b>{lbl}</b>: <span style='color:{color};font-size:1.2rem;'>"
                    f"{pct:.0f}%</span></div>",
                    unsafe_allow_html=True,
                )

        # ── Risk areas ──────────────────────────────────────
        st.markdown("<h3 class='section-hdr'>⚠️ Risk Areas</h3>",
                    unsafe_allow_html=True)
        risky = [c for c in regret.categories if c.score > 25]
        if not risky:
            st.success("No significant risk areas detected — great job!")
        else:
            for cat in sorted(risky, key=lambda c: -c.score):
                icon = {"Career Regret": "💼", "Skill Regret": "🛠️",
                        "Time Waste Regret": "⏳", "Health Regret": "❤️",
                        "Financial Regret": "💰"}.get(cat.name, "⚡")
                sev_color = {"LOW": "#2ecc71", "MODERATE": "#f1c40f",
                             "HIGH": "#e67e22", "CRITICAL": "#e74c3c"}.get(cat.severity, "#ccc")
                st.markdown(
                    f"<div class='metric-box' style='border-left-color:{sev_color};'>"
                    f"{icon} <b>{cat.name}</b> — "
                    f"<span style='color:{sev_color};'>{cat.severity} ({cat.score:.0f})</span>"
                    f"</div>", unsafe_allow_html=True,
                )
                if cat.contributing_gaps:
                    for g in cat.contributing_gaps:
                        st.caption(f"   ↳ {g}")

        # ── Future Predictions ──────────────────────────────
        st.markdown("<h3 class='section-hdr'>🔮 Future Predictions</h3>",
                    unsafe_allow_html=True)
        for scenario in preds.scenarios:
            risk_color = {"LOW": "🟢", "MODERATE": "🟡",
                          "HIGH": "🟠", "CRITICAL": "🔴"}.get(scenario.risk_level, "⚪")
            with st.expander(f"{risk_color} {scenario.horizon} — {scenario.risk_level}"):
                st.markdown(f"**{scenario.summary}**")
                for d in scenario.details:
                    st.markdown(f"- {d}")

        # ── Recommendations ─────────────────────────────────
        st.markdown("<h3 class='section-hdr'>🛑 What to STOP</h3>",
                    unsafe_allow_html=True)
        if recs.stop_doing:
            for a in recs.stop_doing:
                st.markdown(
                    f"<div class='metric-box stop-action'>"
                    f"<b>{a.action}</b><br/>"
                    f"<small style='color:#aaa;'>Priority: {a.priority} · {a.impact}</small>"
                    f"</div>", unsafe_allow_html=True,
                )
        else:
            st.success("Nothing critical to stop — keep it up!")

        st.markdown("<h3 class='section-hdr'>✅ What to START</h3>",
                    unsafe_allow_html=True)
        if recs.start_doing:
            for a in recs.start_doing:
                st.markdown(
                    f"<div class='metric-box start-action'>"
                    f"<b>{a.action}</b><br/>"
                    f"<small style='color:#aaa;'>Priority: {a.priority} · {a.impact}</small>"
                    f"</div>", unsafe_allow_html=True,
                )
        else:
            st.success("You're already doing the key activities — stay consistent!")

        st.markdown("<h3 class='section-hdr'>📆 Weekly Improvement Plan</h3>",
                    unsafe_allow_html=True)
        for step in recs.weekly_plan:
            st.markdown(f"- {step}")

        st.markdown("<h3 class='section-hdr'>🔁 Daily Habit Changes</h3>",
                    unsafe_allow_html=True)
        for habit in recs.daily_habits:
            st.markdown(f"- {habit}")

        # ── Motivational message ────────────────────────────
        st.markdown("---")
        st.markdown(
            f"<div style='background:#1a1a2e;padding:1.5rem;border-radius:1rem;"
            f"text-align:center;font-size:1.1rem;color:#f1c40f;'>"
            f"💡 {recs.motivational}</div>",
            unsafe_allow_html=True,
        )

# =========================================================
# TAB 3 — Weekly tracking / history
# =========================================================
with tab_history:
    st.markdown("### 📈 Weekly Tracking Dashboard")
    track_name = st.text_input("Enter your name to view history", key="track_name")
    if track_name:
        user = get_user(track_name.strip())
        if not user:
            st.warning("No records found for that name. Run an analysis first.")
        else:
            snapshots = get_user_snapshots(user["id"], limit=12)
            if not snapshots:
                st.info("No snapshots yet. Complete an analysis to start tracking.")
            else:
                st.success(f"Found {len(snapshots)} snapshot(s) for **{user['name']}**")

                # Score trend chart
                dates = [s["snapshot_date"] for s in reversed(snapshots)]
                scores = []
                for s in reversed(snapshots):
                    res = s.get("result", {})
                    reg = res.get("regret", {})
                    scores.append(reg.get("overall_score", 0))

                if len(scores) > 1:
                    fig2, ax2 = plt.subplots(figsize=(8, 3))
                    fig2.patch.set_facecolor("#0e1117")
                    ax2.set_facecolor("#0e1117")
                    ax2.plot(dates, scores, marker="o", color="#3498db", linewidth=2)
                    ax2.fill_between(dates, scores, alpha=0.15, color="#3498db")
                    ax2.set_ylabel("Regret Score", color="#ccc")
                    ax2.set_xlabel("Date", color="#ccc")
                    ax2.tick_params(colors="#999")
                    ax2.set_ylim(0, 100)
                    ax2.axhline(30, ls="--", color="#2ecc71", alpha=0.4, label="Low")
                    ax2.axhline(55, ls="--", color="#f1c40f", alpha=0.4, label="Moderate")
                    ax2.axhline(75, ls="--", color="#e74c3c", alpha=0.4, label="High")
                    ax2.legend(fontsize=8, facecolor="#0e1117", edgecolor="#333",
                               labelcolor="#ccc")
                    for spine in ax2.spines.values():
                        spine.set_color("#333")
                    plt.xticks(rotation=45, ha="right")
                    plt.tight_layout()
                    st.pyplot(fig2)
                else:
                    st.metric("Latest Regret Score", f"{scores[0]:.0f}%")

                # Latest snapshot details
                latest = snapshots[0]
                st.markdown("#### Latest Snapshot Details")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Date:** {latest['snapshot_date']}")
                    st.markdown(f"**Study hrs:** {latest['study_hours']}")
                    st.markdown(f"**Screen time:** {latest['screen_time']}")
                    st.markdown(f"**Sleep:** {latest['sleep_hours']}")
                with col_b:
                    st.markdown(f"**Skill learning:** {latest['skill_learning_hrs']}")
                    st.markdown(f"**Exercise:** {latest['exercise_hours']}")
                    st.markdown(f"**Distraction:** {latest['distraction_hours']}")
                    st.markdown(f"**Consistency:** {latest['consistency_level']}/10")

                # Progress comparison
                if len(snapshots) >= 2:
                    prev = snapshots[1]
                    st.markdown("#### Progress vs Previous Snapshot")
                    prev_res = prev.get("result", {}).get("regret", {})
                    curr_res = latest.get("result", {}).get("regret", {})
                    prev_score = prev_res.get("overall_score", 0)
                    curr_score = curr_res.get("overall_score", 0)
                    delta = curr_score - prev_score
                    delta_icon = "📉" if delta < 0 else "📈" if delta > 0 else "➡️"
                    delta_word = "improved" if delta < 0 else "worsened" if delta > 0 else "unchanged"
                    st.markdown(
                        f"{delta_icon} Regret score **{delta_word}** by "
                        f"**{abs(delta):.1f}** points ({prev_score:.0f} → {curr_score:.0f})"
                    )

# ── Footer ──────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#555;font-size:0.85rem;'>"
    "Future Regret Prediction AI Agent · Built with Python & Streamlit · "
    "Shallow AI · Rule‑based intelligence"
    "</p>", unsafe_allow_html=True,
)
