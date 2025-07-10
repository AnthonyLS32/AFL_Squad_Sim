import streamlit as st
import json
import random
import numpy as np
import matplotlib.pyplot as plt

# --- Load player pool safely -----------------------------------------------------------
@st.cache_resource
def load_players():
    with open('players.json') as f:
        players = json.load(f)
    # Validate: ensure required keys exist
    for p in players:
        p.setdefault("name", "Unknown")
        p.setdefault("position", "Unknown")
        p.setdefault("ovr", 50)
        p.setdefault("goals", 0)
        p.setdefault("disposals", 0)
        p.setdefault("tackles", 0)
        p.setdefault("inside50", 0)
        p.setdefault("rebound50", 0)
    return players

player_pool = load_players()

# --- Radar Chart (Pentagon) -----------------------------------------------------------
def show_player_radar(player):
    stats = [
        player.get("goals", 0),
        player.get("disposals", 0),
        player.get("tackles", 0),
        player.get("inside50", 0),
        player.get("rebound50", 0),
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

# --- Session State Setup ---------------------------------------------------------------
if 'squad' not in st.session_state:
    st.session_state.squad = []
    st.session_state.selected_team = []

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

# --- Sidebar --------------------------------------------------------------------------
tab = st.sidebar.radio("Menu", ["Squad", "Selected Team"])

# --- Squad Tab ------------------------------------------------------------------------
if tab == "Squad":
    st.header("Your Squad")
    for p in st.session_state.squad:
        name = p.get('name', 'Unknown')
        pos = p.get('position', 'Unknown')
        ovr = p.get('ovr', 50)
        st.write(f"**{name}** | {pos} | OVR: {ovr}")
        show_player_radar(p)

# --- Selected Team Tab ---------------------------------------------------------------
elif tab == "Selected Team":
    st.header("Pick Your Starting Team")
    slots = [("Forward", 1), ("Midfield", 1), ("Ruck", 1), ("Defender", 1)]
    selections = []

    for pos, count in slots:
        st.subheader(f"{pos}")
        available = [p for p in st.session_state.squad if p["position"] == pos]
        names = [p["name"] for p in available]
        if names:
            sel = st.selectbox(f"Select {pos}", names, key=f"sel_{pos}")
            selections.append(sel)
        else:
            st.warning(f"No available players for {pos}!")

    if st.button("Save Team"):
        st.session_state.selected_team = selections.copy()
        st.success("✅ Team saved!")

    if st.session_state.selected_team:
        st.write("**Your Saved Team:**")
        for name in st.session_state.selected_team:
            st.write(f"• {name}")
