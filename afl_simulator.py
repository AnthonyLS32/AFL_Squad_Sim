import streamlit as st
import random
import json
import os
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="AFL Squad Simulator", layout="wide")

# --------- Load Players ---------
@st.cache_resource
def load_players():
    with open("players.json") as f:
        return json.load(f)

player_pool = load_players()

# --------- Init Session State ---------
if "squad" not in st.session_state:
    st.session_state.squad = []
if "xp" not in st.session_state:
    st.session_state.xp = {}
if "coins" not in st.session_state:
    st.session_state.coins = 500
if "draft_picks" not in st.session_state:
    st.session_state.draft_picks = []
if "draft_round" not in st.session_state:
    st.session_state.draft_round = 1
if "selected_team" not in st.session_state:
    st.session_state.selected_team = []

# --------- Pentagon Plot ---------
def plot_pentagon(player):
    stats = [
        player['goals'] * 10,
        player['disposals'],
        player['tackles'] * 10,
        player['inside50'] * 10,
        player['onepercenters'] * 10
    ]
    labels = ['Goals', 'Disposals', 'Tackles', 'Inside50', '1%ers']
    stats += stats[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels) + 1, endpoint=True)

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.plot(angles, stats, 'o-', linewidth=2)
    ax.fill(angles, stats, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_yticklabels([])
    ax.set_title(f"{player['name']} OVR:{player['ovr']}", y=1.1)
    st.pyplot(fig)

# --------- Draft Logic ---------
def autopick():
    available = [p for p in player_pool if p not in st.session_state.squad]
    pick = max(available, key=lambda p: p['ovr'])
    st.session_state.squad.append(pick)
    st.session_state.draft_picks.append(pick)
    st.session_state.draft_round += 1

def draft_phase():
    st.subheader(f"Draft Round {st.session_state.draft_round} / 10")
    available = [p for p in player_pool if p not in st.session_state.squad]
    sample = random.sample(available, min(5, len(available)))
    for p in sample:
        if st.button(f"Pick {p['name']} ({p['position']}, OVR: {p['ovr']})"):
            st.session_state.squad.append(p)
            st.session_state.draft_picks.append(p)
            st.session_state.draft_round += 1
            st.experimental_rerun()
    if st.button("AutoPick Best Available"):
        autopick()
        st.experimental_rerun()

# --------- Training Logic ---------
def training():
    st.subheader("Training Centre")
    st.write("Select up to 5 players and train them on a stat. Cost: 50 coins per player.")
    selected = st.multiselect("Pick Players to Train", [p['name'] for p in st.session_state.squad])
    stat = st.selectbox("Focus Stat", ['goals', 'disposals', 'tackles', 'inside50', 'onepercenters'])
    if st.button("Train"):
        if len(selected) > 5:
            st.error("Select max 5 players")
            return
        if st.session_state.coins < 50 * len(selected):
            st.error("Not enough coins!")
            return
        for name in selected:
            for p in st.session_state.squad:
                if p['name'] == name:
                    p[stat] += 0.1
                    st.session_state.xp[name] = st.session_state.xp.get(name, 0) + 5
        st.session_state.coins -= 50 * len(selected)
        st.success("Training done!")

# --------- Squad Display ---------
def squad_view():
    st.subheader("Your Squad")
    st.write(f"XP: {sum(st.session_state.xp.values())} | Coins: {st.session_state.coins}")
    for p in st.session_state.squad:
        st.write(f"{p['name']} | {p['position']} | OVR: {p['ovr']}")
        plot_pentagon(p)

# --------- Selected Team ---------
def select_team():
    st.subheader("Select Your Starting Team")
    squad = st.session_state.squad
    positions = ['Forward', 'Midfield', 'Defender']
    for pos in positions:
        options = [p['name'] for p in squad if p['position'] == pos]
        if options:
            chosen = st.selectbox(f"{pos}:", options, key=pos)
            for p in squad:
                if p['name'] == chosen:
                    st.session_state.selected_team = [p for p in st.session_state.selected_team if p['position'] != pos]
                    st.session_state.selected_team.append(p)
    if st.button("Lock Team"):
        st.success("Team locked for next match!")

# --------- Sidebar ---------
menu = st.sidebar.selectbox("Go to", ["Draft", "Squad", "Selected Team", "Training"])

if menu == "Draft" and st.session_state.draft_round <= 10:
    draft_phase()
elif menu == "Squad":
    squad_view()
elif menu == "Selected Team":
    select_team()
elif menu == "Training":
    training()
else:
    st.write("Draft Complete! Go to Squad.")
