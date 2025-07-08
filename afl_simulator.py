import streamlit as st
import json
import random
import os

# ---- Load player pool ----
with open('players_full.json') as f:
    player_pool = json.load(f)

# ---- Squad & Career Session ----
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

# ---- App Title ----
st.title("🏉 AFL Ultimate Squad — Prototype FUT Version")

# ---- Display helper ----
def display_player_card(player):
    st.image(player.get('photo_url', 'https://via.placeholder.com/80'), width=80)
    st.write(f"**{player['name']}** ({player['year']})")
    st.write(f"{player['position']} | OVR: {player['ovr']}")
    st.write(f"G: {player['goals']} | D: {player['disposals']} | T: {player['tackles']}")

# ---- Squad Layout ----
st.header("📌 Squad on Field")

backs = [p for p in squad if p['line'] == 'Back'][:6]
mids = [p for p in squad if p['line'] == 'Mid'][:6]
forwards = [p for p in squad if p['line'] == 'Forward'][:6]
rucks = [p for p in squad if p['line'] == 'Ruck'][:2]
bench = squad[20:]

st.subheader("Backs")
cols = st.columns(len(backs))
for idx, p in enumerate(backs):
    with cols[idx]:
        display_player_card(p)

st.subheader("Midfielders")
cols = st.columns(len(mids))
for idx, p in enumerate(mids):
    with cols[idx]:
        display_player_card(p)

st.subheader("Forwards")
cols = st.columns(len(forwards))
for idx, p in enumerate(forwards):
    with cols[idx]:
        display_player_card(p)

st.subheader("Ruck")
cols = st.columns(len(rucks))
for idx, p in enumerate(rucks):
    with cols[idx]:
        display_player_card(p)

st.subheader("Bench")
cols = st.columns(len(bench))
for idx, p in enumerate(bench):
    with cols[idx]:
        display_player_card(p)

# ---- Swap Players ----
st.header("🔄 Swap Players")

# Only allow swap within same line
main_options = [f"{i+1}: {p['name']} ({p['line']})" for i, p in enumerate(squad[:20])]
bench_options = [f"{20+i+1}: {p['name']} ({p['line']})" for i, p in enumerate(bench)]

swap_out = st.selectbox("Swap OUT (on-field)", main_options)
swap_in = st.selectbox("Swap IN (bench)", bench_options)

if st.button("Confirm Swap"):
    idx_out = int(swap_out.split(":")[0]) - 1
    idx_in = int(swap_in.split(":")[0]) - 1
    if squad[idx_out]['line'] == squad[idx_in]['line']:
        squad[idx_out], squad[idx_in] = squad[idx_in], squad[idx_out]
        with open('squad.json', 'w') as f:
            json.dump(squad, f)
        st.success(f"Swapped {squad[idx_out]['name']} with {squad[idx_in]['name']}")
    else:
        st.warning("Swap failed: lines must match!")

# ---- Delist ----
st.header("🚮 Delist Player")
delist_options = [f"{i+1}: {p['name']} ({p['position']})" for i, p in enumerate(squad)]
delist_player = st.selectbox("Pick to delist", delist_options)
if st.button("Delist"):
    idx = int(delist_player.split(":")[0]) - 1
    gone = squad.pop(idx)
    with open('squad.json', 'w') as f:
        json.dump(squad, f)
    st.success(f"{gone['name']} has been delisted!")

# ---- Career Mode ----
st.header(f"🎮 Career Mode — Round {career['round']}/23")
if career['round'] <= 23:
    ai_team = random.sample(player_pool, 22)
    ai_ovr = sum(p['ovr'] for p in ai_team) / len(ai_team)
    my_ovr = sum(p['ovr'] for p in squad) / len(squad)
    st.write(f"Your Avg OVR: {my_ovr:.1f} | Opponent Avg OVR: {ai_ovr:.1f}")

    if st.button("Play Match"):
        result = random.random() + (my_ovr - ai_ovr) / 100
        if result > 0.55:
            outcome = "🏆 WIN!"
            coins = 50
            xp = 10
        elif result > 0.45:
            outcome = "🤝 DRAW!"
            coins = 30
            xp = 5
        else:
            outcome = "❌ LOSS!"
            coins = 10
            xp = 2
        career['coins'] += coins
        career['xp'] += xp
        career['round'] += 1
        with open('career.json', 'w') as f:
            json.dump(career, f)
        st.success(f"{outcome} +{coins} Coins | +{xp} XP")
else:
    st.write("✅ Season complete!")

# ---- Packs ----
st.header("🎁 Buy Pack (5 players)")
st.write(f"Coins: {career['coins']}")
if st.button("Buy Pack (50 coins)"):
    if career['coins'] >= 50:
        pack = random.sample(player_pool, 5)
        pack[-1] = random.choice([p for p in player_pool if p['ovr'] >= 90])
        squad.extend(pack)
        career['coins'] -= 50
        with open('squad.json', 'w') as f:
            json.dump(squad, f)
        with open('career.json', 'w') as f:
            json.dump(career, f)
        st.success(f"New players: {[p['name'] for p in pack]}")
    else:
        st.warning("Not enough coins!")

# ---- Training ----
st.header("📈 Training")
st.write(f"XP Available: {career['xp']}")
train_options = [f"{i+1}: {p['name']} ({p['position']})" for i, p in enumerate(squad)]
selected_player = st.selectbox("Pick to train", train_options)
selected_stat = st.selectbox("Stat to boost", ["goals", "disposals", "tackles"])

if st.button("Train (+0.1, -5 XP)"):
    if career['xp'] >= 5:
        idx = int(selected_player.split(":")[0]) - 1
        squad[idx][selected_stat] += 0.1
        career['xp'] -= 5
        with open('squad.json', 'w') as f:
            json.dump(squad, f)
        with open('career.json', 'w') as f:
            json.dump(career, f)
        st.success(f"Trained {squad[idx]['name']} +0.1 {selected_stat}")
    else:
        st.warning("Not enough XP!")
