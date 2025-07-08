import json
import random
import streamlit as st

# Load player pool
with open('players_full.json') as f:
    player_pool = json.load(f)

# Make sure pool is big enough
if len(player_pool) < 22:
    st.error("Your player pool must have at least 22 players.")
    st.stop()

# Init squad & XP
if 'squad' not in st.session_state:
    st.session_state['squad'] = random.sample(player_pool, 22)
if 'xp' not in st.session_state:
    st.session_state['xp'] = 0
if 'last_pack' not in st.session_state:
    st.session_state['last_pack'] = []

# Functions
def open_pack():
    commons = random.sample([p for p in player_pool if p['ovr'] < 90], 4)
    rare = random.choice([p for p in player_pool if p['ovr'] >= 90])
    pack = commons + [rare]
    st.session_state['squad'].extend(pack)
    st.session_state['last_pack'] = pack
    st.success(f"🎉 Pack opened! Got {len(pack)} players.")

def delist_player(name):
    st.session_state['squad'] = [p for p in st.session_state['squad'] if p['name'] != name]
    st.success(f"🚮 {name} delisted!")

def train_player(name, stat):
    for p in st.session_state['squad']:
        if p['name'] == name:
            p[stat] += 0.5
            st.success(f"💪 Trained {name}'s {stat} by 0.5!")
            break

def swap_players(player_out, player_in):
    out = next((p for p in st.session_state['squad'] if p['name'] == player_out), None)
    if out is None:
        st.error("Player to swap out not found.")
        return
    if out['line'] != player_in['line']:
        st.error("Must swap within same line!")
        return
    st.session_state['squad'].remove(out)
    st.session_state['squad'].append(player_in)
    st.success(f"🔄 Swapped {player_out} for {player_in['name']}")

def play_match():
    my_ovr = sum([p['ovr'] for p in st.session_state['squad']]) / len(st.session_state['squad'])
    ai_team = random.sample(player_pool, 22)
    ai_ovr = sum([p['ovr'] for p in ai_team]) / 22
    st.write(f"Your Team OVR: {my_ovr:.1f}")
    st.write(f"AI Team OVR: {ai_ovr:.1f}")
    if my_ovr >= ai_ovr:
        st.success("🏆 You Won! Earned 100 XP and 1 pack!")
        st.session_state['xp'] += 100
        open_pack()
    else:
        st.error("❌ You Lost! Earned 50 XP.")
        st.session_state['xp'] += 50

# UI
st.title("🏉 AFL FUT Career Mode")

st.header(f"Your XP: {st.session_state['xp']}")

# Show squad by lines
def line_group(line):
    return [p for p in st.session_state['squad'] if p['line'] == line]

def show_players(players):
    for p in players:
        st.write(f"{p['name']} | {p['line']} | OVR:{p['ovr']} | G:{p['goals']} D:{p['disposals']} T:{p['tackles']}")

st.subheader("🔵 Forwards")
show_players(line_group('Forward'))

st.subheader("🟢 Mids")
show_players(line_group('Mid'))

st.subheader("🔴 Backs")
show_players(line_group('Back'))

st.subheader("🟡 Rucks")
show_players(line_group('Ruck'))

st.subheader("🟣 Bench (Extra)")
bench = st.session_state['squad'][18:]
show_players(bench)

# Play match
st.subheader("⚡ Play a Match")
if st.button("Play Match vs AI 🤖"):
    play_match()

# Show last pack result
if st.session_state['last_pack']:
    st.subheader("🎁 Last Pack Contents")
    for p in st.session_state['last_pack']:
        st.write(f"{p['name']} | {p['line']} | OVR:{p['ovr']}")

# Open manual pack
if st.button("Open Extra Pack"):
    open_pack()

# Delist
st.subheader("Delist a Player")
delist_name = st.selectbox("Select to delist:", [p['name'] for p in st.session_state['squad']])
if st.button("Delist 🚮"):
    delist_player(delist_name)

# Train
st.subheader("Train a Player")
train_name = st.selectbox("Train who?", [p['name'] for p in st.session_state['squad']])
train_stat = st.selectbox("Which stat?", ["goals", "disposals", "tackles"])
if st.button("Train 📈"):
    train_player(train_name, train_stat)

# Swap
st.subheader("Swap Players")
player_out = st.selectbox("OUT:", [p['name'] for p in st.session_state['squad']])
player_in = st.selectbox("IN:", [p['name'] for p in player_pool])
if st.button("Swap 🔄"):
    in_obj = next((p for p in player_pool if p['name'] == player_in), None)
    if in_obj:
        swap_players(player_out, in_obj)

