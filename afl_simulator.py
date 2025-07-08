import streamlit as st
import json
import random

# Load player pool
with open('players.json') as f:
    player_pool = json.load(f)

# Setup session state
if 'squad' not in st.session_state:
    forwards = [p for p in player_pool if p['position'] == 'Forward'][:4]
    mids = [p for p in player_pool if p['position'] == 'Midfield'][:4]
    defenders = [p for p in player_pool if p['position'] == 'Defender'][:4]
    rucks = [p for p in player_pool if p['position'] == 'Ruck'][:2]
    bench = random.sample(player_pool, 4)
    st.session_state['squad'] = forwards + mids + defenders + rucks + bench
    st.session_state['selected_team'] = []
    st.session_state['coins'] = 500
    st.session_state['xp'] = 0

tabs = st.tabs(['Squad', 'Selected Team', 'Play Match', 'Training', 'Trade/Delist', 'Store'])

# === Squad ===
with tabs[0]:
    st.header("Your Squad")
    for p in st.session_state['squad']:
        st.write(f"{p['name']} | {p['position']} | OVR:{p['ovr']} | G:{p['goals']} D:{p['disposals']} T:{p['tackles']} I50:{p['inside50']} R50:{p['rebound50']} 1%:{p['onepercenters']} HO:{p['hitouts']}")

# === Selected Team ===
with tabs[1]:
    st.header("Select Your Team")
    if st.button('Add to Selected Team'):
        available = [p for p in st.session_state['squad'] if p not in st.session_state['selected_team']]
        if available:
            st.session_state['selected_team'].append(random.choice(available))
    st.write("Selected:")
    for p in st.session_state['selected_team']:
        st.write(f"{p['name']} | {p['position']} | OVR:{p['ovr']}")

# === Play Match ===
with tabs[2]:
    st.header("Play a Match")
    if st.button('Play Match'):
        if len(st.session_state['selected_team']) < 17:
            st.warning("Not enough players selected!")
        else:
            result = random.choice(['Win', 'Draw', 'Loss'])
            st.write(f"Result: {result}")
            if result == 'Win':
                st.session_state['coins'] += 100
                st.session_state['xp'] += 50
            elif result == 'Draw':
                st.session_state['coins'] += 50
                st.session_state['xp'] += 20
            st.write(f"Coins: {st.session_state['coins']} | XP: {st.session_state['xp']}")

# === Training ===
with tabs[3]:
    st.header("Training")
    player = st.selectbox("Select Player", st.session_state['squad'])
    stat = st.selectbox("Stat to Train", ['goals', 'disposals', 'tackles'])
    if st.button('Train'):
        if st.session_state['xp'] >= 20:
            player[stat] += 0.5
            st.session_state['xp'] -= 20
            st.success(f"Trained {player['name']}: +0.5 {stat}")
        else:
            st.warning("Not enough XP!")

# === Trade/Delist ===
with tabs[4]:
    st.header("Trade/Delist")
    player = st.selectbox("Select Player", st.session_state['squad'])
    if st.button('Delist Player'):
        st.session_state['squad'].remove(player)
        st.success(f"Delisted {player['name']}")

    st.header("Store")
    if st.button('Buy Pack (5 Players, 1 Rare) - 200 Coins'):
        if st.session_state['coins'] >= 200:
            new_players = random.sample(player_pool, 5)
            st.session_state['squad'].extend(new_players)
            st.session_state['coins'] -= 200
            st.success("Pack opened! 5 new players added.")
        else:
            st.warning("Not enough coins!")
