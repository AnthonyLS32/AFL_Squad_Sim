import streamlit as st
import json
import random

# Load players.json
with open('players.json') as f:
    player_pool = json.load(f)

# Initialize session state
if 'squad' not in st.session_state:
    st.session_state['squad'] = player_pool.copy()

if 'selected_team' not in st.session_state:
    defenders = [p for p in player_pool if p['position'] == "Defender"]
    midfields = [p for p in player_pool if p['position'] == "Midfield"]
    forwards = [p for p in player_pool if p['position'] == "Forward"]
    rucks = [p for p in player_pool if p['position'] == "Ruck"]
    bench = [p for p in player_pool if p['position'] == "Bench"]

    selected_team = []
    selected_team += random.sample(forwards, min(4, len(forwards)))
    selected_team += random.sample(midfields, min(4, len(midfields)))
    selected_team += random.sample(rucks, min(2, len(rucks)))
    selected_team += random.sample(defenders, min(4, len(defenders)))
    selected_team += random.sample(bench, min(3, len(bench)))

    st.session_state['selected_team'] = selected_team

if 'xp' not in st.session_state:
    st.session_state['xp'] = 0

if 'coins' not in st.session_state:
    st.session_state['coins'] = 500

tab = st.sidebar.selectbox(
    "Choose tab",
    ["Squad", "Selected Team", "Training", "Trade/Delist", "Store"]
)

def player_full_stats_str(p):
    return (
        f"{p['name']} | Pos: {p['position']} | Line: {p.get('line', 'N/A')} | "
        f"OVR: {p['ovr']} | G:{p.get('goals',0)} "
        f"D:{p.get('disposals',0)} T:{p.get('tackles',0)} "
        f"I50:{p.get('inside50',0)} R50:{p.get('rebound50',0)} "
        f"1%:{p.get('onepercenters',0)} HO:{p.get('hitouts',0)}"
    )

if tab == "Squad":
    st.title("Full Squad")
    st.write(f"XP: {st.session_state['xp']} | Coins: {st.session_state['coins']}")
    for p in st.session_state['squad']:
        st.write(player_full_stats_str(p))

elif tab == "Selected Team":
    st.title("Selected Team")
    st.write(f"XP: {st.session_state['xp']} | Coins: {st.session_state['coins']}")

    limits = {"Forward": 4, "Midfield": 4, "Ruck": 2, "Defender": 4, "Bench": 3}

    pos_counts = {pos: 0 for pos in limits.keys()}
    for p in st.session_state['selected_team']:
        pos = p.get('position', 'Bench')
        if pos not in pos_counts:
            pos = 'Bench'
        pos_counts[pos] += 1

    st.write(
        f"Selected Team Counts: Forwards {pos_counts['Forward']}/4, "
        f"Midfields {pos_counts['Midfield']}/4, Rucks {pos_counts['Ruck']}/2, "
        f"Defenders {pos_counts['Defender']}/4, Bench {pos_counts['Bench']}/3"
    )

    for pos in ["Defender", "Midfield", "Ruck", "Forward", "Bench"]:
        st.subheader(f"{pos}s:")
        players = [pl for pl in st.session_state['selected_team'] if pl.get('position','Bench') == pos]
        for p in players:
            st.write(player_full_stats_str(p))

    available_names = [p['name'] for p in st.session_state['squad'] if p not in st.session_state['selected_team']]
    selected_name = st.selectbox("Select player to add:", available_names)

    if st.button("Add Player"):
        player = next(p for p in st.session_state['squad'] if p['name'] == selected_name)
        pos = player.get('position', 'Bench')
        if pos not in limits:
            pos = 'Bench'

        if pos_counts[pos] >= limits[pos]:
            st.warning(f"Max {pos}s reached.")
        else:
            st.session_state['selected_team'].append(player)
            st.success(f"Added {player['name']} to {pos}.")

elif tab == "Training":
    st.title("Training")
    st.write("Training features coming soon...")

elif tab == "Trade/Delist":
    st.title("Trade / Delist")
    st.write("Manage players coming soon...")

elif tab == "Store":
    st.title("Store")
    st.write("Purchase packs and items coming soon...")
