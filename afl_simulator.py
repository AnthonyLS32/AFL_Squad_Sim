import streamlit as st
import json
import random
import os
from datetime import datetime

# ---- Load players ----
with open('players_full.json') as f:
    player_pool = json.load(f)

# ---- Session State ----
if 'squad' not in st.session_state:
    if os.path.exists('squad.json'):
        with open('squad.json') as f:
            st.session_state['squad'] = json.load(f)
    else:
        st.session_state['squad'] = random.sample(player_pool, 22)
        with open('squad.json', 'w') as f:
            json.dump(st.session_state['squad'], f)

if 'career' not in st.session_state:
    if os.path.exists('career.json'):
        with open('career.json') as f:
            st.session_state['career'] = json.load(f)
    else:
        st.session_state['career'] = {'round': 1, 'coins': 100, 'xp': 0}
        with open('career.json', 'w') as f:
            json.dump(st.session_state['career'], f)

squad = st.session_state['squad']
career = st.session_state['career']

st.title("🏉 AFL Ultimate Squad FUT Prototype")

# ---- Layout helper ----
def display_player_card(player):
    st.image(player.get('photo_url', 'https://via.placeholder.com/100'), width=80)
    st.write(f"**{player['name']}** ({player['year']})")
    age = player.get('year', 2024) - (1987 if 'Lance' in player['name'] else 1995)  # simple mock
    st.write(f"Age: {age}")
    st.write(f"{player['position']} | OVR: {player['ovr']}")
    st.write(f"G: {player['goals']} | D: {player['disposals']} | T: {player['tackles']}")

# ---- Squad screen ----
st.header("📌 My Squad (Oval Layout)")

backs = squad[:6]
mids = squad[6:12]
forwards = squad[12:18]
bench = squad[18:]

st.subheader("Backs")
cols = st.columns(6)
for idx, p in enumerate(backs):
    with cols[idx]:
        display_player_card(p)

st.subheader("Midfielders & Ruck")
cols = st.columns(6)
for idx, p in enumerate(mids):
    with cols[idx]:
        display_player_card(p)

st.subheader("Forwards")
cols = st.columns(6)
for idx, p in enumerate(forwards):
    with cols[idx]:
        display_player_card(p)

st.subheader("Bench")
cols = st.columns(len(bench))
for idx, p in enumerate(bench):
    with cols[idx]:
        display_player_card(p)

# ---- Swap ----
st.subheader("🔄 Swap Players")
pos_options = [f"{i+1} {p['name']} ({p['position']})" for i, p in enumerate(squad)]
swap_out = st.selectbox("Pick position to replace", pos_options)
swap_in = st.selectbox("Pick bench player to swap in", pos_options[18:])

if st.button("Swap"):
    idx
