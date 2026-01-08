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
