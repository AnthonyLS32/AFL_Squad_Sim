import streamlit as st
import json
import random
import os

# ---- Load players ----
with open('players_full.json') as f:
    player_pool = json.load(f)

# ---- Session State ----
if 'squad' not in st.session_state:
    if os.path.exists('squad.json'):
        with open('squad.json') as f:
            st.session_state['squad'] = json.load(f)
    else:
        st.session_state['squad'] = random.sample(player_pool, 22)
        with open('squad.json', 'w') as f:
            json.dump(st.session_state['squad'], f)

if 'career' not in st.session_state:
    if os.path.exists('career.json'):
        with open('career.json') as f:
            st.session_state['career'] = json.load(f)
    else:
        st.session_state['career'] = {'round': 1, 'coins': 100, 'xp': 0}
        with open('career.json', 'w') as f:
            json.dump(st.session_state['career'], f)

squad = st.session_state['squad']
career = st.session_state['career']

st.title("🏉 AFL Ultimate Squad FUT Prototype")

# ---- Layout helper ----
def display_player_card(player):
    st.image(player.get('photo_url', 'https://via.placeholder.com/100'), width=80)
    st.write(f"**{player['name']}** ({player['year']})")
    age = player.get('year', 2024) - (1987 if 'Lance' in player['name'] else 1995)  # mock
    st.write(f"Age: {age}")
    st.write(f"{player['position']} | OVR: {player['ovr']}")
    st.write(f"G: {player['goals']} | D: {player['disposals']} | T: {player['tackles']}")

# ---- Squad screen ----
st.header("📌 My Squad (Oval Layout)")

backs = squad[:6]
mids = squad[6:12]
forwards = squad[12:18]
bench = squad[18:]

st.subheader("Backs")
cols = st.columns(6)
for idx, p in enumerate(backs):
    with cols[idx]:
        display_player_card(p)

st.subheader("Midfielders & Ruck")
cols = st.columns(6)
for idx, p in enumerate(mids):
    with cols[idx]:
        display_player_card(p)

st.subheader("Forwards")
cols = st.columns(6)
for idx, p in enumerate(forwards):
    with cols[idx]:
        display_player_card(p)

st.subheader("Bench")
cols = st.columns(len(bench))
for idx, p in enumerate(bench):
    with cols[idx]:
        display_player_card(p)

# ---- Swap ----
st.subheader("🔄 Swap Players")
pos_options = [f"{i+1} {p['name']} ({p['position']})" for i, p in enumerate(squad)]
swap_out = st.selectbox("Pick position to replace", pos_options)
swap_in = st.selectbox("Pick bench player to swap in", pos_options[18:])

if st.button("Swap"):
    idx_out = int(swap_out.split()[0]) - 1
    idx_in = int(swap_in.split()[0]) - 1
    squad[idx_out], squad[idx_in] = squad[idx_in], squad[idx_out]
    with open('squad.json', 'w') as f:
        json.dump(squad, f)
    st.success("Swapped!")

# ---- Opponent & Match ----
st.header(f"🎮 Career Mode — Round {career['round']}/23")
if career['round'] <= 23:
    ai_team = random.sample(player_pool, 22)
    ai_ovr = sum([p['ovr'] for p in ai_team]) / len(ai_team)
    my_ovr = sum([p['ovr'] for p in squad]) / len(squad)
    st.write(f"Your Avg OVR: {my_ovr:.1f}")
    st.write(f"Opponent Avg OVR: {ai_ovr:.1f}")
    if st.button("Play Match"):
        result = random.random() + (my_ovr - ai_ovr)/100
        if result > 0.55:
            outcome = "WIN"
            coins = 50
            xp = 10
        elif result > 0.45:
            outcome = "DRAW"
            coins = 30
            xp = 5
        else:
            outcome = "LOSS"
            coins = 10
            xp = 2
        career['coins'] += coins
        career['xp'] += xp
        career['round'] += 1
        with open('career.json', 'w') as f:
            json.dump(career, f)
        st.success(f"{outcome}! +{coins} Coins, +{xp} XP")
else:
    st.write("🏆 Season finished!")

# ---- Packs ----
st.header("🎁 Packs")
st.write(f"Coins: {career['coins']}")
if st.button("Buy Pack (50 coins)"):
    if career['coins'] >= 50:
        new_card = random.choice(player_pool)
        squad.append(new_card)
        career['coins'] -= 50
        with open('squad.json', 'w') as f:
            json.dump(squad, f)
        with open('career.json', 'w') as f:
            json.dump(career, f)
        st.success(f"You got {new_card['name']}!")
    else:
        st.error("Not enough coins!")

# ---- Training ----
st.header("📈 Training")
st.write(f"XP Available: {career['xp']}")
train_choice = st.selectbox("Pick player to train", pos_options)
stat_choice = st.selectbox("Pick stat to train", ["goals", "disposals", "tackles"])

if st.button("Train (+0.1 to stat, -5 XP)"):
    if career['xp'] >= 5:
        idx = int(train_choice.split()[0]) - 1
        squad[idx][stat_choice] += 0.1
        career['xp'] -= 5
        with open('squad.json', 'w') as f:
            json.dump(squad, f)
        with open('career.json', 'w') as f:
            json.dump(career, f)
        st.success(f"Trained {squad[idx]['name']}!")
    else:
        st.error("Not enough XP!")
