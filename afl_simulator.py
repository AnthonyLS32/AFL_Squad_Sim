import streamlit as st
import json
import random

# Load players.json
with open('players.json') as f:
    player_pool = json.load(f)

# Initialise session state
if 'squad' not in st.session_state:
    st.session_state['squad'] = random.sample(player_pool, 40)

if 'selected_team' not in st.session_state:
    st.session_state['selected_team'] = []

if 'xp' not in st.session_state:
    st.session_state['xp'] = 0

if 'coins' not in st.session_state:
    st.session_state['coins'] = 500

# App tabs
tab = st.sidebar.selectbox(
    "Choose tab",
    ["Squad", "Selected Team", "Training", "Trade/Delist", "Store"]
)

if tab == "Squad":
    st.title("Squad")
    st.write(f"**XP:** {st.session_state['xp']} | **Coins:** {st.session_state['coins']}")
    for p in st.session_state['squad']:
        st.write(f"{p['name']} ({p['year']}) | {p['line']} | OVR: {p['ovr']}")

elif tab == "Selected Team":
    st.title("Select Your Team")
    st.write("Pick your match 17 + Bench with position rules:")

    # Count how many per line
    line_counts = {
        "Forward": sum(1 for p in st.session_state['selected_team'] if p['line'] == "Forward"),
        "Mid": sum(1 for p in st.session_state['selected_team'] if p['line'] == "Mid"),
        "Ruck": sum(1 for p in st.session_state['selected_team'] if p['line'] == "Ruck"),
        "Back": sum(1 for p in st.session_state['selected_team'] if p['line'] == "Back"),
        "Bench": sum(1 for p in st.session_state['selected_team'] if p['line'] == "Bench")
    }

    st.write(
        f"**Forwards:** {line_counts['Forward']}/4 | "
        f"**Mids:** {line_counts['Mid']}/4 | "
        f"**Rucks:** {line_counts['Ruck']}/2 | "
        f"**Backs:** {line_counts['Back']}/4 | "
        f"**Bench:** {line_counts['Bench']}/3"
    )

    available_names = [p['name'] for p in st.session_state['squad'] if p not in st.session_state['selected_team']]
    selected_name = st.selectbox(
        "Select player to add:", available_names
    )

    if st.button("Add Player"):
        player = next(p for p in st.session_state['squad'] if p['name'] == selected_name)
        pos = player['line']
        if pos not in ["Forward", "Mid", "Ruck", "Back"]:
            pos = "Bench"

        limits = {"Forward": 4, "Mid": 4, "Ruck": 2, "Back": 4, "Bench": 3}

        if line_counts[pos] >= limits[pos]:
            st.warning(f"Max {pos}s reached.")
        else:
            st.session_state['selected_team'].append(player)
            st.success(f"Added {player['name']} to {pos}.")

    st.subheader("Your Selected Team:")
    for p in st.session_state['selected_team']:
        st.write(f"{p['name']} ({p['line']}) | OVR: {p['ovr']}")

elif tab == "Training":
    st.title("Training")
    st.write("Training logic goes here. Earn XP to boost players!")

elif tab == "Trade/Delist":
    st.title("Trade / Delist")
    st.write("Manage your squad. Sell or delist players here.")

elif tab == "Store":
    st.title("Store")
    st.write("Use coins to buy packs.")
