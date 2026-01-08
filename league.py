import random
import json

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

    def to_dict(self):
        return {
            "name": self.name,
            "strength": self.strength,
            "history": self.history,
            "promotions": self.promotions,
            "relegations": self.relegations,
            "titles": self.titles
        }

    @staticmethod
    def from_dict(d):
        t = Team(d["name"], d["strength"])
        t.history = d.get("history", [])
        t.promotions = d.get("promotions", 0)
        t.relegations = d.get("relegations", 0)
        t.titles = d.get("titles", 0)
        return t


# ======================
# 試合
# ======================
def play_match(a, b):
    if random.random() < a.strength / (a.strength + b.strength):
        win, lose = a, b
    else:
        win, lose = b, a

    win.adjust(+1)
    lose.adjust(-1)
    return win, lose


# ======================
# ラウンドロビン
# ======================
def round_robin(teams, double=False):
    teams = list(teams)
    wins = {t: 0 for t in teams}

    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            for _ in range(2 if double else 1):
                w, _ = play_match(teams[i], teams[j])
                wins[w] += 1

    return sorted(teams, key=lambda t: wins[t], reverse=True)


# ======================
# 保存 / 読込
# ======================
def save_teams(path, season, upper, lowers):
    data = {
        "season": season,
        "upper": [t.to_dict() for t in upper],
        "lowers": [[t.to_dict() for t in league] for league in lowers]
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_teams(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    season = data["season"]
    upper = [Team.from_dict(d) for d in data["upper"]]
    lowers = [
        [Team.from_dict(d) for d in league]
        for league in data["lowers"]
    ]
    return season, upper, lowers
