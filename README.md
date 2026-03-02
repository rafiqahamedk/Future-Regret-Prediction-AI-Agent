# 🔮 Future Regret Prediction AI Agent

> A shallow AI agent that predicts potential future regret based on your current habits, skills, and lifestyle decisions — then gives you a corrective action plan.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red?logo=streamlit)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ⚡ Why This Project?

| Problem | Our Solution |
|---------|-------------|
| People don't realize small daily habits compound into major life regret | **Quantifies regret risk** with a 0–100 score |
| No tool connects daily routines to long-term career goals | **Career-specific benchmarks** for 7 different paths |
| Generic advice doesn't account for individual lifestyle | **Personalized gap analysis** based on YOUR data |
| People know what to do but not what to STOP | **STOP/START framework** with priority & impact |
| Progress is invisible without tracking | **Weekly snapshots** with trend charts & comparison |

### What Makes This Unique

- 🧠 **No API keys, no cloud, no GPU** — runs 100% offline on any machine
- 🎯 **Career-aware intelligence** — a Software Engineer gets different advice than a Govt Job aspirant
- 📉 **Time-horizon simulation** — see how today's habits look in 3 months vs 2 years
- 🔒 **Privacy-first** — all data stays in a local SQLite file, nothing leaves your machine
- 💡 **Explainable AI** — every score and recommendation traces back to specific habit gaps

---

## 🧠 What It Does

People make daily decisions about time, learning, habits, and careers without understanding long-term consequences. **Most regret in life comes from repeated small poor decisions, not a single failure.**

This AI agent answers one powerful question:

> *"If my current lifestyle continues, what will I regret in the future?"*

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **🔐 Authentication** | Email-based login/signup with hashed passwords |
| **📋 Lifestyle Analysis** | Collects daily routine, productivity, and self-reflection data |
| **🎯 Goal vs Action Comparison** | Compares habits against career-specific benchmarks |
| **📊 Regret Score (0–100)** | Weighted composite score across 5 dimensions |
| **⚠️ Regret Type Detection** | Career, Skill, Time Waste, Health, Financial |
| **🔮 Future Scenario Simulation** | Predictions for 3 months, 6 months, 1 year, 2 years |
| **✅ Correction Generator** | What to STOP, what to START, weekly & daily plans |
| **📈 Weekly Tracking** | Persistent history with progress comparison charts |
| **🚀 Auto-redirect** | Jumps to results tab automatically after analysis |

---

## 🏗️ Architecture

```
                        ┌─────────────────┐
                        │   Login/Signup   │
                        │  (Email + SHA256)│
                        └────────┬────────┘
                                 │
┌─────────────┐     ┌───────────▼──┐     ┌────────────────┐
│  user_input  │────▶│   analyzer    │────▶│  regret_engine  │
│  (Module 1)  │     │   (Module 2)  │     │  (Module 3)     │
└─────────────┘     └──────────────┘     └───────┬────────┘
                                                  │
                    ┌──────────────┐     ┌────────▼───────┐
                    │ recommender  │◀────│   predictor     │
                    │  (Module 5)  │     │   (Module 4)    │
                    └──────┬───────┘     └────────────────┘
                           │
                    ┌──────▼───────┐     ┌────────────────┐
                    │   dashboard   │◀───▶│   database      │
                    │  (Module 6)   │     │   (SQLite)      │
                    └──────────────┘     └────────────────┘
```

### Project Files

| File | Purpose |
|------|---------|
| `config.py` | Constants, scoring weights, career benchmarks, thresholds |
| `database.py` | SQLite persistence — accounts, users, snapshots + auth |
| `user_input.py` | Dataclasses & validation for user profiles |
| `analyzer.py` | Gap analysis comparing habits vs career-specific ideals |
| `regret_engine.py` | Weighted 0–100 regret scoring & category classification |
| `predictor.py` | Time-horizon future scenario generation |
| `recommendation.py` | Rule-based corrective action generator |
| `dashboard.py` | Streamlit UI — login, 3 tabs, charts, auto-redirect |
| `requirements.txt` | Python dependencies |
| `README.md` | Project documentation |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### 1. Clone & Install

