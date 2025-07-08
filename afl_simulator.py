import streamlit as st
import json
import random

# Load full player pool
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

# Tabs
tab = st.sidebar.radio("Menu", ["Squad", "Selected Team", "Training", "Trade/Delist", "Store"])

# Squad tab
if tab == "Squad":
    st.title("Your Squad")
    st.write(f"XP: {st.session_state['xp']} | Coins: {st.session_state['coins']}")

    for p in st.session_state['squad']:
        st.write(
            f"{p['name']} ({p['year']}) | {p['position']} | OVR:{p['ovr']} | "
            f"G:{p['goals']} D:{p['disposals']} T:{p['tackles']} "
            f"I50:{p['inside50']} R50:{p['rebound50']} 1%:{p['onepercenters']} HO:{p['hitouts']}"
        )

# Selected Team tab
elif tab == "Selected Team":
    st.title("Select Your Team")

    st.write("Your Squad:")
    for p in st.session_state['squad']:
        st.write(f"{p['name']} | {p['position']} | OVR:{p['ovr']}")

    selected_name = st.selectbox(
        "Pick player to add to Selected Team:",
        [p['name'] for p in st.session_state['squad']]
    )

    if st.button("Add Player"):
        player = next(p for p in st.session_state['squad'] if p['name'] == selected_name)
        if player not in st.session_state['selected_team']:
            st.session_state['selected_team'].append(player)
            st.success(f"Added {player['name']} to Selected Team.")

    st.write("Selected Team:")
    for p in st.session_state['selected_team']:
        st.write(f"{p['name']} | {p['position']} | OVR:{p['ovr']}")

# Training tab
elif tab == "Training":
    st.title("Training")

    st.write("Spend XP to boost a player stat!")

    player_name = st.selectbox(
        "Select player to train:",
        [p['name'] for p in st.session_state['squad']]
    )

    stat = st.selectbox("Stat to boost:", ["ovr", "goals", "disposals", "tackles"])

    cost = 50
    if st.button(f"Train (+1 {stat}, Costs {cost} XP)"):
        if st.session_state['xp'] >= cost:
            for p in st.session_state['squad']:
                if p['name'] == player_name:
                    p[stat] += 1
            st.session_state['xp'] -= cost
            st.success(f"Trained {player_name}'s {stat} by 1!")
        else:
            st.error("Not enough XP!")

# Trade/Delist tab
elif tab == "Trade/Delist":
    st.title("Trade / Delist")

    player_name = st.selectbox(
        "Select player to delist:",
        [p['name'] for p in st.session_state['squad']]
    )

    if st.button("Delist Player"):
        st.session_state['squad'] = [
            p for p in st.session_state['squad'] if p['name'] != player_name
        ]
        st.success(f"Delisted {player_name}")

# Store tab
elif tab == "Store":
    st.title("Store - Buy Pack")

    cost = 200

    if st.button(f"Buy Pack (5 players, 1 rare, {cost} coins)"):
        if st.session_state['coins'] >= cost:
            new_players = random.sample(player_pool, 4)
            rare = random.choice([p for p in player_pool if p['ovr'] > 85])
            new_players.append(rare)
            st.session_state['squad'].extend(new_players)
            st.session_state['coins'] -= cost
            st.success(f"Packed 5 players! Rare: {rare['name']}")
        else:
            st.error("Not enough coins!")

# Simulate match result & rewards (optional)
if st.sidebar.button("Play Match"):
    if len(st.session_state['selected_team']) < 18:
        st.warning("You must select at least 18 players to play.")
    else:
        result = random.choice(["Win", "Draw", "Loss"])
        st.write(f"Result: {result}")
        if result == "Win":
            st.session_state['xp'] += 100
            st.session_state['coins'] += 150
        elif result == "Draw":
            st.session_state['xp'] += 50
            st.session_state['coins'] += 75
        else:
            st.session_state['xp'] += 20
            st.session_state['coins'] += 30
        st.success(f"Earned XP & Coins for {result}!")
