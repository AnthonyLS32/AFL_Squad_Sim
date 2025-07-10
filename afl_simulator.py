import streamlit as st
import json
import random

# ---------------- Load Player Pool ------------------
with open('players.json') as f:
    player_pool = json.load(f)

# -------------- Session State ----------------------
if 'squad' not in st.session_state:
    def pick_for_pos(pos, count):
        pos_players = [p for p in player_pool if p['position'] == pos and p['name'] != "Lance Franklin"]
        return random.sample(pos_players, count)

    squad = [p for p in player_pool if p['name'] == "Lance Franklin"]
    squad += pick_for_pos("Forward", 4)
    squad += pick_for_pos("Midfield", 5)
    squad += pick_for_pos("Defender", 5)
    squad += pick_for_pos("Ruck", 2)

    st.session_state.squad = squad
    st.session_state.selected_team = []
    st.session_state.xp = 0
    st.session_state.coins = 500
    st.session_state.match_log = []

# -------------------- Helper -----------------------
def stats(p):
    return (
        f"{p['name']} | {p['position']} | OVR:{p['ovr']} | "
        f"Goals:{p['goals']} Disposals:{p['disposals']} Marks:{p.get('marks',0)} Tackles:{p['tackles']} "
    )

# ---------------- Sidebar --------------------------
tab = st.sidebar.radio("Menu", ["Squad", "Selected Team", "Play Match", "Training", "Store"])

# ------------------ Squad --------------------------
if tab == "Squad":
    st.title("Your Squad")
    st.write(f"XP: {st.session_state.xp} | Coins: {st.session_state.coins}")
    for p in st.session_state.squad:
        st.image(p.get('photo_url', ''), width=100)
        st.write(stats(p))

# --------------- Selected Team ---------------------
elif tab == "Selected Team":
    st.title("Select Your Team")

    slots = [("Forward", 5), ("Midfield", 5), ("Ruck", 2), ("Defender", 5)]

    new_selection = []

    for pos, count in slots:
        st.subheader(f"{pos}s ({count})")
        pool = [p for p in st.session_state.squad if p['position'] == pos]
        names = [p['name'] for p in pool]

        for i in range(count):
            key = f"{pos}_{i}"
            sel = st.selectbox(f"{pos} #{i+1}", ["--"] + names, key=key)
            if sel != "--":
                new_selection.append(sel)

    if st.button("Save Selected Team"):
        st.session_state.selected_team = new_selection.copy()
        st.success("Team saved!")

    if st.button("Autopick Best Team"):
        auto_team = []
        for pos, count in slots:
            pool = [p for p in st.session_state.squad if p['position'] == pos]
            pool.sort(key=lambda x: x['ovr'], reverse=True)
            auto_team += [p['name'] for p in pool[:count]]
        st.session_state.selected_team = auto_team
        st.success("Autopick complete!")

    if st.session_state.selected_team:
        st.write("**Current Selected Team:**")
        for name in st.session_state.selected_team:
            st.write(name)

# ------------------ Play Match ---------------------
elif tab == "Play Match":
    st.title("Play Match")
    if not st.session_state.selected_team or len(st.session_state.selected_team) < 17:
        st.warning("Pick & save your team first!")
    else:
        if st.button("Play vs AI Club"):
            opponent = random.choice(["Hawks", "Cats", "Demons", "Swans"])
            result = random.choices(["Win", "Draw", "Loss"], weights=[0.5, 0.2, 0.3])[0]
            xp_gain = 50 if result == "Win" else 25 if result == "Draw" else 10
            coin_gain = 100 if result == "Win" else 50 if result == "Draw" else 0

            st.session_state.xp += xp_gain
            st.session_state.coins += coin_gain

            st.write(f"{result} vs {opponent}")
            st.write(f"Gained {xp_gain} XP, {coin_gain} coins")

            st.session_state.match_log.append({
                "opponent": opponent,
                "result": result,
                "xp": xp_gain,
                "coins": coin_gain
            })

    if st.session_state.match_log:
        st.subheader("Match Log")
        for m in st.session_state.match_log[-5:]:
            st.write(f"{m['result']} vs {m['opponent']} (+{m['xp']} XP, +{m['coins']}¢)")

# ---------------- Training -------------------------
elif tab == "Training":
    st.title("Training Center")
    st.write(f"XP: {st.session_state.xp}")

    player = st.selectbox("Choose Player", [p['name'] for p in st.session_state.squad])
    stat = st.selectbox("Attribute", ["goals", "disposals", "tackles"])
    cost = 20

    if st.button(f"Train +0.2 {stat} for {cost} XP"):
        if st.session_state.xp >= cost:
            for p in st.session_state.squad:
                if p['name'] == player:
                    p[stat] += 0.2
                    p['ovr'] = round(p['ovr'] + 0.2, 1)
                    st.session_state.xp -= cost
                    st.success(f"{player} improved {stat}!")
                    break
        else:
            st.error("Not enough XP!")

# ---------------- Store ----------------------------
elif tab == "Store":
    st.title("Store")
    st.write(f"Coins: {st.session_state.coins}")
    price = 200
    if st.button(f"Buy 5-Player Pack for {price} Coins"):
        if st.session_state.coins >= price:
            st.session_state.coins -= price
            commons = [p for p in player_pool if p['ovr'] < 80]
            rares = [p for p in player_pool if p['ovr'] >= 80]
            pack = random.sample(commons, 4) + random.sample(rares, 1)
            new = 0
            for pl in pack:
                if pl not in st.session_state.squad:
                    st.session_state.squad.append(pl)
                    new += 1
            st.write("**Pack Contents:**")
            for pl in pack:
                st.write(stats(pl))
            st.success(f"Added {new} new players!")
        else:
            st.error("Not enough coins!")
