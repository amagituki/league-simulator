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
    season, upper, lowers = league.simulate_season(season, upper, lowers)
    league.save_teams(SAVE_FILE, season, upper, lowers)

st.header(f"Season {season}")
for i, t in enumerate(upper, 1):
    st.write(f"{i}. {t.name} STR:{t.strength}")

if st.button("🧨 完全強制リセット"):
    try:
        os.remove(SAVE_FILE)
        st.success("league_save.json を削除しました")
    except FileNotFoundError:
        st.warning("保存データは存在しませんでした")
    st.rerun()
