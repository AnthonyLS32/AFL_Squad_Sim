import json
import random
import streamlit as st

# Load player pool
with open('players_full.json') as f:
    player_pool = json.load(f)

# Ensure enough players
if len(player_pool) < 22:
    st.error("Your player pool must have at least 22 players!")
    st.stop()

# Initialize squad
if 'squad' not in st.session_state:
    st.session_state['squad'] = random.sample(player_pool, 22)

# Functions
def open_pack():
    commons = random.sample([p for p in player_pool if p['ovr'] < 90], 4)
    rare = random.choice([p for p in player_pool if p['ovr'] >= 90])
    pack = commons + [rare]
    st.session_state['squad'].extend(pack)
    st.success("✅ Pack opened! 5 new players added.")

def delist_player(name):
    st.session_state['squad'] = [p for p in st.session_state['squad'] if p['name'] != name]
    st.success(f"🚮 {name} delisted!")

def train_player(name, stat):
    for p in st.session_state['squad']:
        if p['name'] == name:
            if stat in ['goals', 'disposals', 'tackles']:
                p[stat] += 0.5
                st.success(f"💪 Trained {name}'s {stat}!")
            break

def swap_players(player_out, player_in):
    out = next((p for p in st.session_state['squad'] if p['name'] == player_out), None)
    if out is None:
        st.error("Player to swap out not found.")
        return
    if out['line'] != player_in['line']:
        st.error("Position mismatch! Must match line.")
        return
    st.session_state['squad'].remove(out)
    st.session_state['squad'].append(player_in)
    st.success(f"🔄 Swapped {player_out} for {player_in['name']}")

# UI
st.title("🏉 AFL Squad FUT-Style")

# Squad overview
st.subheader("Your Squad (on the Oval)")
for p in st.session_state['squad']:
    st.write(f"• {p['name']} | {p['line']} | OVR: {p['ovr']} | G:{p['goals']} D:{p['disposals']} T:{p['tackles']}")

# Open Pack
if st.button("Open Player Pack 🎁"):
    open_pack()

# Delist
st.subheader("Delist a Player")
delist_name = st.selectbox("Select to delist:", [p['name'] for p in st.session_state['squad']])
if st.button("Delist 🚮"):
    delist_player(delist_name)

# Train
st.subheader("Train a Player")
train_name = st.selectbox("Player to Train:", [p['name'] for p in st.session_state['squad']])
train_stat = st.selectbox("Which stat?", ["goals", "disposals", "tackles"])
if st.button("Train 📈"):
    train_player(train_name, train_stat)

# Swap
st.subheader("Swap Players")
player_out = st.selectbox("Swap OUT:", [p['name'] for p in st.session_state['squad']])
player_in = st.selectbox("Swap IN (from pool):", [p['name'] for p in player_pool])
if st.button("Swap 🔄"):
    in_player_obj = next((p for p in player_pool if p['name'] == player_in), None)
    if in_player_obj:
        swap_players(player_out, in_player_obj)

# Simulate match
st.subheader("Play Match vs AI 🤖")
if st.button("Play Match"):
    my_ovr = sum([p['ovr'] for p in st.session_state['squad']]) / len(st.session_state['squad'])
    ai_team = random.sample(player_pool, 22)
    ai_ovr = sum([p['ovr'] for p in ai_team]) / len(ai_team)
    st.write(f"Your Team OVR: {my_ovr:.1f}")
    st.write(f"AI Team OVR: {ai_ovr:.1f}")
    if my_ovr > ai_ovr:
        st.success("🏆 You Won!")
    else:
        st.error("❌ You Lost!")

# Debug
st.caption("Tip: Your squad stays saved in session.")
