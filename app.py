import streamlit as st
import os
from league import (
    create_initial_teams,
    load_teams,
    save_teams,
    simulate_season
)

SAVE_FILE = "league_save.json"

st.set_page_config(page_title="League Simulator", layout="wide")
st.title("🏆 League Simulator")

# -------------------------
# データロード
# -------------------------
if os.path.exists(SAVE_FILE):
    season, upper, lowers = load_teams(SAVE_FILE)
else:
    upper, lowers = create_initial_teams()
    season = 0

# -------------------------
# 操作
# -------------------------
if st.button("▶ 次のシーズンをシミュレーション"):
    season += 1
    simulate_season(season, upper, lowers)
    save_teams(SAVE_FILE, season, upper, lowers)
    st.success(f"Season {season} 完了")

if st.button("🗑 データ初期化"):
    upper, lowers = create_initial_teams()
    season = 0
    save_teams(SAVE_FILE, season, upper, lowers)
    st.experimental_rerun()

st.divider()
st.subheader(f"現在のシーズン：{season}")

# -------------------------
# 表示
# -------------------------
st.header("上位リーグ")
for i, t in enumerate(upper, 1):
    st.write(f"{i}. {t.name}（STR {t.strength}）")

for i, league in enumerate(lowers):
    st.header(f"下部リーグ {i}")
    for j, t in enumerate(league, 1):
        st.write(f"{j}. {t.name}（STR {t.strength}）")

