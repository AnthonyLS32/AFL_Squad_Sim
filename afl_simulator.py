import json
import random
import streamlit as st

# Load player pool
with open('players_full.json') as f:
    player_pool = json.load(f)

# Init session state
if 'squad' not in st.session_state:
    st.session_state['squad'] = random.sample(player_pool, 22)
if 'xp' not in st.session_state:
    st.session_state['xp'] = 0
if 'coins' not in st.session_state:
    st.session_state['coins'] = 500
if 'last_pack' not in st.session_state:
    st.session_state['last_pack'] = []

# Functions
def open_pack():
    if st.session_state['coins'] < 100:
        st.error("Not enough coins to buy a pack.")
        return
    pack = []
    attempts = 0
    while len(pack) < 5 and attempts < 50:
        new_player = random.choice(player_pool)
        if not any(p['name'] == new_player['name'] and p['year'] == new_player['year'] for p in st.session_state['squad'] + pack):
            pack.append(new_player)
        attempts += 1
    st.session_state['squad'].extend(pack)
    st.session_state['coins'] -= 100
    st.session_state['last_pack'] = pack
    st.success(f"Pack opened! {len(pack)} players added.")

def delist_player(name):
    if len(st.session_state['squad']) <= 22:
        st.warning("Cannot delist below 22 players.")
        return
    st.session_state['squad'] = [p for p in st.session_state['squad'] if p['name'] != name]
    st.success(f"{name} delisted!")

def train_player(name, stat):
    if st.session_state['coins'] < 25:
        st.error("Not enough coins to train.")
        return
    for p in st.session_state['squad']:
        if p['name'] == name:
            p[stat] += 0.5
            st.session_state['coins'] -= 25
            st.success(f"{name}'s {stat} increased by 0.5!")
            break

def swap_players(player_out, player_in):
    out = next((p for p in st.session_state['squad'] if p['name'] == player_out), None)
    if out is None:
        st.error("Player not found in squad.")
        return
    if out['line'] != player_in['line']:
        st.error("Must swap within same position group.")
        return
    st.session_state['squad'].remove(out)
    st.session_state['squad'].append(player_in)
    st.success(f"Swapped {player_out} with {player_in['name']}.")

def play_match():
    my_ovr = sum([p['ovr'] for p in st.session_state['squad']]) / len(st.session_state['squad'])
    ai_team = random.sample(player_pool, 22)
    ai_ovr = sum([p['ovr'] for p in ai_team]) / 22
    st.write(f"Your OVR: {my_ovr:.1f} | AI OVR: {ai_ovr:.1f}")
    if my_ovr >= ai_ovr:
        st.success("You won! +100 XP +100 Coins")
        st.session_state['xp'] += 100
        st.session_state['coins'] += 100
    else:
        st.warning("You lost. +50 XP +50 Coins")
        st.session_state['xp'] += 50
        st.session_state['coins'] += 50

# Tabs
tabs = st.tabs(["Squad", "Selected Team", "Training", "Trade/Delist", "Store"])

with tabs[0]:
    st.header(f"Squad | XP: {st.session_state['xp']} | Coins: {st.session_state['coins']}")
    for p in st.session_state['squad']:
        st.write(f"{p['name']} ({p['year']}) | {p['line']} | OVR:{p['ovr']} | G:{p['goals']} D:{p['disposals']} T:{p['tackles']} I50:{p['inside50']} R50:{p['rebound50']} 1%:{p['onepercenters']} HO:{p['hitouts']}")

with tabs[1]:
    st.header("Selected Team (Oval View)")
    for line in ['Forward', 'Mid', 'Back', 'Ruck']:
        st.subheader(f"{line}s")
        for p in [x for x in st.session_state['squad'] if x['line'] == line][:5]:
            st.write(f"{p['name']} | OVR:{p['ovr']}")

    bench = st.session_state['squad'][18:]
    st.subheader("Bench")
    for p in bench:
        st.write(f"{p['name']} | {p['line']} | OVR:{p['ovr']}")

with tabs[2]:
    st.header("Training")
    name = st.selectbox("Player", [p['name'] for p in st.session_state['squad']])
    stat = st.selectbox("Stat", ["goals", "disposals", "tackles", "inside50", "rebound50", "onepercenters", "hitouts"])
    if st.button("Train (25 Coins)"):
        train_player(name, stat)

with tabs[3]:
    st.header("Trade / Delist")
    player_out = st.selectbox("Swap Out", [p['name'] for p in st.session_state['squad']])
    player_in = st.selectbox("Swap In", [p['name'] for p in player_pool])
    if st.button("Swap"):
        in_obj = next((p for p in player_pool if p['name'] == player_in), None)
        swap_players(player_out, in_obj)

    delist_name = st.selectbox("Delist", [p['name'] for p in st.session_state['squad']])
    if st.button("Delist"):
        delist_player(delist_name)

with tabs[4]:
    st.header("Store")
    if st.button("Open Pack (100 Coins)"):
        open_pack()
    if st.button("Play Match"):
        play_match()

    if st.session_state['last_pack']:
        st.subheader("Last Pack:")
        for p in st.session_state['last_pack']:
            st.write(f"{p['name']} | {p['line']} | OVR:{p['ovr']}")
