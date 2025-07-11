import streamlit as st
import json
import random
import matplotlib.pyplot as plt
import numpy as np

# === Load player pool ===
@st.cache_data
def load_players():
    with open("players.json") as f:
        players = json.load(f)
        for p in players:
            # Recalculate OVR based on stat weights
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

# === Session State ===
if "squad" not in st.session_state:
    def pick_for_pos(pos, count):
        pos_players = [p for p in player_pool if p["position"] == pos]
        return random.sample(pos_players, min(count, len(pos_players)))

    forwards = pick_for_pos("Forward", 5)
    mids = pick_for_pos("Midfield", 5)
    rucks = pick_for_pos("Ruck", 3)
    defs = pick_for_pos("Defender", 5)
    starter_squad = forwards + mids + rucks + defs

    st.session_state.squad = starter_squad
    st.session_state.selected_team = []
    st.session_state.xp = 0
    st.session_state.coins = 500

# === Pentagon Plot ===
def plot_pentagon(p):
    stats = [
        p["goals"],
        p["disposals"],
        p["tackles"],
        p["inside50"],
        p["rebound50"]
    ]
    labels = ["Goals", "Disposals", "Tackles", "Inside50", "Rebound50"]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    stats += stats[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4,4), subplot_kw=dict(polar=True))
    ax.fill(angles, stats, color='skyblue', alpha=0.25)
    ax.plot(angles, stats, color='blue', linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    st.pyplot(fig)

# === Helper ===
def stats_line(p):
    return f"{p['name']} | {p['position']} | OVR: {p['ovr']}"

# === Sidebar ===
tab = st.sidebar.radio("Menu", ["Squad", "Selected Team", "Training"])

# === Squad Tab ===
if tab == "Squad":
    st.header("Your Squad")
    st.write(f"XP: {st.session_state.xp} | Coins: {st.session_state.coins}")

    for p in st.session_state.squad:
        st.write(stats_line(p))
        plot_pentagon(p)

# === Selected Team ===
elif tab == "Selected Team":
    st.header("Select Team")

    slots = [("Forward", 1), ("Midfield", 1), ("Ruck", 1), ("Defender", 1)]
    selections = []

    for pos, count in slots:
        st.subheader(f"{pos}s")
        available = [p["name"] for p in st.session_state.squad if p["position"] == pos]
        sel = st.selectbox(f"Select {pos}", available, key=f"{pos}_sel")
        selections.append(sel)

    if st.button("Save Team"):
        st.session_state.selected_team = selections
        st.success("Team saved!")

    if st.session_state.selected_team:
        st.write("**Current Team:**")
        for nm in st.session_state.selected_team:
            st.write(nm)

# === Training ===
elif tab == "Training":
    st.header("Training")
    st.write(f"XP: {st.session_state.xp}")

    player = st.selectbox("Player to Train", [p["name"] for p in st.session_state.squad], key="train_p")
    stat = st.selectbox("Stat", ["goals", "disposals", "tackles", "inside50", "rebound50"], key="train_stat")
    cost = 10

    if st.button(f"Train +1 {stat} for {cost} XP"):
        if st.session_state.xp >= cost:
            for p in st.session_state.squad:
                if p["name"] == player:
                    p[stat] += 1
                    p["ovr"] = round(
                        p["goals"] * 0.3 +
                        p["disposals"] * 0.2 +
                        p["tackles"] * 0.2 +
                        p["inside50"] * 0.1 +
                        p["rebound50"] * 0.1 +
                        p["onepercenters"] * 0.05 +
                        p["hitouts"] * 0.05
                    )
                    st.session_state.xp -= cost
                    st.success(f"{player}'s {stat} increased!")
                    break
        else:
            st.error("Not enough XP!")
