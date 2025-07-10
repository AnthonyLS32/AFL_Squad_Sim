import streamlit as st
import random
import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------
# Mock player pool (expand to 300 for real use)
# --------------------------------------------
player_pool = [
    {'name': 'Lance Franklin', 'position': 'Forward',
     'attributes': {'Speed': 85, 'Strength': 90, 'Skill': 92, 'Endurance': 80, 'Agility': 78}},
    {'name': 'Tom Lynch', 'position': 'Forward',
     'attributes': {'Speed': 80, 'Strength': 85, 'Skill': 88, 'Endurance': 75, 'Agility': 74}},
    {'name': 'Patrick Cripps', 'position': 'Midfield',
     'attributes': {'Speed': 80, 'Strength': 85, 'Skill': 90, 'Endurance': 88, 'Agility': 82}},
    {'name': 'Clayton Oliver', 'position': 'Midfield',
     'attributes': {'Speed': 78, 'Strength': 80, 'Skill': 89, 'Endurance': 85, 'Agility': 81}},
    {'name': 'Max Gawn', 'position': 'Ruck',
     'attributes': {'Speed': 60, 'Strength': 95, 'Skill': 75, 'Endurance': 85, 'Agility': 70}},
    {'name': 'Brodie Grundy', 'position': 'Ruck',
     'attributes': {'Speed': 62, 'Strength': 90, 'Skill': 70, 'Endurance': 82, 'Agility': 68}},
    {'name': 'Tom Stewart', 'position': 'Defender',
     'attributes': {'Speed': 78, 'Strength': 82, 'Skill': 85, 'Endurance': 80, 'Agility': 79}},
    {'name': 'Darcy Moore', 'position': 'Defender',
     'attributes': {'Speed': 75, 'Strength': 80, 'Skill': 82, 'Endurance': 78, 'Agility': 77}},
    {'name': 'Utility Player', 'position': 'Utility',
     'attributes': {'Speed': 75, 'Strength': 75, 'Skill': 75, 'Endurance': 75, 'Agility': 75}},
]

positions = ['Forward', 'Midfield', 'Ruck', 'Defender', 'Utility']

# --------------------------------------------
# Init session state
# --------------------------------------------
if 'xp' not in st.session_state:
    st.session_state.xp = 0
if 'coins' not in st.session_state:
    st.session_state.coins = 500
if 'selected_team' not in st.session_state:
    st.session_state.selected_team = {pos: None for pos in positions}
if 'match_log' not in st.session_state:
    st.session_state.match_log = []

# --------------------------------------------
# Sidebar
# --------------------------------------------
tab = st.sidebar.radio(
    "Menu", ["Select Team", "Play Match", "Training", "Squad"])

# --------------------------------------------
# Pentagon radar chart
# --------------------------------------------
def plot_pentagon(player_attrs, player_name):
    labels = list(player_attrs.keys())
    stats = list(player_attrs.values())
    stats += stats[:1]  # close loop

    angles = np.linspace(0, 2 * np.pi, len(labels) + 1)

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.plot(angles, stats, 'o-', linewidth=2)
    ax.fill(angles, stats, alpha=0.25)
    ax.set_thetagrids(angles[:-1] * 180/np.pi, labels)
    ax.set_ylim(0, 100)
    ax.set_title(player_name)
    ax.set_yticklabels([])
    st.pyplot(fig)

# --------------------------------------------
# SELECT TEAM TAB
# --------------------------------------------
if tab == "Select Team":
    st.title("Select Your Team")
    for pos in positions:
        st.subheader(f"{pos}")
        already = [p for p in st.session_state.selected_team.values() if p]
        pool = [p for p in player_pool if p['position'] == pos and p['name'] not in already]

        if st.session_state.selected_team[pos]:
            st.success(f"Selected: {st.session_state.selected_team[pos]}")
            if st.button(f"Deselect {pos}"):
                st.session_state.selected_team[pos] = None
        else:
            options = ["-- Select --"] + [p['name'] for p in pool]
            choice = st.selectbox(f"Pick {pos}", options, key=f"pick_{pos}")
            if choice != "-- Select --":
                st.session_state.selected_team[pos] = choice

        selected = st.session_state.selected_team[pos]
        if selected:
            p = next(p for p in player_pool if p['name'] == selected)
            plot_pentagon(p['attributes'], selected)

    if st.button("AutoPick Best Team"):
        for pos in positions:
            pos_players = [p for p in player_pool if p['position'] == pos]
            if pos_players:
                best = max(pos_players, key=lambda x: np.mean(list(x['attributes'].values())))
                st.session_state.selected_team[pos] = best['name']
        st.experimental_rerun()

    st.markdown("---")
    st.subheader("Current Team")
    for pos, name in st.session_state.selected_team.items():
        st.write(f"**{pos}**: {name if name else 'None'}")

# --------------------------------------------
# PLAY MATCH TAB
# --------------------------------------------
elif tab == "Play Match":
    st.title("Play a Match")
    if None in st.session_state.selected_team.values():
        st.warning("You must select a full team first.")
    else:
        if st.button("Kick Off"):
            result = random.choices(["Win", "Loss"], weights=[0.5, 0.5])[0]
            xp = 50 if result == "Win" else 20
            st.session_state.xp += xp
            st.success(f"Result: {result} (+{xp} XP)")
            st.session_state.match_log.append({"result": result, "xp": xp})

    if st.session_state.match_log:
        st.subheader("Match History")
        for match in st.session_state.match_log:
            st.write(f"{match['result']} (+{match['xp']} XP)")

# --------------------------------------------
# TRAINING TAB
# --------------------------------------------
elif tab == "Training":
    st.title("Training Center")
    st.write(f"XP: {st.session_state.xp}")
    selected = [n for n in st.session_state.selected_team.values() if n]
    if not selected:
        st.warning("Select a team first.")
    else:
        player = st.selectbox("Pick Player", selected)
        stat = st.selectbox("Stat", ['Speed', 'Strength', 'Skill', 'Endurance', 'Agility'])
        if st.button("Train +2"):
            if st.session_state.xp >= 20:
                p = next(p for p in player_pool if p['name'] == player)
                p['attributes'][stat] += 2
                if p['attributes'][stat] > 100:
                    p['attributes'][stat] = 100
                st.session_state.xp -= 20
                st.success(f"{player} trained +2 {stat}")
            else:
                st.error("Not enough XP")

# --------------------------------------------
# SQUAD TAB
# --------------------------------------------
elif tab == "Squad":
    st.title("Full Squad")
    for p in player_pool:
        st.write(f"{p['name']} ({p['position']})")
        plot_pentagon(p['attributes'], p['name'])
