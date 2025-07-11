import streamlit as st
import json
import random
import matplotlib.pyplot as plt
import numpy as np

# -------------------------------
# Load Players
# -------------------------------
@st.cache_data
def load_players():
    with open("players.json", "r") as f:
        return json.load(f)

player_pool = load_players()

# -------------------------------
# Pentagon Plot Function
# -------------------------------
def plot_pentagon(player):
    stats = [
        player['goals'] * 10,
        player['disposals'] * 3,
        player['tackles'] * 10,
        player['inside50'] * 10,
        player['onepercenters'] * 10
    ]
    max_value = max(stats + [1])
    stats = [s / max_value for s in stats]

    labels = ['Goals', 'Disposals', 'Tackles', 'Inside50', '1%ers']
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    stats += stats[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.fill(angles, stats, color='skyblue', alpha=0.4)
    ax.plot(angles, stats, color='blue', linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    st.pyplot(fig)

# -------------------------------
# Autopick function
# -------------------------------
def auto_pick_squad(pool):
    squad = []
    for pos, count in [('Forward', 3), ('Midfield', 4), ('Defender', 3), ('Ruck', 1)]:
        players = [p for p in pool if p['position'] == pos]
        best = sorted(players, key=lambda x: x.get('ovr', 50), reverse=True)[:count]
        squad.extend(best)
    return squad

# -------------------------------
# Session State Init
# -------------------------------
if 'squad' not in st.session_state:
    st.session_state.squad = auto_pick_squad(player_pool)
if 'selected_team' not in st.session_state:
    st.session_state.selected_team = []

# -------------------------------
# UI Layout
# -------------------------------
st.title("AFL Squad Simulator")
st.sidebar.title("Menu")
page = st.sidebar.radio("Go to", ["Squad", "Selected Team"])

# -------------------------------
# Squad Page
# -------------------------------
if page == "Squad":
    st.header("Your Squad")
    for p in st.session_state.squad:
        st.write(f"**{p['name']}** | {p['position']} | OVR: {p.get('ovr', 50)}")
        plot_pentagon(p)

# -------------------------------
# Team Selection
# -------------------------------
elif page == "Selected Team":
    st.header("Pick Your Team")

    for pos in ['Forward', 'Midfield', 'Defender', 'Ruck']:
        selected = [p for p in st.session_state.selected_team if p['position'] == pos]
        available = [p for p in st.session_state.squad if p['position'] == pos and p not in st.session_state.selected_team]

        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"{pos} (Selected)")
            for p in selected:
                st.write(f"{p['name']} | OVR: {p.get('ovr', 50)}")
                if st.button(f"Deselect {p['name']}", key=f"de_{p['name']}"):
                    st.session_state.selected_team.remove(p)

        with col2:
            st.subheader(f"{pos} (Available)")
            for p in available:
                st.write(f"{p['name']} | OVR: {p.get('ovr', 50)}")
                if st.button(f"Select {p['name']}", key=f"sel_{p['name']}"):
                    st.session_state.selected_team.append(p)

    if st.button("Autopick Best Team"):
        st.session_state.selected_team = auto_pick_squad(st.session_state.squad)

    st.write("### Final Team")
    for p in st.session_state.selected_team:
        st.write(f"{p['name']} | {p['position']} | OVR: {p.get('ovr', 50)}")

