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
    st.rerun()


st.divider()
st.subheader(f"現在のシーズン：{season}")

# -------------------------
# 表示
# -------------------------
st.header("上位リーグ（チーム名編集）")

for i, t in enumerate(upper):
    new_name = st.text_input(
        label=f"上位 {i+1}",
        value=t.name,
        key=f"upper_{i}"
    )
    if new_name != t.name:
        upper[i] = t._replace(name=new_name)
        save_teams(SAVE_FILE, season, upper, lowers)


for li, league in enumerate(lowers):
    st.header(f"下部リーグ {li+1}")

    for ti, t in enumerate(league):
        new_name = st.text_input(
            label=f"下部{li+1}-{ti+1}",
            value=t.name,
            key=f"lower_{li}_{ti}"
        )
        if new_name != t.name:
            lowers[li][ti] = t._replace(name=new_name)
            save_teams(SAVE_FILE, season, upper, lowers)


