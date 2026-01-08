# league.py
import random
import json

MIN_STR, MAX_STR = 30, 100

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
        return self.__dict__

    @staticmethod
    def from_dict(d):
        t = Team(d["name"], d["strength"])
        t.history = d["history"]
        t.promotions = d["promotions"]
        t.relegations = d["relegations"]
        t.titles = d["titles"]
        return t


def play_match(a, b):
    if random.random() < a.strength / (a.strength + b.strength):
        a.adjust(1)
        b.adjust(-1)
        return a, b
    else:
        b.adjust(1)
        a.adjust(-1)
        return b, a


def round_robin(teams, double=False):
    wins = {t: 0 for t in teams}
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            for _ in range(2 if double else 1):
                w, _ = play_match(teams[i], teams[j])
                wins[w] += 1
    return sorted(teams, key=lambda t: wins[t], reverse=True)


def upper_split(teams):
    random.shuffle(teams)
    g1, g2 = teams[:5], teams[5:]
    qualified = round_robin(g1)[:3] + round_robin(g2)[:3]
    return round_robin(qualified, double=True)


def lower_split(teams):
    random.shuffle(teams)
    g1, g2 = teams[:4], teams[4:]
    qualified = round_robin(g1, True)[:2] + round_robin(g2, True)[:2]
    return round_robin(qualified, True)


def promotion_tournament(lower, upper_bottom):
    ranking = round_robin(lower + upper_bottom, True)
    promoted = ranking[:2]
    for t in promoted:
        t.promotions += 1
    for t in upper_bottom:
        if t not in promoted:
            t.relegations += 1
    return promoted


def create_initial_teams():
    upper = [Team(f"U{i+1}", random.randint(65, 80)) for i in range(10)]
    lowers = [[Team(f"L{j+1}-{i+1}", random.randint(40, 60)) for i in range(8)] for j in range(2)]
    return upper, lowers


def save_teams(path, season, upper, lowers):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "season": season,
            "upper": [t.to_dict() for t in upper],
            "lowers": [[t.to_dict() for t in lg] for lg in lowers]
        }, f, ensure_ascii=False, indent=2)


def load_teams(path):
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    return (
        d["season"],
        [Team.from_dict(x) for x in d["upper"]],
        [[Team.from_dict(x) for x in lg] for lg in d["lowers"]]
    )

def simulate_season(season, upper, lowers):
    upper_rank = upper_split(upper)
    for i, t in enumerate(upper_rank, 1):
        t.record(season, "upper", i)

    lower_rankings = []
    lower_candidates = []

    for idx, lg in enumerate(lowers, 1):
        r = lower_split(lg)
        for i, t in enumerate(r, 1):
            t.record(season, f"lower_{idx}", i)
        lower_rankings.append(r)
        lower_candidates.extend(r)

    promoted = promotion_tournament(lower_candidates, upper_rank[-2:])
    new_upper = upper_rank[:-2] + promoted

    # 上位に行かなかったチームを下部へ
    remaining_lower = [
        t for t in lower_candidates + upper_rank[-2:]
        if t not in promoted
    ]

    random.shuffle(remaining_lower)

    new_lowers = [
        remaining_lower[i*8:(i+1)*8]
        for i in range(len(lowers))
    ]

    return season + 1, new_upper, new_lowers