```bash
git clone <repo-url>
cd Shallow_AI_Agent
pip install -r requirements.txt
```

### 2. Run

```bash
streamlit run dashboard.py
# or if streamlit is not on PATH:
python -m streamlit run dashboard.py
```

### 3. Use

1. Open **http://localhost:8501** in your browser
2. **Sign up** with your email and password
3. **Log in** with your credentials
4. Fill in your lifestyle data in the **Input** tab
5. Click **🔍 Analyze My Future** → auto-redirects to results
6. View your regret score, risk areas, predictions, and action plan
7. Come back weekly to track progress in the **Weekly Tracking** tab

---

## 🖥️ Dashboard Overview

### 🔐 Login Page
- Email + password authentication
- Sign up with email (required), display name (optional), password
- Passwords hashed with SHA-256 — no plaintext storage
- Session-based auth with logout button
- All data stored locally (no cloud, no tracking)

### 📝 Tab 1 — Input Your Data
- Basic info (name, age, career goal — 7 career paths supported)
- Daily routine sliders (study, screen time, sleep, exercise, distractions)
- Weekly productivity metrics (projects, courses, consistency, focus)
- Self-reflection text fields (strengths, avoidances, distractions, goals)

### 📊 Tab 2 — Analysis & Report
- **Regret Score** — large color-coded card (0–100%)
  - 🟢 0–30 LOW | 🟡 31–55 MODERATE | 🟠 56–75 HIGH | 🔴 76–100 CRITICAL
- **Radar chart** — 5 sub-scores visualized (Consistency, Productivity, Distraction, Goal Alignment, Learning Effort)
- **Risk areas** — severity badges with contributing gap details
- **Future predictions** — expandable cards for 3m / 6m / 1y / 2y horizons
- **🛑 STOP doing** — high-priority actions to eliminate
- **✅ START doing** — high-priority actions to adopt
- **📆 Weekly plan** — structured Mon–Sun schedule
- **🔁 Daily habits** — micro-routine changes
- **💡 Motivational feedback** — personalized AI message

### 📈 Tab 3 — Weekly Tracking
- Historical regret score trend chart with threshold lines
- Snapshot-over-snapshot progress comparison (improved / worsened)
- Detailed view of latest snapshot data
- Persistent across sessions via SQLite

---

## ⚙️ Intelligence Logic

### How the AI Thinks

The agent uses **rule-based intelligence** — no deep learning, no API calls, no GPU required.

```
1. Collect user data (daily habits, weekly metrics, self-reflection)
2. Load career-specific benchmarks (ideal study hrs, max screen time, etc.)
3. Compute gaps between current habits and ideal benchmarks
4. Score each gap by severity (LOW → CRITICAL)
5. Aggregate into 5 weighted sub-scores
6. Calculate final Regret Score (0–100)
7. Classify regret types (Career, Skill, Time Waste, Health, Financial)
8. Simulate future scenarios with time-horizon decay multipliers
9. Generate STOP/START recommendations using rule engine
10. Output complete report with motivational feedback
```

### Scoring Formula

```
Future Regret Score = Σ (1 − sub_score_i) × weight_i × 100
```

| Sub-Score | Weight | What It Measures |
|-----------|--------|-----------------|
| Consistency | 0.20 | Self-rated consistency level (1–10) |
| Productivity | 0.20 | Self-rated focus level (1–10) |
| Distraction | 0.20 | Screen time + distraction hours vs limits |
| Goal Alignment | 0.25 | Study + coding hours vs career benchmarks |
| Learning Effort | 0.15 | Skill learning + courses + projects vs benchmarks |

### Career Benchmarks

The agent ships with ideal daily/weekly benchmarks for **7 career paths**:

