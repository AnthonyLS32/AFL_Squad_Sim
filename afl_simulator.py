import streamlit as st
import json
import random
import numpy as np
import matplotlib.pyplot as plt

# --- Load player pool -----------------------------------------------------------
@st.cache_resource
def load_players():
    with open('players.json') as f:
        players = json.load(f)
    return players

player_pool = load_players()

# --- Radar Chart ---------------------------------------------------------------
def show_player_radar(player):
    stats = [
        player["goals"],
        player["disposals"],
        player["tackles"],
        player["inside50"],
        player["rebound50"],
    ]
    labels = ["Goals", "Disposals", "Tackles", "Inside 50", "Rebound 50"]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    stats += stats[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.fill(angles, stats, color="red", alpha=0.25)
    ax.plot(angles, stats, color="red", linewidth=2)

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    st.pyplot(fig)

# --- Session State Setup -------------------------------------------------------
if 'squad' not in st.session_state:
    st.session_state.squad = []
    st.session_state.selected_team = []

    # Always include Buddy Franklin
    buddy = next((p for p in player_pool if p["name"] == "Lance Franklin"), None)
    if buddy:
        st.session_state.squad.append(buddy)

    def pick(pos, n):
        pool = [p for p in player_pool if p["position"] == pos and p not in st.session_state.squad]
        return random.sample(pool, min(n, len(pool)))

    st.session_state.squad += pick("Forward", 4)
    st.session_state.squad += pick("Midfield", 4)
    st.session_state.squad += pick("Ruck", 2)
    st.session_state.squad += pick("Defender", 4)

# --- Sidebar Navigation --------------------------------------------------------
tab = st.sidebar.radio("Menu", ["Squad", "Selected Team"])

# --- Squad Tab -----------------------------------------------------------------
if tab == "Squad":
    st.header("Your Squad")
    for p in st.session_state.squad:
        st.write(f"**{p['name']}** | {p['position']} | OVR: {p['ovr']}")
        show_player_radar(p)

# --- Selected Team Tab ---------------------------------------------------------
elif tab == "Selected Team":
    st.header("Pick Your Starting Team")
    slots = [("Forward", 1), ("Midfield", 1), ("Ruck", 1), ("Defender", 1)]
    selections = []

    for pos, count in slots:
        st.subheader(f"{pos}")
        available = [p for p in st.session_state.squad if p["position"] == pos]
        names = [p["name"] for p in available]
        sel = st.selectbox(f"Select {pos}", names, key=f"sel_{pos}")
        selections.append(sel)

    if st.button("Save Team"):
        st.session_state.selected_team = selections.copy()
        st.success("✅ Team saved!")

    if st.session_state.selected_team:
        st.write("**Your Saved Team:**")
        for name in st.session_state.selected_team:
            st.write(f"• {name}")
