import streamlit as st
import json
import random

# Load player pool
with open('players.json') as f:
    player_pool = json.load(f)

# Initialize session state
if 'squad' not in st.session_state:
    st.session_state['squad'] = random.sample(player_pool, 22)
if 'xp' not in st.session_state:
    st.session_state['xp'] = 0
if 'coins' not in st.session_state:
    st.session_state['coins'] = 500

st.title("AFL Squad Simulator")

tab = st.sidebar.radio("Navigation", ["Squad", "Selected Team", "Play Match", "Training", "Trade/Delist", "Store"])

if tab == "Squad":
    st.header(f"Squad | XP: {st.session_state['xp']} | Coins: {st.session_state['coins']}")
    for p in st.session_state['squad']:
        st.write(
            f"{p['name']} | Pos: {p['position']} | OVR: {p['ovr']} | "
            f"G:{p['goals']} D:{p['disposals']} T:{p['tackles']} "
            f"I50:{p['inside50']} R50:{p['rebound50']} 1%:{p['onepercenters']} HO:{p['hitouts']}"
        )

elif tab == "Selected Team":
    st.title("Select Your Team")

    squad = st.session_state['squad']

    required_slots = {
        "Forwards": 4,
        "Midfielders": 4,
        "Rucks": 2,
        "Defenders": 4,
        "Bench": 3
    }

    selected_team = []

    for slot, count in required_slots.items():
        st.subheader(f"{slot}")
        if slot == "Forwards":
            available = [p for p in squad if p['position'] == "Forward"]
        elif slot == "Midfielders":
            available = [p for p in squad if p['position'] == "Midfield"]
        elif slot == "Rucks":
            available = [p for p in squad if p['position'] == "Ruck"]
        elif slot == "Defenders":
            available = [p for p in squad if p['position'] == "Defender"]
        else:
            available = squad  # Bench: any position

        for i in range(count):
            player = st.selectbox(
                f"Select {slot[:-1]} {i+1}",
                options=[f"{p['name']} | OVR: {p['ovr']}" for p in available],
                key=f"{slot}_{i}"
            )
            selected_team.append(player)

    st.write("### Your Selected Team")
    for player in selected_team:
        st.write(player)

elif tab == "Play Match":
    st.title("Play Match")
    st.info("This is where the match simulation will run. [To be implemented]")

elif tab == "Training":
    st.title("Training")
    st.info("This is where you’ll spend XP to improve players. [To be implemented]")

elif tab == "Trade/Delist":
    st.title("Trade / Delist")
    st.info("This is where you’ll manage your squad. [To be implemented]")

elif tab == "Store":
    st.title("Store")
    st.info("This is where you’ll spend coins on packs. [To be implemented]")
