import random
import json
from collections import defaultdict

MIN_STR, MAX_STR = 30, 100

# ======================
# チーム
# ======================
class Team:
    def __init__(self, name, strength):
        self.name = name
        self.strength = strength

        self.history = []
        self.promotions = 0
        self.relegations = 0
        self.titles = 0

    def adjust(self, delta):
        self.strength = max(MIN_STR, min(MAX_STR, self.strength + delta))

    def record(self, season, league, rank):
        self.history.append({
            "season": season,
            "league": league,
            "rank": rank
        })

    def __repr__(self):
        return f"{self.name}({self.strength})"


# ======================
# 試合
# ======================
def play_match(a, b):
    if random.random() < a.strength / (a.strength + b.strength):
        win = a
        lose = b
    else:
        win = b
        lose = a

    win = win._replace(strength=win.strength + 1)
    return win, lose


# ======================
# ラウンドロビン
# ======================def round_robin(teams):
    teams = list(teams)
    wins = {t.name: 0 for t in teams}

    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            win, lose = play_match(teams[i], teams[j])
            wins[win.name] += 1

            if teams[i].name == win.name:
                teams[i] = win
            else:
                teams[j] = win

    teams.sort(key=lambda t: wins[t.name], reverse=True)
    return teams



# ======================
# ダブルエリミネーション
# ======================
def double_elimination(teams):
    losses = {t: 0 for t in teams}
    alive = teams[:]

    while True:
        active = [t for t in alive if losses[t] < 2]
        if len(active) <= 1:
            break

        random.shuffle(active)
        for i in range(0, len(active), 2):
            if i + 1 >= len(active):
                continue
            w, l = play_match(active[i], active[i + 1])
            losses[l] += 1

    return sorted(teams, key=lambda t: losses[t])


# ======================
# 上位リーグ（1スプリット）
# ======================
def upper_split(teams):
    random.shuffle(teams)
    g1, g2 = teams[:5], teams[5:]

    qualified = round_robin(g1)[:3] + round_robin(g2)[:3]
    return round_robin(qualified, double=True)


# ======================
# 下部リーグ（1スプリット）
# ======================
def lower_split(teams):
    random.shuffle(teams)
    g1, g2 = teams[:4], teams[4:]

    qualified = round_robin(g1, double=True)[:2] \
              + round_robin(g2, double=True)[:2]

    return double_elimination(qualified)


# ======================
# 入れ替え戦
# ======================
def promotion_tournament(lower_top6, upper_bottom2):
    ranking = double_elimination(lower_top6 + upper_bottom2)
    promoted = ranking[:2]

    for t in promoted:
        t.promotions += 1
        t.adjust(+3)

    for t in upper_bottom2:
        if t not in promoted:
            t.relegations += 1
            t.adjust(-3)

    return promoted


# ======================
# 履歴記録
# ======================
def record_upper(season, ranking):
    for i, t in enumerate(ranking, start=1):
        t.record(season, "upper", i)
        if i == 1:
            t.titles += 1


def record_lower(season, league_idx, ranking):
    for i, t in enumerate(ranking, start=1):
        t.record(season, f"lower_{league_idx}", i)


# ======================
# 保存／読込
# ======================
import json

def save_teams(filename, season, upper, lowers):
    data = {
        "season": season,
        "upper": [
            {"name": t.name, "strength": t.strength} for t in upper
        ],
        "lowers": [
            [
                {"name": t.name, "strength": t.strength} for t in league
            ] for league in lowers
        ]
    }
    with open(filename, "w") as f:
        json.dump(data, f)


def team_to_dict(t, league):
    return {
        "name": t.name,
        "strength": t.strength,
        "league": league,
        "history": t.history,
        "promotions": t.promotions,
        "relegations": t.relegations,
        "titles": t.titles
    }


def load_teams(filename):
    import json
    from collections import namedtuple

    Team = namedtuple("Team", ["name", "strength"])

    with open(filename) as f:
        data = json.load(f)

    season = data["season"]
    upper = [Team(**t) for t in data["upper"]]
    lowers = [
        [Team(**t) for t in league] for league in data["lowers"]
    ]

    return season, upper, lowers



# ======================
# シーズン
# ======================
def simulate_season(season, upper, lowers):
    for _ in range(2):  # 2スプリット
        upper_rank = upper_split(upper)
        lower_ranks = [lower_split(l) for l in lowers]

    record_upper(season, upper_rank)
    for i, r in enumerate(lower_ranks):
        record_lower(season, i, r)

    lower_top6 = [r[0] for r in lower_ranks] + [r[1] for r in lower_ranks]
    upper_bottom2 = upper_rank[-2:]

    promoted = promotion_tournament(lower_top6, upper_bottom2)

    for t in promoted:
        if t in upper_bottom2:
            continue
        upper.append(t)
        for league in lowers:
            if t in league:
                league.remove(t)

    for t in upper_bottom2:
        if t not in promoted:
            upper.remove(t)
            lowers[random.randint(0, 2)].append(t)


# ======================
# 初期化 & 実行
# ======================
def create_initial_teams():
    upper = [Team(f"U{i}", random.randint(70, 90)) for i in range(10)]
    lowers = [
        [Team(f"L{l}-{i}", random.randint(40, 70)) for i in range(8)]
        for l in range(3)
    ]
    return upper, lowers

