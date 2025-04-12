import tkinter as tk
from tkinter import ttk, scrolledtext
from nba_score import get_recent_games, get_box_score

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

scoring_system = {"PTS": 1.0, "REB": 1.2, "AST": 1.5, "TOV": 1.0}

# GUI setup
window = tk.Tk()
window.title("NBA Game Viewer + Box Scores")
window.geometry("880x720")

selected_team = tk.StringVar(window)
selected_team.set("Toronto Raptors")

tk.Label(window, text="Select NBA Team", font=("Helvetica", 14, "bold")).pack(pady=10)
team_dropdown = ttk.Combobox(window, textvariable=selected_team, values=list(NBA_TEAMS.keys()), state="readonly", width=30)
team_dropdown.pack()

tk.Button(window, text="Fetch Recent Games", command=lambda: fetch_and_display_games()).pack(pady=5)

recent_games = []
game_listbox = tk.Listbox(window, width=85, height=6)
game_listbox.pack(pady=10)

team_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=105, height=14, font=("Courier New", 10))
tk.Label(window, text="Team Stats", font=("Helvetica", 12, "bold")).pack()
team_box.pack(padx=10, pady=5)

player_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=105, height=22, font=("Courier New", 10))
tk.Label(window, text="Player Stats", font=("Helvetica", 12, "bold")).pack()
player_box.pack(padx=10, pady=5)

def fetch_and_display_games():
    team = selected_team.get()
    abbr = NBA_TEAMS.get(team, "TOR")
    games = get_recent_games(abbr)
    recent_games.clear()
    game_listbox.delete(0, tk.END)

    for summary, link in games:
        recent_games.append((summary, link))
        game_listbox.insert(tk.END, summary)

def on_game_select(event):
    selection = game_listbox.curselection()
    if not selection:
        return
    index = selection[0]
    summary, box_link = recent_games[index]
    if box_link:
        team_data, player_data = get_box_score(box_link, scoring_system)
        team_box.delete(1.0, tk.END)
        player_box.delete(1.0, tk.END)
        team_box.insert(tk.END, team_data)
        player_box.insert(tk.END, player_data)
    else:
        team_box.insert(tk.END, "❌ No box score available.")
        player_box.insert(tk.END, "")

game_listbox.bind("<<ListboxSelect>>", on_game_select)

window.mainloop()
