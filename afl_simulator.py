import streamlit as st
import random
import json
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="AFL Squad Simulator", layout="wide")

# ------------------------
# --- Load Players ---
# ------------------------

@st.cache_data
def load_players():
    with open("players.json", "r") as f:
        players = json.load(f)
    return players

player_pool = load_players()

# ------------------------
# --- Init State ---
# ------------------------

if "squad" not in st.session_state:
    st.session_state.squad = []
if "selected_team" not in st.session_state:
    st.session_state.selected_team = []
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "coins" not in st.session_state:
    st.session_state.coins = 500
if "draft_round" not in st.session_state:
    st.session_state.draft_round = 1
if "draft_picks" not in st.session_state:
    st.session_state.draft_picks = []

# ------------------------
# --- Sidebar ---
# ------------------------

st.sidebar.title("Menu")
page = st.sidebar.radio("Go to", ["Draft", "Squad", "Selected Team", "Training"])

# ------------------------
# --- Pentagon Plot ---
# ------------------------

def plot_pentagon(player):
    stats = [player["goals"], player["disposals"], player["tackles"], player["inside50"], player["rebound50"]]
    labels = ["Goals", "Disposals", "Tackles", "Inside50", "Rebound50"]

    # Normalise stats to 0-10
    norm_stats = [min(s / 5, 10) for s in stats]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    norm_stats += norm_stats[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.fill(angles, norm_stats, color="blue", alpha=0.25)
    ax.plot(angles, norm_stats, color="blue", linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    st.pyplot(fig)

# ------------------------
# --- Draft ---
# ------------------------

def draft_phase():
    st.subheader(f"Draft Round {st.session_state.draft_round} / 10")

    available = [p for p in player_pool if p["name"] not in [s["name"] for s in st.session_state.squad]]

    if not available or st.session_state.draft_round > 10:
        st.success("Draft complete! Go to Squad.")
        return

    sample = random.sample(available, min(5, len(available)))

    for i, p in enumerate(sample):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{p['name']}** | {p['position']} | OVR: {p['ovr']}")
        with col2:
            if st.button("Draft", key=f"draft_{st.session_state.draft_round}_{i}"):
                st.session_state.squad.append(p)
                st.session_state.draft_picks.append(p)
                st.session_state.draft_round += 1
                st.experimental_rerun()

    if st.button("AutoPick Best Available", key=f"auto_{st.session_state.draft_round}"):
        autopick()
        st.experimental_rerun()

def autopick():
    available = [p for p in player_pool if p["name"] not in [s["name"] for s in st.session_state.squad]]
    if available:
