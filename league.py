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
            "rank": rank,
            "strength": self.strength
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
    teams = teams[:]
    random.shuffle(teams)
    g1, g2 = teams[:5], teams[5:]

    qualified = round_robin(g1)[:3] + round_robin(g2)[:3]
    return round_robin(qualified, double=True)


# ======================
# 下部リーグ（1スプリット）
# ======================
def lower_split(teams):
    teams = teams[:]
    random.shuffle(teams)
    g1, g2 = teams[:4], teams[4:]

    qualified = (
        round_robin(g1, double=True)[:2]
        + round_robin(g2, double=True)[:2]
    )

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

# ======================
# シーズン進行
# ======================
def simulate_season(season, upper, lowers):
    # 上位リーグ
    upper_rank = upper_split(upper)
    for i, t in enumerate(upper_rank, start=1):
        t.record(season, "upper", i)

    # 下部リーグ
    lower_top = []
    for idx, league in enumerate(lowers, start=1):
        ranking = lower_split(league)
        for i, t in enumerate(ranking, start=1):
            t.record(season, f"lower_{idx}", i)
        lower_top.extend(ranking[:2])  # 各下部上位2

    # 上位下位2
    upper_bottom2 = upper_rank[-2:]

    # 入れ替え戦
    promoted = promotion_tournament(lower_top, upper_bottom2)

    # 上位リーグ更新
    new_upper = upper_rank[:-2] + promoted

    # 下部リーグ再編（簡易）
    remaining = [t for t in upper_bottom2 + lower_top if t not in promoted]
    while len(remaining) < 8 * len(lowers):
        remaining.append(random.choice(remaining))

    new_lowers = [
        remaining[i*8:(i+1)*8]
        for i in range(len(lowers))
    ]

    return season + 1, new_upper, new_lowers
