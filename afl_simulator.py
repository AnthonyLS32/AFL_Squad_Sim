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
