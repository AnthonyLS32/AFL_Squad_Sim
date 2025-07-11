import streamlit as st
import random
import json
import matplotlib.pyplot as plt

# ---- Load or Create Players ---- #
@st.cache_data
def load_players():
    # Example: Load from JSON file, or make a quick pool inline
    return [
        {"name": f"Player{i}", "position": random.choice(["Forward", "Midfield", "Defender", "Ruck"]),
         "goals": random.uniform(0, 2),
         "disposals": random.uniform(10, 30),
         "tackles": random.uniform(1, 6),
         "inside50": random.uniform(1, 6),
         "rebound50": random.uniform(0, 7),
         "onepercenters": random.uniform(0, 8),
         "hitouts": random.uniform(0, 35) if random.choice(["Ruck", "Other"]) == "Ruck" else 0,
         "ovr": random.randint(55, 85),
         "xp": 0
         }
        for i in range(1, 101)
    ]

player_pool = load_players()

# ---- Initialize Session State ---- #
if "squad" not in st.session_state:
    st.session_state.squad = []

if "draft_round" not in st.session_state:
    st.session_state.draft_round = 1

if "xp" not in st.session_state:
    st.session_state.xp = 0

if "coins" not in st.session_state:
    st.session_state.coins = 500

if "selected_team" not in st.session_state:
    st.session_state.selected_team = []

# ---- Functions ---- #
def calculate_overall(player):
    stats = ["goals", "disposals", "tackles", "inside50", "rebound50", "onepercenters", "hitouts"]
    values = [player[s] for s in stats]
    return int(sum(values) / len(values) * 3)

def plot_pentagon(player):
    categories = ["Goals", "Disposals", "Tackles", "Inside50", "Rebound50"]
    values = [player["goals"], player["disposals"] / 3, player["tackles"], player["inside50"], player["rebound50"]]
    values += values[:1]
    angles = [n / float(len(categories)) * 2 * 3.14159 for n in range(len(categories))]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.fill(angles, values, alpha=0.25)
    ax.plot(angles, values, linewidth=2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    st.pyplot(fig)

def draft_phase():
    st.title(f"Draft Round {st.session_state.draft_round} / 10")
    available = random.sample(player_pool, 5)
    for i, p in enumerate(available):
        key = f"pick_{st.session_state.draft_round}_{i}_{p['name']}"
        if st.button(f"Pick {p['name']} ({p['position']}, OVR: {p['ovr']})", key=key):
            st.session_state.squad.append(p)
            st.session_state.draft_round += 1
            st.experimental_rerun()

    if st.button("Auto Pick Best", key="auto_pick"):
        best = max(available, key=lambda x: x['ovr'])
        st.session_state.squad.append(best)
        st.session_state.draft_round += 1
        st.experimental_rerun()

    if st.session_state.draft_round > 10:
        st.success("Draft complete!")
        st.stop()

def show_squad():
    st.header("Your Squad")
    st.write(f"XP: {st.session_state.xp} | Coins: {st.session_state.coins}")
    for p in st.session_state.squad:
        st.write(f"{p['name']} | {p['position']} | OVR: {p['ovr']}")
        plot_pentagon(p)

def select_team():
    st.header("Select Your Team")
    available = [p for p in st.session_state.squad if p not in st.session_state.selected_team]

    for pos in ["Forward", "Midfield", "Defender", "Ruck"]:
        current = [p for p in st.session_state.selected_team if p["position"] == pos]
        if current:
            st.write(f"{pos}: {current[0]['name']} (OVR {current[0]['ovr']})")
            if st.button(f"Deselect {pos} ({current[0]['name']})", key=f"des_{pos}"):
                st.session_state.selected_team.remove(current[0])
                st.experimental_rerun()
        else:
            options = [p for p in available if p["position"] == pos]
            for i, p in enumerate(options):
                if st.button(f"Select {p['name']} ({p['ovr']}) for {pos}", key=f"sel_{pos}_{i}"):
                    st.session_state.selected_team.append(p)
                    st.experimental_rerun()

    if st.button("Auto Pick Team", key="auto_pick_team"):
        st.session_state.selected_team = []
        for pos in ["Forward", "Midfield", "Defender", "Ruck"]:
            best = max([p for p in available if p["position"] == pos], key=lambda x: x["ovr"], default=None)
            if best:
                st.session_state.selected_team.append(best)
        st.experimental_rerun()

    if len(st.session_state.selected_team) == 4:
        st.success("Team ready!")

def training_phase():
    st.header("Training")
    available = st.session_state.squad
    selected = st.multiselect("Pick up to 5 players to train", [p["name"] for p in available])

    if st.button("Train Selected"):
        for name in selected:
            p = next(p for p in available if p["name"] == name)
            p["xp"] += 10
        st.success("Training complete!")

# ---- Pages ---- #
menu = st.sidebar.radio("Go to", ["Draft", "Squad", "Selected Team", "Training"])

if menu == "Draft":
    draft_phase()
elif menu == "Squad":
    show_squad()
elif menu == "Selected Team":
    select_team()
elif menu == "Training":
    training_phase()
