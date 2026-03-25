<div align="center">

# 🏓 Ping Pong Tournament Manager

**A single-elimination bracket system with a live web viewer.**

Generate brackets · Enter scores · Track standings — all from the terminal.

[![Python](https://img.shields.io/badge/Python_3-backend-306998?style=for-the-badge&logo=python&logoColor=white)](.)
[![HTML](https://img.shields.io/badge/HTML%2FCSS%2FJS-frontend-e34c26?style=for-the-badge&logo=html5&logoColor=white)](.)

</div>

---

## What It Does

A Python CLI that manages a full **single-elimination ping pong tournament** — from team registration to final results. Comes with a clean, responsive web page to view matches, brackets, and rankings live.

- Register teams via CSV (doubles format: two players per team)
- Auto-generates the full bracket tree with bye handling
- Enter match scores through an interactive CLI — winners auto-advance
- Smart scheduling that skips configurable off-days
- Live rankings sorted by wins → point difference → points scored
- Responsive web viewer — works on any device, zero dependencies

---

## Quick Start

```bash
# 1 — Add your teams to teams.csv (see format below)

# 2 — Generate the bracket
python manager.py

# 3 — Launch the web viewer
python server.py          # opens http://localhost:8000

# 4 — Enter match results (interactive)
python manager.py         # select match → enter scores → winner advances
```

---

## CSV Format

```csv
Timestamp,Player1 Name,Player1 Phone,Player2 Name,Player2 Phone,Track
2026/03/01,Alice,0100000001,Bob,0100000002,Engineering
```

| Column | Description |
|---|---|
| `Timestamp` | Registration date |
| `Player1 Name` / `Player2 Name` | Player names |
| `Player1 Phone` / `Player2 Phone` | Contact numbers |
| `Track` | Team category / group (optional) |

---

## Project Structure

```
├── manager.py              # CLI — bracket generation, score entry, scheduling
├── index.html              # Web viewer — matches, bracket tree, rankings
├── server.py               # Starts a local HTTP server & opens the browser
├── teams.csv               # Team registration data
└── tournament_data.json    # Tournament state (auto-generated)
```

---

## Configuration

Edit the top of `manager.py` to customize:

```python
CSV_FILE       = 'teams.csv'
JSON_FILE      = 'tournament_data.json'
START_DATE     = "2026-04-01"      # First match day
MATCHES_PER_DAY = 2                # Max matches scheduled per day
```

---

## Hosting

| Method | How |
|---|---|
| **Local** | `python server.py` or `python -m http.server 8000` |
| **LAN** | Share `http://YOUR_IP:8000` on event day |
| **GitHub Pages** | Push `index.html` + `tournament_data.json` |
| **ngrok** | `ngrok http 8000` for a public URL |

---

## Tech

**Python 3** · **pandas** · **Vanilla HTML / CSS / JS** · **Plus Jakarta Sans**

---

<div align="center">

*Made with ❤️ for ping pong tournaments everywhere*

</div>
