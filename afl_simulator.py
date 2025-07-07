import streamlit as st
import json
import random

with open("cards.json") as f:
    cards = json.load(f)

# Load or init squad
try:
    with open("squad.json") as f:
        squad = json.load(f)
except:
    squad = []

st.title("🏉 AFL Squad Simulator")

tab1, tab2, tab3, tab4 = st.tabs(["My Cards", "Build Squad", "Play Match", "Open Pack"])

with tab1:
    st.header("My Cards")
    for card in cards:
        st.write(f"{card['name']} {card['year']} — {card['position']}")

with tab2:
    st.header("Build Squad")
    selected = st.multiselect(
        "Select your squad (must meet position rules)",
        [f"{c['name']} {c['year']}" for c in cards]
    )
    if st.button("Save Squad"):
        squad = [c for c in cards if f"{c['name']} {c['year']}" in selected]
        with open("squad.json", "w") as f:
            json.dump(squad, f)
        st.success("Squad saved!")

with tab3:
    st.header("Play Match")
    if squad:
        score = 60
        for p in squad:
            if "Forward" in p['position']:
                score += p['goals'] * 5
            if "Mid" in p['position']:
                score += p['clearances'] * 2
            if "Defender" in p['position']:
                score -= p['rebound50s']
        score += random.randint(-10, 10)
        st.write(f"Your score: {int(score)}")
    else:
        st.warning("Build and save a squad first!")

with tab4:
    st.header("Open Pack")
    legends = [
        {"name": "Buddy Franklin", "year": 2008, "position": "Tall Forward"},
        {"name": "Gary Ablett Jr.", "year": 2014, "position": "Inside Mid"},
        {"name": "Dustin Martin", "year": 2017, "position": "Inside Mid"}
    ]
    if st.button("Open Legends Pack"):
        unlocked = random.sample(legends, 1)
        cards.extend(unlocked)
        with open("cards.json", "w") as f:
            json.dump(cards, f)
        st.success(f"You got: {unlocked[0]['name']} {unlocked[0]['year']}")