| Career | Study hrs | Coding hrs | Max Screen | Max Distraction | Min Sleep |
|--------|-----------|-----------|------------|----------------|-----------|
| Software Engineer | 3 | 3 | 3 | 1 | 7 |
| AI/ML Engineer | 4 | 3 | 3 | 1 | 7 |
| Data Scientist | 3.5 | 2.5 | 3 | 1 | 7 |
| Government Job | 6 | 0 | 2 | 1 | 7 |
| Business / Startup | 2 | 1 | 3 | 1.5 | 7 |
| Freelancer | 2 | 3 | 3 | 1 | 7 |
| Other | 2 | 1 | 3 | 1.5 | 7 |

### Regret Categories

| Type | Triggered By |
|------|-------------|
| 🏢 Career Regret | Low study hours, few projects, poor consistency |
| 🛠️ Skill Regret | Low skill practice, no courses, learning gaps |
| ⏳ Time Waste Regret | High screen time, excessive distraction hours |
| ❤️ Health Regret | Sleep deficit, no exercise |
| 💰 Financial Regret | Derived from career + skill risk compounding |

### Future Simulation

Predictions scale across time horizons using multipliers:

| Horizon | Multiplier | Effect |
|---------|-----------|--------|
| 3 months | 0.6× | Early warning signals |
| 6 months | 0.8× | Noticeable gaps forming |
| 1 year | 1.0× | Full impact of current habits |
| 2 years | 1.2× | Compounded consequences |

---

## 📂 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Streamlit | Rapid prototyping, clean UI, built-in widgets |
| Backend | Python (pure) | No frameworks needed, lightweight |
| Database | SQLite | Zero-config, file-based, portable |
| Charts | Matplotlib + NumPy | Radar charts, trend lines, publication-quality |
| Auth | SHA-256 hashing | Simple, no external auth dependencies |
| AI Type | Rule-based / Shallow AI | Explainable, fast, no GPU required |

---

## 🎯 Use Cases

- **🎓 Students** preparing for placements — track study habits vs career requirements
- **💼 Professionals** evaluating work-life balance and growth trajectory
- **🏆 Hackathon projects** — unique concept, real-world impact, portfolio-ready
- **🧘 Self-improvement** — weekly check-ins with data-driven honest feedback
- **📊 Career coaches** — use as a diagnostic tool for mentoring sessions

---

## 🛣️ Roadmap (Future Enhancements)

- [ ] PDF report generation & download
- [ ] Voice input support
- [ ] Email reminders for weekly check-ins
- [ ] AI motivational quotes (dynamic)
- [ ] "Reality Check" mode (brutally honest analysis)
- [ ] Progress badges & streak tracking
- [ ] Multi-language support
- [ ] REST API (FastAPI) for mobile/web integration
- [ ] Export data as CSV/JSON

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT — free to use, modify, and distribute.

---

## 💬 Sample Output

```
────────────────────────────────────────
 FUTURE REGRET SCORE: 72%  [HIGH]
────────────────────────────────────────

 RISK AREAS:
  🏢 Career Regret — HIGH (65)
  ⏳ Time Waste Regret — CRITICAL (90)
  🛠️ Skill Regret — MODERATE (40)

 FUTURE WARNING (1 year):
  If this routine continues for 1 year,
  you risk missing important Software
  Engineer milestones.

 RECOMMENDED CHANGES:
  🛑 STOP: Reduce social media from 3.0 hrs to under 1 hr/day
  🛑 STOP: Reduce total screen time from 6.0 hrs
  ✅ START: Add 1.0 hrs of focused study per day
  ✅ START: Dedicate 2.0 more hrs/day to hands-on skill practice
  ✅ START: Build at least 1 project per month
  ✅ START: Use a habit tracker — commit to 5+ consistent days/week
────────────────────────────────────────
```

---

*Built with ❤️ as a Shallow AI Agent — proving that intelligence doesn't need deep learning, just smart rules and good design.*
