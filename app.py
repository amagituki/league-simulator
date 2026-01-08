import streamlit as st
import league
import os

SAVE_FILE = "league_save.json"

st.title("League Simulator")

if os.path.exists(SAVE_FILE):
    season, upper, lowers = league.load_teams(SAVE_FILE)
else:
    upper, lowers = league.create_initial_teams()
    season = 0
    league.save_teams(SAVE_FILE, season, upper, lowers)

if st.button("次のシーズン"):
    season += 1
    league.simulate_season(season, upper, lowers)
    league.save_teams(SAVE_FILE, season, upper, lowers)
    st.success(f"Season {season} 完了")

st.header(f"Season {season-1} 結果")

# ======================
# 上位リーグ
# ======================
st.subheader("🏆 上位リーグ順位")

for i, t in enumerate(upper, start=1):
    st.write(f"{i}. {t.name} ｜ STR {t.strength}")

st.subheader("⬇ 下部リーグ")

for idx, league in enumerate(lowers, start=1):
    st.write(f"--- 下部リーグ {idx} ---")
    for i, t in enumerate(league, start=1):
        st.write(f"{i}. {t.name} ｜ STR {t.strength}")

st.header("📜 チーム履歴")

all_teams = upper[:]
for lg in lowers:
    all_teams.extend(lg)

team = st.selectbox(
    "チームを選択",
    all_teams,
    format_func=lambda t: t.name
)

st.write(f"### {team.name}")
st.write(f"現在STR: {team.strength}")
st.write(f"昇格: {team.promotions} / 降格: {team.relegations}")

for h in team.history:
    st.write(
        f"Season {h['season']}｜{h['league']}｜{h['rank']}位"
    )

st.header("📈 強さ推移")

seasons = [h["season"] for h in team.history]
strengths = [h.get("strength", team.strength) for h in team.history]

if seasons:
    st.line_chart(
        {"STR": strengths},
        x=seasons
    )
else:
    st.write("履歴がありません")
