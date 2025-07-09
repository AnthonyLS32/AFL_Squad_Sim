import streamlit as st
import json
import random

# --- Load player pool ----------------------------------------------------------------
with open('players.json') as f:
    player_pool = json.load(f)

# --- Initialize session state -------------------------------------------------------
if 'squad' not in st.session_state:
    # Start with exactly 22: 4 FWD, 4 MID, 2 RUCK, 4 DEF, 3 Bench
    def pick(pos, n):
        lst = [p for p in player_pool if p['position']==pos]
        return random.sample(lst, min(n,len(lst)))
    squad = pick('Forward',4) + pick('Midfield',4) + pick('Ruck',2) + pick('Defender',4) + pick(None,3)
    st.session_state.update(squad=squad, selected_team=[], xp=0, coins=500, match_log=[])

# --- Sidebar navigation -------------------------------------------------------------
tab = st.sidebar.radio("Menu", ["Squad","Selected Team","Play Match","Training","Trade/Delist","Store"])

# --- Helper: full stats line --------------------------------------------------------
def stats(p):
    return (f"{p['name']} | {p['position']} | OVR:{p['ovr']} | "
        f"G:{p['goals']} D:{p['disposals']} T:{p['tackles']} "
        f"I50:{p['inside50']} R50:{p['rebound50']} 1%:{p['onepercenters']} HO:{p['hitouts']}")

# --- SQUAD TAB ----------------------------------------------------------------------
if tab=="Squad":
    st.header("Your Squad")
    st.write(f"XP: {st.session_state.xp} | Coins: {st.session_state.coins}")
    for p in st.session_state.squad:
        st.write(stats(p))

# --- SELECTED TEAM TAB --------------------------------------------------------------
elif tab=="Selected Team":
    st.header("Select & Save Your Team (22 slots)")

    # define slots
    slots = [("Forward",4),("Midfield",4),("Ruck",2),("Defender",4),("Bench",3)]
    selections = []

    for pos,count in slots:
        st.subheader(f"{pos}s ({count})")
        if pos!="Bench":
            pool = [p for p in st.session_state.squad if p['position']==pos]
        else:
            pool = st.session_state.squad
        names = [p['name'] for p in pool]
        for i in range(count):
            sel = st.selectbox(f"{pos} #{i+1}", names, key=f"{pos}_{i}")
            selections.append(sel)

    if st.button("Save Selected Team"):
        st.session_state.selected_team = selections.copy()
        st.success("Selected team saved!")

    if st.session_state.selected_team:
        st.write("**Current Saved Team:**")
        for nm in st.session_state.selected_team:
            st.write(nm)

# --- PLAY MATCH TAB -----------------------------------------------------------------
elif tab=="Play Match":
    st.header("Play a Match")
    if not st.session_state.selected_team or len(st.session_state.selected_team)<13:
        st.warning("Select & save at least 13 players in Selected Team first.")
    else:
        if st.button("Kick Off vs AI Club"):
            opponent = random.choice(["Melbourne","Hawthorn","Fremantle","Richmond","Geelong"])
            result = random.choices(["Win","Draw","Loss"],weights=[0.5,0.2,0.3])[0]
            xp_gain = 50 if result=="Win" else 25 if result=="Draw" else 10
            coin_gain = 100 if result=="Win" else 50 if result=="Draw" else 0
            st.session_state.xp += xp_gain
            st.session_state.coins += coin_gain

            st.subheader(f"{result} vs {opponent}!")
            st.write(f"You earned {xp_gain} XP & {coin_gain} coins.")

            # simple box score
            box = []
            for name in random.sample(st.session_state.selected_team,3):
                box.append(f"{name}: {random.randint(10,30)} disposals")
            st.write("**Top Disposal Getters:**")
            for line in box: st.write(line)

            st.write("**Goal Kickers:**")
            for name in random.sample(st.session_state.selected_team,3):
                st.write(f"{name}: {random.randint(1,4)} goals")

            # log match
            st.session_state.match_log.append({
                "opponent": opponent, "result": result,
                "xp": xp_gain, "coins": coin_gain
            })

    if st.session_state.match_log:
        st.subheader("Match History")
        for m in st.session_state.match_log[-5:]:
            st.write(f"{m['result']} vs {m['opponent']} (+{m['xp']} XP, +{m['coins']}¢)")

# --- TRAINING TAB -------------------------------------------------------------------
elif tab=="Training":
    st.header("Training Center")
    st.write(f"XP Available: {st.session_state.xp}")
    player = st.selectbox("Choose Player", [p['name'] for p in st.session_state.squad], key="trn_pl")
    stat = st.selectbox("Stat to Boost", ["goals","disposals","tackles","inside50","rebound50","onepercenters","hitouts"], key="trn_st")
    cost = 20
    if st.button(f"Train +0.5 {stat} for {cost} XP"):
        if st.session_state.xp>=cost:
            for p in st.session_state.squad:
                if p['name']==player:
                    p[stat]+=0.5
                    p['ovr']=round((p['ovr']+p[stat]*0.1),1)
                    st.session_state.xp-=cost
                    st.success(f"{player}'s {stat} improved!")
                    break
        else:
            st.error("Not enough XP!")

# --- TRADE/DELIST TAB ---------------------------------------------------------------
elif tab=="Trade/Delist":
    st.header("Trade / Delist")
    to_remove = st.selectbox("Select Player to Remove", [p['name'] for p in st.session_state.squad], key="del_pl")
    if st.button("Delist Player"):
        st.session_state.squad = [p for p in st.session_state.squad if p['name']!=to_remove]
        st.success(f"{to_remove} has been delisted.")

# --- STORE TAB ----------------------------------------------------------------------
elif tab=="Store":
    st.header("Store")
    st.write(f"Coins: {st.session_state.coins}")
    price=200
    if st.button(f"Buy 5‐Player Pack for {price} Coins"):
        if st.session_state.coins>=price:
            st.session_state.coins-=price
            commons=[p for p in player_pool if p['ovr']<90]
            rares=[p for p in player_pool if p['ovr']>=90]
            pack = random.sample(commons,4)+random.sample(rares,1)
            # add new
            new=0
            for pl in pack:
                if pl not in st.session_state.squad:
                    st.session_state.squad.append(pl); new+=1
            st.write("**Pack Contents:**")
            for pl in pack: st.write(stats(pl))
            st.success(f"Added {new} new players.")
        else:
            st.error("Not enough coins!")
