<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&height=220&color=0:d4400a,40:f07040,100:1a1a18&text=Ping%20Pong%20Tournament%20Manager&fontColor=ffffff&fontSize=40&fontAlignY=38&desc=Fast%20brackets.%20Clean%20scores.%20A%20better%20cup%20dashboard.&descAlignY=58" alt="Ping Pong Tournament Manager banner" width="100%" />
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Plus+Jakarta+Sans&weight=700&size=24&pause=1200&center=true&vCenter=true&width=900&lines=Import+teams+from+CSV;Generate+a+full+knockout+bracket;Track+scores+and+auto-advance+winners;Show+matches%2C+bracket%2C+and+rankings+in+the+browser" alt="Animated project summary" />
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.x-1a5fa0?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Frontend" src="https://img.shields.io/badge/Frontend-HTML%20%2F%20CSS%20%2F%20JS-d4400a?style=for-the-badge&logo=html5&logoColor=white">
  <img alt="Tournament" src="https://img.shields.io/badge/Tournament-Single%20Elimination-1a7f4e?style=for-the-badge">
  <img alt="Data" src="https://img.shields.io/badge/Data-JSON%20%2B%20CSV-b07800?style=for-the-badge">
  <img alt="Status" src="https://img.shields.io/badge/Status-Ready%20for%20Match%20Day-111111?style=for-the-badge">
</p>

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&color=ffffff00&height=2&section=header" alt="" width="100%" />
</p>

A lightweight tournament management project for organizing and displaying a ping pong cup. The project combines:

- A Python script to import teams, generate the knockout bracket, schedule matches, and record results
- A static web dashboard to show matches, bracket progress, and team rankings
- JSON-based persistence so the tournament state can be reused between sessions

The current sample data is set up for a 32-team tournament and includes 5 rounds.

<p align="center">
  <img alt="divider" src="https://capsule-render.vercel.app/api?type=soft&color=0:1a1a18,100:d4400a&height=90&section=header&text=Match%20Flow&fontSize=28&fontColor=ffffff&animation=fadeIn" width="100%" />
</p>

<p align="center">
  <img alt="CSV" src="https://img.shields.io/badge/teams.csv-Player%20import-e8f0fa?style=flat-square&labelColor=1a5fa0&color=e8f0fa">
  <img alt="arrow" src="https://img.shields.io/badge/-%E2%86%92-ffffff?style=flat-square&labelColor=ffffff&color=ffffff">
  <img alt="manager" src="https://img.shields.io/badge/manager.py-Bracket%20%2B%20scheduling-fff0ea?style=flat-square&labelColor=d4400a&color=fff0ea">
  <img alt="arrow" src="https://img.shields.io/badge/-%E2%86%92-ffffff?style=flat-square&labelColor=ffffff&color=ffffff">
  <img alt="json" src="https://img.shields.io/badge/tournament_data.json-Saved%20state-e8f5ee?style=flat-square&labelColor=1a7f4e&color=e8f5ee">
  <img alt="arrow" src="https://img.shields.io/badge/-%E2%86%92-ffffff?style=flat-square&labelColor=ffffff&color=ffffff">
  <img alt="frontend" src="https://img.shields.io/badge/index.html-Live%20dashboard-fdf5e0?style=flat-square&labelColor=b07800&color=fdf5e0">
</p>

## Features

- Imports teams from a CSV file
- Creates a full single-elimination bracket automatically
- Handles bye slots when the number of teams is not a power of two
- Schedules round 1 matches starting from a configured date
- Propagates winners to the next round
- Recalculates team statistics from saved match data
- Displays matches, bracket, and rankings in the browser

## Project Structure

```text
.
|-- index.html              # Frontend dashboard
|-- manager.py              # Tournament generator and match update tool
|-- server.py               # Starts a local static server on port 8000
|-- teams.csv               # Input team/player list
|-- tournament_data.json    # Generated tournament data
`-- Visuals/                # Project visuals/assets
```

## Requirements

- Python 3
- `pandas`

Install the Python dependency with:

```bash
pip install pandas
```

## Input Data

`teams.csv` should contain team/player information. The current script expects these columns:

- `Player1 Name`
- `Player2 Name`
- `Track`

Other columns may exist in the file, but these are the ones used by `manager.py`.

## How It Works

### 1. Generate or load tournament data

Run:

```bash
python manager.py
```

What happens:

- If `tournament_data.json` already exists, the script loads it and recalculates stats
- If the JSON file does not exist, the script imports teams from `teams.csv`, creates the bracket, schedules matches, and saves the generated data
- The script then opens an interactive terminal flow to update completed match scores

### 2. View the tournament in the browser

You can start the local web server with either command:

```bash
python server.py
```

or

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

The dashboard reads directly from `tournament_data.json`, so any score updates saved by `manager.py` will appear in the frontend after refresh.

## Tournament Configuration

The main settings are defined near the top of `manager.py`:

- `CSV_FILE`: source CSV file
- `JSON_FILE`: saved tournament state
- `START_DATE`: first scheduling date
- `MATCH_DURATION`: spacing between same-day matches in minutes
- `MATCHES_PER_DAY`: maximum matches scheduled per day

## Frontend Views

The dashboard in `index.html` contains three main views:

- `Matches`: grouped match list with status and schedule
- `Bracket`: round-by-round tournament tree
- `Rankings`: team standings based on saved statistics

## Output Data

`tournament_data.json` stores:

- Teams and player names
- Track information
- Match schedule
- Scores
- Winners
- Team statistics such as wins, goals for, goals against, and matches played

This file acts as the single source of truth for the frontend.

## Typical Workflow

1. Update `teams.csv` with the participating teams
2. Run `python manager.py` to create or update the tournament
3. Enter match scores in the terminal as matches are played
4. Run `python server.py` and open the dashboard in the browser
5. Refresh the page to see the latest bracket and rankings

## Notes

- Round 1 is scheduled automatically; later rounds are scheduled when both teams are known
- Friday and Saturday are skipped by the scheduler
- The project currently uses a single-elimination format
- `tournament_data.json` is generated data and can be regenerated from `teams.csv` when starting a new tournament

## Future Improvements

- Add a `requirements.txt` file
- Add score validation rules
- Support double elimination or group stages
- Add admin controls directly in the web UI
- Export results to PDF or Excel
