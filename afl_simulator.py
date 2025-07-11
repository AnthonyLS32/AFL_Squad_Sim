import streamlit as st
import json
import random
import matplotlib.pyplot as plt
import numpy as np

@st.cache_data
def load_players():
    with open("players.json") as f:
        players = json.load(f)
        for p in players:
            p["ovr"] = round(
                p["goals"] * 0.3 +
                p["disposals"] * 0.2 +
                p["tackles"] * 0.2 +
                p["inside50"] * 0.1 +
                p["rebound50"] * 0.1 +
                p["onepercenters"] * 0.05 +
                p["hitouts"] * 0.05
            )
        return players

player_pool = load_players()

if "squad" not in st.session_state:
    st.session_state.squad = random.sample(player_pool, min(4, len(player_pool)))
    st.session_state.xp = 0

def plot_pentagon(p):
    stats = [
        p["goals"] * 10,
        p["disposals"] / 3,
        p["tackles"] * 5,
        p["inside50"] * 10,
        p["rebound50"] * 10
    ]
    labels = ["Goals", "Disposals", "Tackles", "Inside50", "Rebound50"]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    stats += stats[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.fill(angles, stats, color='skyblue', alpha=0.3)
    ax.plot(angles, stats, color='blue')
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    st.pyplot(fig)

st.title("Squad")

names = [p["name"] for p in st.session_state.squad]
selected = st.selectbox("Select player to view", names)

player = next(p for p in st.session_state.squad if p["name"] == selected)
st.write(f"{player['name']} | {player['position']} | OVR: {player['ovr']}")
plot_pentagon(player)
