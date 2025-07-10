import streamlit as st
import json
import random
import math
import plotly.graph_objects as go

# --- Load player pool ---
with open('players.json') as f:
    player_pool = json.load(f)

# --- Helper: pick players by position ---
def pick_for_pos(pos, n):
    pool = [p for p in player_pool if p["position"] == pos]
    return random.sample(pool, n)

# --- Initialize session ---
if 'squad' not in st.session_state:
    st.session_state.squad = [player for player in pick_for_pos("Forward", 5) + pick_for_pos("Midfield", 5) + pick_for_pos("Defender", 5) + pick_for_pos("Ruck", 3)]
    st.session_state.squad.append(next(p for p in player_pool if p["name"] == "Lance Franklin"))
    st.session_state.selected_team = []
    st.session_state.xp = 0
    st.session_state.coins = 500
    st.session_state.match_log = []
    st.session_state.ladder = []

# --- Sidebar ---
tab = st.sidebar.radio("Menu", ["Squad", "Selected Team", "Play Match", "Training", "Season"])

# --- Helper: player stats ---
def stats(p):
    return f"{p['name']} | {p['position']} | OVR: {p['ovr']} | XP: {p['xp']}"

# --- Helper: radar chart ---
def radar_chart(p):
    fig = go.Figure()
    categories = ['disposals', 'tackles', 'marks', 'clearances', 'goals']
    values = [p[c] for c in categories]
    fig.add_trace(go.Scatterpolar(
        r = values + [values[0]],
        theta = categories + [categories[0]],
        fill = 'toself'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, max(values)+5])), showlegend=False)
    st.plotly_chart(fig)

# --- SQUAD ---
if tab == "Squad":
    st.header("Your Squad")
    st.write(f"XP: {st.session_state.xp} | Coins: {st.session_state.coins}")
    for p in st.session_state.squad:
        st.write(stats(p))
        radar_chart(p)
        st.progress(min(100, int(p['xp'])), text=f"XP: {p['xp']}")

# --- SELECTED TEAM ---
elif tab == "Selected Team":
    st.header("Select Your Team (15 slots)")
    slots = [("Forward", 5), ("Midfield", 5), ("Defender", 3), ("Ruck", 2)]
    selections = []
    for pos, count in slots:
        st.subheader(f"{pos}s ({count})")
        pool = [p for p in st.session_state.squad if p['position'] == pos]
        names = [p['name'] for p in pool]
        for i in range(count):
            sel = st.selectbox(f"{pos} #{i+1}", names, key=f"{pos}_{i}")
            selections.append(sel)

    if st.button("Save Selected Team"):
        st.session_state.selected_team = selections.copy()
        st.success("Team saved!")

    if st.button("Auto Pick"):
        best = sorted(st.session_state.squad, key=lambda x: -x['ovr'])
        auto = []
        for pos, count in slots:
            picks = [p['name'] for p in best if p['position'] == pos][:count]
            auto.extend(picks)
        st.session_state.selected_team = auto
        st.success("Auto-picked best squad!")

    if st.session_state.selected_team:
        st.write("**Current Team:**")
        for nm in st.session_state.selected_team:
            st.write(nm)

# --- PLAY MATCH ---
elif tab == "Play Match":
    st.header("Play Match")
    if not st.session_state.selected_team or len(st.session_state.selected_team) < 15:
        st.warning("Pick and save at least 15 players.")
    else:
        opponent = random.choice(["Hawthorn", "Geelong", "Carlton", "Melbourne", "Fremantle"])
        st.write(f"Next Match: vs {opponent}")
        if st.button("Kick Off"):
            score = random.randint(50, 120)
            opp_score = random.randint(40, 110)
            if score > opp_score:
                result = "Win"
                xp = 50
                coins = 100
            elif score == opp_score:
                result = "Draw"
                xp = 25
                coins = 50
            else:
                result = "Loss"
                xp = 10
                coins = 0
            st.session_state.xp += xp
            st.session_state.coins += coins
            for p in st.session_state.squad:
                p['xp'] += random.randint(1, 5)
            st.success(f"{result}! {score} - {opp_score} | +{xp} XP +{coins} Coins")
            st.session_state.match_log.append({"opponent": opponent, "result": result})

        if st.session_state.match_log:
            st.subheader("Match Log")
            for m in st.session_state.match_log[-5:]:
                st.write(f"{m['result']} vs {m['opponent']}")

# --- TRAINING ---
elif tab == "Training":
    st.header("Training")
    st.write(f"XP: {st.session_state.xp}")
    picks = st.multiselect("Pick up to 5 players", [p['name'] for p in st.session_state.squad])
    stat = st.selectbox("Attribute", ["disposals", "tackles", "marks", "clearances", "goals"])
    if st.button("Train"):
        if st.session_state.xp >= 20 and len(picks) <= 5:
            for name in picks:
                for p in st.session_state.squad:
                    if p['name'] == name:
                        p[stat] += 0.5
                        p['xp'] += 2
            st.session_state.xp -= 20
            st.success("Training done!")
        else:
            st.error("Not enough XP or too many players!")

# --- SEASON MODE ---
elif tab == "Season":
    st.header("Season Mode")
    st.write("Draft, ladder, finals coming soon!")
