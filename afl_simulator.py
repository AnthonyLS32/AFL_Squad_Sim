import streamlit as st
import json
import random

# Load player pool
with open('players.json') as f:
    player_pool = json.load(f)

# Ensure squad exists
if 'squad' not in st.session_state:
    # Start with position-balanced squad
    forwards = [p for p in player_pool if p['position'] == 'Forward'][:4]
    mids = [p for p in player_pool if p['position'] == 'Midfield'][:4]
    rucks = [p for p in player_pool if p['position'] == 'Ruck'][:2]
    defs = [p for p in player_pool if p['position'] == 'Defender'][:4]
    bench = random.sample(player_pool, 3)
    st.session_state['squad'] = forwards + mids + rucks + defs + bench
    st.session_state['coins'] = 500
    st.session_state['xp'] = 0
    st.session_state['selected_team'] = []

# Tabs
tab = st.sidebar.radio("Go to", ["Squad", "Selected Team", "Play Match", "Training", "Trade/Delist", "Store"])

# Squad
if tab == "Squad":
    st.title("Your Squad")
    st.write(f"XP: {st.session_state['xp']} | Coins: {st.session_state['coins']}")
    for p in st.session_state['squad']:
        st.write(
            f"{p['name']} | {p['position']} | OVR: {p['ovr']} | G:{p['goals']} D:{p['disposals']} T:{p['tackles']} "
            f"I50:{p['inside50']} R50:{p['rebound50']} 1%:{p['onepercenters']} HO:{p['hitouts']}"
        )

# Selected Team
elif tab == "Selected Team":
    st.title("Pick your Selected Team")

    selected = []
    for pos in ["Forward", "Midfield", "Ruck", "Defender"]:
        options = [p['name'] for p in st.session_state['squad'] if p['position'] == pos]
        if options:
            choice = st.selectbox(f"Pick {pos}", options, key=pos)
            selected.append(choice)

    bench_options = [p['name'] for p in st.session_state['squad']]
    for i in range(1, 4):
        choice = st.selectbox(f"Pick Bench Player {i}", bench_options, key=f"Bench{i}")
        selected.append(choice)

    if st.button("Save Team"):
        st.session_state['selected_team'] = selected
        st.success("Team saved!")

# Play Match
elif tab == "Play Match":
    st.title("Play Match")
    if len(st.session_state['selected_team']) < 13:
        st.warning("Please select a full team first!")
    else:
        opponent = random.choice(["Melbourne", "Hawthorn", "Fremantle", "Richmond"])
        st.write(f"Your team vs {opponent}")

        result = random.choice(["Win", "Loss", "Draw"])
        st.write(f"Result: {result}")

        xp_gain = 50 if result == "Win" else 20
        coin_gain = 100 if result == "Win" else 50
        st.session_state['xp'] += xp_gain
        st.session_state['coins'] += coin_gain

        st.write(f"You earned {xp_gain} XP and {coin_gain} coins!")

        st.write("Top Performers:")
        for name in random.sample(st.session_state['selected_team'], 3):
            st.write(f"{name} - Outstanding Game!")

# Training
elif tab == "Training":
    st.title("Training")
    player = st.selectbox("Select Player to Train", [p['name'] for p in st.session_state['squad']], key="train_player")
    stat = st.selectbox("Stat to Train", ["goals", "disposals", "tackles", "inside50", "rebound50", "onepercenters", "hitouts"], key="train_stat")

    if st.button("Train"):
        for p in st.session_state['squad']:
            if p['name'] == player:
                p[stat] += 0.1
                st.session_state['xp'] -= 20
                st.success(f"{player}'s {stat} increased!")

# Trade/Delist
elif tab == "Trade/Delist":
    st.title("Trade / Delist")
    player = st.selectbox("Select Player to Delist", [p['name'] for p in st.session_state['squad']], key="delist_player")

    if st.button("Delist"):
        st.session_state['squad'] = [p for p in st.session_state['squad'] if p['name'] != player]
        st.success(f"{player} has been delisted!")

# Store
elif tab == "Store":
    st.title("Store")
    st.write("Buy a Player Pack for 200 Coins (5 Players, 1 Guaranteed Rare)")
    if st.button("Buy Pack"):
        if st.session_state['coins'] >= 200:
            st.session_state['coins'] -= 200
            new_players = random.sample(player_pool, 5)
            st.session_state['squad'].extend(new_players)
            st.success(f"Pack opened! New players added.")
        else:
            st.warning("Not enough coins!")
