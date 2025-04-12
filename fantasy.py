def calculate_fantasy_score(pts, reb, ast, stl, blk, tov, fg3m, techs=0, flagrants=0):
    """
    Calculates fantasy basketball score based on advanced custom scoring.
    
    Scoring System:
    - Points: +0.5
    - Rebounds: +1
    - Assists: +1
    - Steals: +2
    - Blocks: +2
    - Turnovers: -1
    - 3PT Made: +0.5
    - Technical Fouls: -2
    - Flagrant Fouls: -2
    - Double-double: +1
    - Triple-double: +2
    - 40+ Points: +2
    - 50+ Points: +2
    """

    # Core scoring
    score = (
        pts * 0.5 +
        reb * 1 +
        ast * 1 +
        stl * 2 +
        blk * 2 +
        fg3m * 0.5 -
        tov * 1 -
        techs * 2 -
        flagrants * 2
    )

    # Bonus: Double-double and Triple-double
    categories_hit = sum([
        pts >= 10,
        reb >= 10,
        ast >= 10,
        stl >= 10,
        blk >= 10
    ])
    if categories_hit >= 3:
        score += 3  # 1 for double-double + 2 for triple-double
    elif categories_hit == 2:
        score += 1  # double-double bonus only

    # Bonus: High scoring games
    if pts >= 50:
        score += 4  # 2 for 40+ and additional 2 for 50+
    elif pts >= 40:
        score += 2

    return round(score, 1)
