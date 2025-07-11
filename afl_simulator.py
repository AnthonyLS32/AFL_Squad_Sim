import streamlit as st
import json
import random
import matplotlib.pyplot as plt
import numpy as np

# === Compute OVR ===
def compute_ovr(p):
    max_vals = {
        "goals": 4.0,
        "disposals": 35.0,
        "tackles": 8.0,
        "inside50": 6.0,
        "rebound50": 6.0,
        "hitouts": 40.0
    }
    weights = {
        "goals": 0.3,
        "disposals": 0.4,
        "tackles": 0.1,
        "inside50": 0.08,
        "rebound50": 0.08,
        "hitouts": 0.2
    }
    total_weight = sum(weights.values())
    ovr = 0
    for stat, weight in weights.items():
        val = p.get(stat, 0)
        scaled = val / max_vals[stat]
        ovr += scaled * weight
    ovr = (ovr / total_weight) * 100
    ovr = max(40, min(round(ovr * 0.9), 90))
    return ovr

# === Load Players ===
@st.cache_data
def load_players():
    with open("players.json") as f:
        players = json.load(f)
    for p in players:
        p["ovr"] = compute_ovr(p)
    return players

player_pool = load_players()

# === Pentagon ===
def plot_pentagon(player):
    labels = ["Goals", "Disposals", "Tackles", "Inside50", "Rebound50", "Hitouts"]
    stats = [
        player.get("goals", 0) * 25,
        player.get("disposals", 0) * 3,
        player.get("tackles", 0) * 12.5,
        player.get("inside50", 0) * 16.5,
        player.get("rebound50", 0) * 16.5,
        player.get("hitouts", 0) * 2.5
    ]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    stats += stats[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.fill(angles, stats, color="skyblue", alpha=0.25)
    ax.plot(angles, stats, color="blue", linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    st.pyplot(fig)

# === Sidebar ===
st.sidebar.title("Menu")
page = st.sidebar.selectbox("Go to", ["Squad", "Selected Team", "Training"])

# === Session ===
if "squad" not in st.session_state:
    forwards = [p for p in player_pool if p["position"] == "Forward"]
    mids = [p for p in player_pool if p["position"] == "Midfield"]
    defs = [p for p in player_pool if p["position"] == "Defender"]
    rucks = [p for p in player_pool if p["position"] == "Ruck"]

    starting_squad = (
        random.sample(forwards, 3)
        + random.sample(mids, 3)
        + random.sample(defs, 3)
        + random.sample(rucks, 1)
    )
    st.session_state.squad = starting_squad
    st.session_state.selected_team = []

# === Autopick ===
def autopick():
    positions = {"Forward": 1, "Midfield": 1, "Defender": 1, "Ruck": 1}
    selected = []
    for pos, count in positions.items():
        candidates = [p for p in st.session_state.squad if p["position"] == pos]
        best = sorted(candidates, key=lambda p: p["ovr"], reverse=True)[:count]
        selected.extend(best)
    st.session_state.selected_team = selected

# === Pages ===
if page == "Squad":
    st.title("Your Squad")
    for p in st.session_state.squad:
        st.write(f"{p['name']} | {p['position']} | OVR: {p['ovr']}")
        plot_pentagon(p)

elif page == "Selected Team":
    st.title("Selected Team")
    if st.button("AutoPick Best Team"):
        autopick()
    selected = st.session_state.selected_team
    for p in selected:
        st.write(f"{p['name']} | {p['position']} | OVR: {p['ovr']}")
        plot_pentagon(p)

    available = [p for p in st.session_state.squad if p not in selected]
    st.write("Available:")
    for p in available:
        if st.button(f"Add {p['name']}"):
            if len(selected) < 4:
                st.session_state.selected_team.append(p)
                st.experimental_rerun()

elif page == "Training":
    st.title("Training")
    st.write("Coming soon...")
