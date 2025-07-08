import json
import random
import streamlit as st

# Load player pool
with open('players_full.json') as f:
    player_pool = json.load(f)

if len(player_pool) < 22:
    st.error("❌ Your player pool does not have at least 22 players.")
    st.stop()

if 'squad' not in st.session_state:
    st.session_state['squad'] = random.sample(player_pool, 22)

squad = st.session_state['squad']

st.title("AFL Squad Simulator ✅")
st.header("Your Squad:")

for player in squad:
    st.write(f"{player['name']} | {player['position']} | OVR: {player['ovr']}")

if st.button("Reshuffle Squad"):
    st.session_state['squad'] = random.sample(player_pool, 22)
    st.experimental_rerun()
