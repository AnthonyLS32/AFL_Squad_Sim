import json
import random
import streamlit as st

# Load player pool
with open('players_full.json') as f:
    player_pool = json.load(f)

# Pick squad if not set
if 'squad' not in st.session_state:
    if len(player_pool) < 22:
        st.error("❌ Not enough players to pick a squad of 22!")
        st.stop()
    st.session_state['squad'] = random.sample(player_pool, 22)

squad = st.session_state['squad']

st.title("AFL Squad Simulator ✅")
st.header("Your Squad:")

for player in squad:
    st.write(f"{player['name']} - {player['position']} - {player['ovr']} OVR")

if st.button("Reshuffle Squad"):
    st.session_state['squad'] = random.sample(player_pool, 22)
    st.experimental_rerun()
