import streamlit as st
import json
import random

# Load players
with open('players.json') as f:
    player_pool = json.load(f)

# Initialize session state
if 'squad' not in st.session_state:
    # Start with exactly enough players for one starting team: 4 F, 4 M, 2 R, 4 D, 3 Bench
    positions_needed = {
        "Forward": 4,
        "Midfield": 4,
        "Ruck": 2,
        "Defender": 4,
        "Bench": 3
    }
    initial_squad = []
    remaining = player_pool.copy()
    for position, count in positions_needed.items():
        pos_players = [p for p in remaining if p['position'] == position or (position == "Bench")]
        selected = random.sample(pos_players, count)
        initial_squad.extend(selected)
        for s in selected:
            if s in remaining:
                remaining.remove(s)
    st.session_state['squad'] = initial_squad
    st.session_state['xp'] = 0
    st.session_state['coins'] = 500
    st.session_state['selected_team'] = []

# Tabs
tab = st.sidebar.radio("Navigation", ["Squad", "Selected Team", "Play Match", "Training", "Trade/Delist", "Store"])

# Squad tab
if tab == "Squad":
    st.header(f"Squad | XP: {st.session_state['xp']} | Coins: {st.session_state['coins']}")
    for p in st.session_state['squad']:
        st.write(
            f"{p['name']} | {p['position']} | "
            f"OVR:{p['ovr']} | "
            f"G:{p['goals']} D:{p['disposals']} T:{p['tackles']} "
            f"I50:{p['inside50']} R50:{p['rebound50']} 1%:{p['onepercenters']} HO:{p['hitouts']}"
        )

# Selected Team tab
elif tab == "Selected Team":
    st.header("Select Your Team")
    st.write("Pick your starting 22")

    selected_players = []
    for idx in range(1, 23):
        player_name = st.selectbox(
            f"Select Player {idx}",
            [p['name'] for p in st.session_state['squad']],
            key=f"selectbox_{idx}"
        )
        selected_players.append(player_name)

    st.session_state['selected_team'] = selected_players

    if st.button("Confirm Team"):
        st.success(f"Team confirmed with {len(selected_players)} players")

# Play Match tab
elif tab == "Play Match":
    st.header("Play Match")
    if st.button("Play vs AI Team"):
        # Simulate simple win/loss/draw
        result = random.choice(["Win", "Loss", "Draw"])
        if result == "Win":
            st.session_state['xp'] += 50
            st.session_state['coins'] += 100
        elif result == "Draw":
            st.session_state['xp'] += 25
            st.session_state['coins'] += 50
        else:
            st.session_state['xp'] += 10

        st.success(f"Result: {result}")
        st.write(f"XP: {st.session_state['xp']} | Coins: {st.session_state['coins']}")

# Training tab
elif tab == "Training":
    st.header("Training")
    player_name = st.selectbox(
        "Select player to train",
        [p['name'] for p in st.session_state['squad']],
        key="training_select"
    )
    stat_to_train = st.selectbox("Select stat", ["goals", "disposals", "tackles", "inside50", "rebound50", "onepercenters", "hitouts"], key="stat_select")
    if st.button("Train"):
        for p in st.session_state['squad']:
            if p['name'] == player_name:
                p[stat_to_train] += 0.1  # Small improvement
                st.session_state['xp'] -= 10  # Cost
                st.success(f"{player_name} trained {stat_to_train}")

# Trade/Delist tab
elif tab == "Trade/Delist":
    st.header("Trade or Delist Players")
    player_name = st.selectbox(
        "Select player to delist",
        [p['name'] for p in st.session_state['squad']],
        key="delist_select"
    )
    if st.button("Delist"):
        st.session_state['squad'] = [p for p in st.session_state['squad'] if p['name'] != player_name]
        st.success(f"{player_name} removed from squad")

# Store tab
elif tab == "Store":
    st.header("Store")
    st.write("Buy new packs for 200 coins")
    if st.button("Buy Pack"):
        if st.session_state['coins'] >= 200:
            st.session_state['coins'] -= 200
            new_players = random.sample(player_pool, 5)
            st.session_state['squad'].extend(new_players)
            st.success(f"Pack opened! Added {len(new_players)} new players")
        else:
            st.warning("Not enough coins")
