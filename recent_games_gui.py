import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, scrolledtext

# --- NBA TEAM ABBREVIATIONS ---
NBA_TEAMS = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BRK",
    "Charlotte Hornets": "CHO", "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC", "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA", "Milwaukee Bucks": "MIL", "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP", "New York Knicks": "NYK", "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHO",
    "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR", "Utah Jazz": "UTA", "Washington Wizards": "WAS"
}

# --- SCRAPER: GAME RESULTS + BOX SCORE URL ---
def get_recent_games(team_abbr="TOR", year="2025", num_games=5):
    url = f"https://www.basketball-reference.com/teams/{team_abbr}/{year}_games.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return [("❌ Failed to load data.", None)]

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", {"id": "games"})
    if not table:
        return [("❌ Game table not found.", None)]

    rows = table.tbody.find_all("tr")
    recent_games = []

    for row in reversed(rows):
        if row.get("class") == ["thead"]:
            continue

        date = row.find("td", {"data-stat": "date_game"})
        result = row.find("td", {"data-stat": "game_result"})
        opp = row.find("td", {"data-stat": "opp_name"})
        pts = row.find("td", {"data-stat": "pts"})
        opp_pts = row.find("td", {"data-stat": "opp_pts"})
        home_away = "vs" if row.find("td", {"data-stat": "game_location"}).text == "" else "@"

        # Skip upcoming games
        if not (pts.text and opp_pts.text and result.text):
            continue

        summary = f"{date.text}: {home_away} {opp.text} – {pts.text}-{opp_pts.text} ({result.text})"
        link_cell = row.find("td", {"data-stat": "box_score_text"}).find("a")
        box_link = "https://www.basketball-reference.com" + link_cell["href"] if link_cell else None

        recent_games.append((summary, box_link))
        if len(recent_games) == num_games:
            break

    return recent_games or [("❌ No completed games found.", None)]

# --- SCRAPER: BOX SCORE PAGE ---
def get_box_score(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return "❌ Failed to load box score page."

    soup = BeautifulSoup(response.content, "html.parser")
    output = [f"📊 Box Score: {url}"]

    title = soup.find("title")
    if title:
        output.append(f"🏀 {title.text.strip()}\n")

    stat_labels = [
        "MIN", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "FT", "FTA", "FT%",
        "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"
    ]

    team_stats = {}

    # Scrape totals from table footers
    tables = soup.find_all("table")
    for table in tables:
        if "box-" in table.get("id", "") and table.get("id", "").endswith("-game-basic"):
            team_abbr = table["id"].split("-")[1].upper()
            footer = table.find("tfoot")
            if footer:
                totals = [td.text.strip() for td in footer.find_all("td")]
                team_stats[team_abbr] = totals

    if len(team_stats) != 2:
        return "⚠️ Could not find both teams' totals."

    team1, team2 = list(team_stats.keys())
    stats1 = team_stats[team1]
    stats2 = team_stats[team2]

    header = f"{'🟦 ' + team1 + ' Totals':<30} {'🟦 ' + team2 + ' Totals':<30}"
    output.append(header)
    output.append(f"{'-' * 28}    {'-' * 28}")

    for i in range(len(stat_labels)):
        left = f"{stat_labels[i]}: {stats1[i]:<5}"
        right = f"{stat_labels[i]}: {stats2[i]}"
        row = f"{left:<30} {right:<30}"
        output.append(row)

    return "\n".join(output)




# --- GUI LOGIC ---
def fetch_and_display_games():
    team = selected_team.get()
    abbr = NBA_TEAMS.get(team, "TOR")
    games = get_recent_games(abbr)
    recent_games.clear()
    game_listbox.delete(0, tk.END)

    for i, (summary, link) in enumerate(games):
        recent_games.append((summary, link))
        game_listbox.insert(tk.END, summary)

def on_game_select(event):
    selection = game_listbox.curselection()
    if not selection:
        return
    index = selection[0]
    summary, box_link = recent_games[index]
    if box_link:
        box_data = get_box_score(box_link)
        output_box.delete(1.0, tk.END)
        output_box.insert(tk.END, box_data)
    else:
        output_box.insert(tk.END, "❌ No box score available.")

# --- GUI SETUP ---
window = tk.Tk()
window.title("NBA Game Viewer + Box Scores")
window.geometry("700x600")

selected_team = tk.StringVar(window)
selected_team.set("Toronto Raptors")

tk.Label(window, text="Select NBA Team", font=("Helvetica", 14, "bold")).pack(pady=10)
team_dropdown = ttk.Combobox(window, textvariable=selected_team, values=list(NBA_TEAMS.keys()), state="readonly", width=30)
team_dropdown.pack()

tk.Button(window, text="Fetch Recent Games", command=fetch_and_display_games).pack(pady=5)

# Clickable list of games
recent_games = []
game_listbox = tk.Listbox(window, width=80, height=8)
game_listbox.pack(pady=10)
game_listbox.bind("<<ListboxSelect>>", on_game_select)

# Scrollable output for box score
output_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=85, height=20, font=("Courier New", 10))
output_box.pack(padx=10, pady=10)

window.mainloop()
