import streamlit as st
import json
import random

# Load player pool
with open('players_full.json') as f:
    player_pool = json.load(f)

# Load or create squad
try:
    with open('squad.json') as f:
        squad = json.load(f)
except:
    squad = random.sample(player_pool, 22)
    with open('squad.json', 'w') as f:
        json.dump(squad, f)

# Load or create career
try:
    with open('career.json') as f:
        career = json.load(f)
except:
    career = {'round': 1, 'coins': 100, 'xp': 0}
    with open('career.json', 'w') as f:
        json.dump(career, f)

st.title("AFL Ultimate Squad Sim")

tab1, tab2, tab3, tab4 = st.tabs(["My Squad", "Packs", "Career Mode", "Training"])

# Squad tab
with tab1:
    st.header("Your Squad")
    for p in squad:
        st.write(f"{p['name']} ({p['year']}) - {p['position']}")
        st.write(f"OVR: {p['ovr']} | G: {p['goals']} | D: {p['disposals']} | T: {p['tackles']}")
        st.image(p.get('photo_url', 'https://via.placeholder.com/100'), width=100)

# Packs tab
with tab2:
    st.header("Open a Pack")
    st.write(f"Coins: {career['coins']}")
    if st.button("Buy Pack (50 coins)"):
        if career['coins'] >= 50:
            new_card = random.choice(player_pool)
            squad.append(new_card)
            career['coins'] -= 50
            st.success(f"You got {new_card['name']} ({new_card['year']})!")
            with open('squad.json', 'w') as f:
                json.dump(squad, f)
            with open('career.json', 'w') as f:
                json.dump(career, f)
        else:
            st.error("Not enough coins!")

# Career tab
with tab3:
    st.header(f"Round {career['round']} / 23")
    st.write(f"Coins: {career['coins']} | XP: {career['xp']}")
    if st.button("Play Next Match"):
        result = random.choice(["Win", "Loss"])
        coins_earned = 30 if result == "Win" else 10
        xp_earned = 5
        career['coins'] += coins_earned
        career['xp'] += xp_earned
        career['round'] += 1
        st.success(f"{result}! +{coins_earned} Coins, +{xp_earned} XP")
        with open('career.json', 'w') as f:
            json.dump(career, f)

# Training tab
with tab4:
    st.header("Train a Player")
    st.write(f"XP Available: {career['xp']}")
    names = [f"{p['name']} ({p['year']})" for p in squad]
    choice = st.selectbox("Pick player to train:", names)
    if st.button("Train (+1 OVR, -5 XP)"):
        if career['xp'] >= 5:
            for p in squad:
                if f"{p['name']} ({p['year']})" == choice:
                    p['ovr'] += 1
                    break
            career['xp'] -= 5
            st.success("Player improved!")
            with open('squad.json', 'w') as f:
                json.dump(squad, f)
            with open('career.json', 'w') as f:
                json.dump(career, f)
        else:
            st.error("Not enough XP!")
