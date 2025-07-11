import streamlit as st
import json
import random
import matplotlib.pyplot as plt

# === Pentagon Chart ===

def plot_pentagon(p):
    categories = ["goals", "disposals", "tackles", "inside50", "rebound50"]
    if p.get("hitouts", 0) > 0:
        categories.append("hitouts")
    values = [p.get(cat, 0) for cat in categories]

    angles = [n / float(len(categories)) * 2 * 3.14159 for n in range(len(categories))]
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(2, 2), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color="blue", alpha=0.25)
    ax.plot(angles, values, color="blue")
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=8)
    st.pyplot(fig)

# === Load Players ===

@st.cache_data
def load_players():
    with open("players.json") as f:
        players = json.load(f)
    for p in players:
        p['ovr'] = compute_ovr(p)
    return players

def compute_ovr(p):
    score = (
        p.get("goals", 0) * 10 +
        p.get("disposals", 0) * 2 +
        p.get("tackles", 0) * 5 +
        p.get("inside50", 0) * 4 +
        p.get("rebound50", 0) * 4 +
        p.get("hitouts", 0) * 0.5
    )
    return min(round(score), 99)

player_pool = load_players()

# === Initialise State ===

if "squad" not in st.session_state:
    def pick(pos, n):
        pos_players = [p for p in player_pool if p['position'] == pos]
        return random.sample(pos_players, min(n, len(pos_players)))
    squad = []
    squad += pick("Forward", 5)
    squad += pick("Midfield", 5)
    squad += pick("Defender", 5)
    squad += pick("Ruck", 2)
    st.session_state.squad = squad
    st.session_state.selected_team = []
    st.session_state.xp = 0
    st.session_state.coins = 500

# === Sidebar ===

tab = st.sidebar.radio("Menu", ["Squad", "Selected Team", "Training"])

# === Squad ===

if tab == "Squad":
    st.title("Your Squad")
    st.write(f"XP: {st.session_state.xp} | Coins: {st.session_state.coins}")
    for p in st.session_state.squad:
        st.write(f"**{p['name']}** | {p['position']} | OVR: {p['ovr']}")
        plot_pentagon(p)

# === Selected Team ===

elif tab == "Selected Team":
    st.title("Select Your Team")

    slots = [("Forward", 1), ("Midfield", 1), ("Defender", 1), ("Ruck", 1)]
    selections = []

    for pos, count in slots:
        st.subheader(f"{pos} ({count})")
        options = [p['name'] for p in st.session_state.squad if p['position'] == pos]
        sel = st.selectbox(f"Select {pos}", options, key=f"sel_{pos}")
        selections.append(sel)

    if st.button("Save Team"):
        st.session_state.selected_team = selections
        st.success("Team saved!")

    if st.session_state.selected_team:
        st.write("**Current Selected Team:**")
        for name in st.session_state.selected_team:
            st.write(name)

# === Training ===

elif tab == "Training":
    st.title("Training")
    st.write(f"XP Available: {st.session_state.xp}")

    choices = [p['name'] for p in st.session_state.squad]
    player = st.selectbox("Pick player", choices)
    stat = st.selectbox("Stat to improve", ["goals", "disposals", "tackles", "inside50", "rebound50", "hitouts"])
    cost = 20

    if st.button(f"Train +0.5 {stat} for {cost} XP"):
        if st.session_state.xp >= cost:
            for p in st.session_state.squad:
                if p['name'] == player:
                    p[stat] += 0.5
                    p['ovr'] = compute_ovr(p)
                    st.session_state.xp -= cost
                    st.success(f"{player} trained {stat}!")
        else:
            st.error("Not enough XP!")
