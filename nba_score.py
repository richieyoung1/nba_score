import requests
from bs4 import BeautifulSoup

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

        # Only completed games
        if not (pts.text and opp_pts.text and result.text):
            continue

        summary = f"{date.text}: {home_away} {opp.text} – {pts.text}-{opp_pts.text} ({result.text})"

        # Get box score link if available
        box_link_tag = row.find("td", {"data-stat": "box_score_text"}).find("a")
        box_score_url = "https://www.basketball-reference.com" + box_link_tag["href"] if box_link_tag else None

        recent_games.append((summary, box_score_url))

        if len(recent_games) == num_games:
            break

    return recent_games or [("❌ No completed games found.", None)]
def get_box_score(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return "❌ Failed to load box score page."

    soup = BeautifulSoup(response.content, "html.parser")

    output = [f"📊 Box Score: {url}"]

    # Get team names from page title
    title = soup.find("title")
    if title:
        output.append(f"🏀 {title.text.strip()}")

    # Get each team's total row from team stats tables
    tables = soup.find_all("table")
    for table in tables:
        if "box-" in table.get("id", "") and table.get("id", "").endswith("-game-basic"):
            team_name = table["id"].split("-")[1].upper()
            footer = table.find("tfoot")
            if footer:
                totals = [td.text.strip() for td in footer.find_all("td")]
                output.append(f"\n🟦 {team_name} Totals: {', '.join(totals)}")

    return "\n".join(output)


if __name__ == "__main__":
    get_recent_games()
