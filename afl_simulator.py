import streamlit as st
import json
import random
import os

# --- Load player pool ----------------------------------------------------------------
with open('players.json') as f:
    player_pool = json.load(f)

# --- Load saved squad if exists ------------------------------------------------------
save_file = 'save_squad.json'
if os.path.exists(save_file):
    with open(save_file) as f:
        saved_squad = json.load(f)
else:
    saved_squad = None

# --- Initialize session state --------------------------------------------------------
if 'squad' not in st.session_state:
    def pick(pos, n):
        if pos:
            lst = [p for p in player_pool if p['position'] == pos]
        else:
            lst = player_pool
        return random.sample(lst, min(n, len(lst)))

    if saved_squad:
        squad = saved_squad
    else:
        # Build starting squad, enough for 22 slots
        squad = pick('Forward', 6) + pick('Midfield', 6) + pick('Ruck', 2) + pick('Defender', 6) + pick(None, 4)

    st.session_state.update(
        squad=squad,
        selected_team=[],
        xp=0,
        coins=500,
        match_log=[]
    )

# --- Sidebar navigation -------------------------------------------------------------
tab = st.sidebar.radio("Menu", ["Squad", "Selected Team", "Play Match", "Training", "Trade/Delist", "Store"])

# --- Helper: stats line with photo --------------------------------------------------
def stats(p):
    return (f"![{p['name']}]({p['photo_url']})  \n"
            f"**{p['name']}** | {p['position']} | **OVR:** {p['ovr']}  \n"
            f"G:{p['goals']} D:{p['disposals']} T:{p['tackles']} "
            f"I50:{p['inside50']} R50:{p['rebound50']} 1%:{p['onepercenters']} HO:{p['hitouts']}")

# --- SQUAD TAB ----------------------------------------------------------------------
if tab == "Squad":
    st.header("Your Squad")
    st.write(f"**XP:** {st.session_state.xp} | **Coins:** {st.session_state.coins}")
    for p in st.session_state.squad:
        st.markdown(stats(p))

# --- SELECTED TEAM TAB --------------------------------------------------------------
elif tab == "Selected Team":
    st.header("Select & Save Your Team (22 slots)")

    slots = [("Forward", 6), ("Midfield", 6), ("Ruck", 2), ("Defender", 6), ("Bench", 2)]
    selections = []
    available = st.session_state.squad.copy()

    for pos, count in slots:
        st.subheader(f"{pos}s ({count})")
        if pos != "Bench":
            pool = [p for p in available if p['position'] == pos]
        else:
            pool = available

        for i in range(count):
            names = [p['name'] for p in pool if p['name'] not in selections]
            if not names:
                st.warning(f"No more players available for {pos}.")
                continue
            sel = st.selectbox(f"{pos} #{i+1}", names, key=f"{pos}_{i}")
            selections.append(sel)

    if st.button("Save Selected Team"):
        if len(selections) == sum(count for _, count in slots):
            st.session_state.selected_team = selections.copy()
            st.success("Selected team saved!")
            with open(save_file, 'w') as f:
                json.dump(st.session_state.squad, f)
        else:
            st.error("You must select exactly 22 players!")

    if st.session_state.selected_team:
        st.write("**Current Saved Team:**")
        for nm in st.session_state.selected_team:
            st.write(nm)

# --- PLAY MATCH TAB -----------------------------------------------------------------
elif tab == "Play Match":
    st.header("Play a Match")
    if not st.session_state.selected_team or len(st.session_state.selected_team) < 13:
        st.warning("Select & save at least 13 players in Selected Team first.")
    else:
        if st.button("Kick Off vs AI Club"):
            opponent = random.choice(["Melbourne", "Hawthorn", "Fremantle", "Richmond", "Geelong"])
            result = random.choices(["Win", "Draw", "Loss"], weights=[0.5, 0.2, 0.3])[0]
            xp_gain = 50 if result == "Win" else 25 if result == "Draw" else 10
            coin_gain = 100 if result == "Win" else 50 if result == "Draw" else 0
            st.session_state.xp += xp_gain
            st.session_state.coins += coin_gain

            st.subheader(f"{result} vs {opponent}!")
            st.write(f"You earned {xp_gain} XP & {coin_gain} coins.")

            for name in random.sample(st.session_state.selected_team, 3):
                st.write(f"{name}: {random.randint(10, 30)} disposals")

            st.write("**Goal Kickers:**")
            for name in random.sample(st.session_state.selected_team, 3):
                st.write(f"{name}: {random.randint(1, 4)} goals")

            st.session_state.match_log.append({
                "opponent": opponent, "result": result,
                "xp": xp_gain, "coins": coin_gain
            })

    if st.session_state.match_log:
        st.subheader("Match History")
        for m in st.session_state.match_log[-5:]:
            st.write(f"{m['result']} vs {m['opponent']} (+{m['xp']} XP, +{m['coins']}¢)")

# --- TRAINING TAB -------------------------------------------------------------------
elif tab == "Training":
    st.header("Training Center")
    st.write(f"XP Available: {st.session_state.xp}")
    player = st.selectbox("Choose Player", [p['name'] for p in st.session_state.squad], key="trn_pl")
    stat = st.selectbox("Stat to Boost", ["goals", "disposals", "tackles", "inside50", "rebound50", "onepercenters", "hitouts"], key="trn_st")
    cost = 20

    if st.button(f"Train +0.5 {stat} for {cost} XP"):
        if st.session_state.xp >= cost:
            for p in st.session_state.squad:
                if p['name'] == player:
                    p[stat] += 0.5
                    p['ovr'] = round(p['ovr'] + 0.1, 1)
                    st.session_state.xp -= cost
                    st.success(f"{player}'s {stat} improved!")
                    break
        else:
            st.error("Not enough XP!")

# --- TRADE/DELIST TAB ---------------------------------------------------------------
elif tab == "Trade/Delist":
    st.header("Trade / Delist")
    to_remove = st.selectbox("Select Player to Remove", [p['name'] for p in st.session_state.squad], key="del_pl")
    if st.button("Delist Player"):
        st.session_state.squad = [p for p in st.session_state.squad if p['name'] != to_remove]
        st.success(f"{to_remove} has been delisted.")

# --- STORE TAB ----------------------------------------------------------------------
elif tab == "Store":
    st.header("Store")
    st.write(f"Coins: {st.session_state.coins}")
    price = 200
    if st.button(f"Buy 5‐Player Pack for {price} Coins"):
        if st.session_state.coins >= price:
            st.session_state.coins -= price
            commons = [p for p in player_pool if p['ovr'] < 90]
            rares = [p for p in player_pool if p['ovr'] >= 90]
            pack = random.sample(commons, 4) + random.sample(rares, 1)

            new = 0
            owned_names = [p['name'] for p in st.session_state.squad]
            for pl in pack:
                if pl['name'] not in owned_names:
                    st.session_state.squad.append(pl)
                    new += 1

            st.write("**Pack Contents:**")
            for pl in pack:
                st.markdown(stats(pl))

            st.success(f"Added {new} new players.")
        else:
            st.error("Not enough coins!")
