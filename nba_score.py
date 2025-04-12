import requests
from bs4 import BeautifulSoup
from fantasy import calculate_fantasy_score

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

        if not (pts.text and opp_pts.text and result.text):
            continue

        summary = f"{date.text}: {home_away} {opp.text} – {pts.text}-{opp_pts.text} ({result.text})"
        box_tag = row.find("td", {"data-stat": "box_score_text"}).find("a")
        box_link = "https://www.basketball-reference.com" + box_tag["href"] if box_tag else None

        recent_games.append((summary, box_link))
        if len(recent_games) == num_games:
            break

    return recent_games or [("❌ No completed games found.", None)]


def parse_player_stats(table):
    players = []
    rows = table.find("tbody").find_all("tr")
    for row in rows:
        if row.get("class") == ["thead"]:
            continue

        name_tag = row.find("th", {"data-stat": "player"})
        if not name_tag or "Did Not Play" in row.text:
            continue

        mp_cell = row.find("td", {"data-stat": "mp"})
        if not mp_cell:
            continue

        name = name_tag.text.strip()
        minutes = mp_cell.text

        def get_stat(stat):
            cell = row.find("td", {"data-stat": stat})
            return int(cell.text) if cell and cell.text.isdigit() else 0

        pts = get_stat("pts")
        reb = get_stat("trb")
        ast = get_stat("ast")
        tov = get_stat("tov")
        blk = get_stat("blk")
        stl = get_stat("stl")
        fg3m = get_stat("fg3")
        techs = 0  # Placeholder if not found on the page
        flagrants = 0  # Placeholder

        fantasy_score = calculate_fantasy_score(pts, reb, ast, stl, blk, tov, fg3m, techs, flagrants)

        stat_line = f"{name:<22} | {minutes:>5} | {pts:>3} | {reb:>3} | {ast:>3} | {tov:>2} | {blk:>3} | {stl:>3} | {fantasy_score:>6.1f}"
        players.append(stat_line)

    return players


def get_box_score(url, scoring=None):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return ("❌ Failed to load box score page.", "")

    soup = BeautifulSoup(response.content, "html.parser")
    team_output = []
    player_output = []

    title = soup.find("title")
    if title:
        team_output.append(f"🏀 {title.text.strip()}\n")

    stat_labels = [
        "MIN", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "FT", "FTA", "FT%",
        "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"
    ]

    team_stats = {}
    player_stats = {}

    tables = soup.find_all("table")
    for table in tables:
        if "box-" in table.get("id", "") and table.get("id", "").endswith("-game-basic"):
            team_abbr = table["id"].split("-")[1].upper()

            # Team totals
            footer = table.find("tfoot")
            if footer:
                totals = [td.text.strip() for td in footer.find_all("td")]
                team_stats[team_abbr] = totals

            # Player stats
            player_stats[team_abbr] = parse_player_stats(table)

    if len(team_stats) != 2:
        return ("⚠️ Could not find both teams' totals.", "")

    team1, team2 = list(team_stats.keys())
    stats1 = team_stats[team1]
    stats2 = team_stats[team2]

    header = f"{'🟦 ' + team1 + ' Totals':<30} {'🟦 ' + team2 + ' Totals':<30}"
    team_output.append(header)
    team_output.append(f"{'-' * 28}    {'-' * 28}")

    for i in range(len(stat_labels)):
        left = f"{stat_labels[i]}: {stats1[i]:<5}" if i < len(stats1) else ""
        right = f"{stat_labels[i]}: {stats2[i]}" if i < len(stats2) else ""
        row = f"{left:<30} {right:<30}"
        team_output.append(row)

    # Player headers
    player_output.append(f"\n📋 {team1} Players")
    player_output.append("Player Name            | MIN | PTS | REB | AST | TO | BLK | STL | FPts")
    player_output.append("-" * 72)
    player_output.extend(player_stats[team1])

    player_output.append(f"\n📋 {team2} Players")
    player_output.append("Player Name            | MIN | PTS | REB | AST | TO | BLK | STL | FPts")
    player_output.append("-" * 72)
    player_output.extend(player_stats[team2])

    return ("\n".join(team_output), "\n".join(player_output))
