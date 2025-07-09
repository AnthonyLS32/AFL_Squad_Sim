import streamlit as st
import json
import random

# --- Load player pool ----------------------------------------------------------------
with open('players.json') as f:
    player_pool = json.load(f)

# --- Helper: pick players safely ----------------------------------------------------
def pick_for_pos(pos, count):
    # Exclude Buddy Franklin here to add separately
    pos_players = [p for p in player_pool if p["position"] == pos and p["name"] != "Lance Franklin"]
    actual_count = min(count, len(pos_players))
    return random.sample(pos_players, actual_count)

# --- Initialize session state -------------------------------------------------------
if 'squad' not in st.session_state:
    # Buddy Franklin fixed
    buddy = next(p for p in player_pool if p["name"] == "Lance Franklin")

    # For each position pick 4 random players + Buddy (for Forward)
    forwards = pick_for_pos("Forward", 4) + [buddy]
    midfielders = pick_for_pos("Midfield", 5)
    defenders = pick_for_pos("Defender", 5)
    rucks = pick_for_pos("Ruck", 2)

    squad = forwards + midfielders + defenders + rucks

    # Initialize other states
    st.session_state.update(
        squad=squad,
        selected_team=[None]*22,
        xp=0,
        coins=500,
        match_log=[],
        locked_slots=[False]*22
    )

# --- Sidebar navigation -------------------------------------------------------------
tab = st.sidebar.radio("Menu", ["Squad", "Selected Team", "Auto Pick Team", "Play Match", "Training", "Trade/Delist", "Store"])

# --- Helper: full stats line --------------------------------------------------------
def stats(p):
    return (f"{p['name']} | {p['position']} | OVR:{p['ovr']} | "
            f"G:{p['goals']} D:{p['disposals']} T:{p['tackles']} "
            f"I50:{p['inside50']} R50:{p['rebound50']} 1%:{p['onepercenters']} HO:{p['hitouts']}")

# --- Display player with photo and border -------------------------------------------
def display_player_card(p, selected=False):
    border_color = "green" if selected else "gray"
    st.markdown(f"""
        <div style="
            border: 2px solid {border_color};
            padding: 8px;
            border-radius: 8px;
            margin-bottom: 5px;
            display: flex;
            align-items: center;">
            <img src="{p.get('photo_url', '')}" alt="{p['name']}" width="60" height="60" style="border-radius: 50%; margin-right: 10px;">
            <div>
                <b>{p['name']}</b><br>
                <small>{p['position']} | OVR: {p['ovr']}</small><br>
                <small>G:{p['goals']} D:{p['disposals']} T:{p['tackles']}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- SQUAD TAB ----------------------------------------------------------------------
if tab == "Squad":
    st.header("Your Squad")
    st.write(f"XP: {st.session_state.xp} | Coins: {st.session_state.coins}")

    for p in st.session_state.squad:
        display_player_card(p)

# --- SELECTED TEAM TAB --------------------------------------------------------------
elif tab == "Selected Team":
    st.header("Select & Save Your Team (22 slots)")

    # Position slots and counts to fill 22 total
    slots = [
        ("Forward", 5),
        ("Midfield", 5),
        ("Ruck", 2),
        ("Defender", 5),
        ("Utility", 5)  # Utility can be any position from squad
    ]

    # Flatten squad names for quick lookup
    squad_names = [p['name'] for p in st.session_state.squad]

    # Load current selected team or init None list
    selected_team = st.session_state.selected_team
    locked_slots = st.session_state.locked_slots

    idx = 0
    new_selection = selected_team.copy()

    for pos, count in slots:
        st.subheader(f"{pos}s ({count})")

        # Build available pool for this slot:
        if pos != "Utility":
            pool = [p for p in st.session_state.squad if p["position"] == pos]
        else:
            pool = st.session_state.squad  # utility any position

        pool_names = [p['name'] for p in pool]

        for i in range(count):
            slot_label = f"{pos} #{i+1}"

            # Disable selectbox if locked
            if locked_slots[idx]:
                st.write(f"**{slot_label}:** {selected_team[idx]} (locked)")
            else:
                # Remove already selected players from choices except this slot's current selection
                taken = set(new_selection)
                if selected_team[idx] is not None:
                    taken.discard(selected_team[idx])

                available_names = [n for n in pool_names if n not in taken]

                # Add current selection if not None and not in available (to allow reselect)
                if selected_team[idx] and selected_team[idx] not in available_names:
                    available_names.append(selected_team[idx])
                available_names.sort()

                choice = st.selectbox(slot_label, options=available_names, index=available_names.index(selected_team[idx]) if selected_team[idx] else 0, key=f"sel_{idx}")

                new_selection[idx] = choice

            idx += 1

    # Buttons to lock/unlock
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Lock Selected Slots"):
            for i in range(len(locked_slots)):
                locked_slots[i] = True
            st.success("All slots locked")
    with col2:
        if st.button("Unlock All Slots"):
            for i in range(len(locked_slots)):
                locked_slots[i] = False
            st.success("All slots unlocked")

    if st.button("Save Selected Team"):
        # Check for None values
        if None in new_selection or "" in new_selection:
            st.error("All slots must be selected before saving.")
        else:
            st.session_state.selected_team = new_selection
            st.session_state.locked_slots = locked_slots
            st.success("Selected team saved!")

    # Show current saved team
    st.write("### Current Saved Team")
    for nm in st.session_state.selected_team:
        if nm:
            p = next((pl for pl in st.session_state.squad if pl['name'] == nm), None)
            if p:
                display_player_card(p, selected=True)

# --- AUTO PICK TEAM TAB -------------------------------------------------------------
elif tab == "Auto Pick Team":
    st.header("Auto Pick Best Overall Team")

    if st.button("Auto Pick & Save"):
        # Positions and counts as above
        slots = [
            ("Forward", 5),
            ("Midfield", 5),
            ("Ruck", 2),
            ("Defender", 5),
            ("Utility", 5)
        ]

        new_team = []
        used_names = set()

        # Pick best players per position by OVR descending
        for pos, count in slots:
            if pos != "Utility":
                candidates = sorted([p for p in st.session_state.squad if p["position"] == pos], key=lambda x: x["ovr"], reverse=True)
            else:
                # Utilities pick best remaining regardless of position
                candidates = sorted([p for p in st.session_state.squad if p["name"] not in used_names], key=lambda x: x["ovr"], reverse=True)

            picked = []
            for p in candidates:
                if p["name"] not in used_names and len(picked) < count:
                    picked.append(p["name"])
                    used_names.add(p["name"])

            new_team.extend(picked)

        # Save team
        st.session_state.selected_team = new_team
        st.session_state.locked_slots = [False]*22
        st.success("Auto picked team saved!")

    # Show current saved team
    st.write("### Current Saved Team")
    for nm in st.session_state.selected_team:
        if nm:
            p = next((pl for pl in st.session_state.squad if pl['name'] == nm), None)
            if p:
                display_player_card(p, selected=True)

# --- PLAY MATCH TAB -----------------------------------------------------------------
elif tab == "Play Match":
    st.header("Play a Match")

    if not st.session_state.selected_team or None in st.session_state.selected_team:
        st.warning("Select & save your full 22 player team first.")
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

            # simple box score
            box = []
            top_players = random.sample(st.session_state.selected_team, 3)
            for name in top_players:
                box.append(f"{name}: {random.randint(10,30)} disposals")
            st.write("**Top Disposal Getters:**")
            for line in box:
                st.write(line)

            st.write("**Goal Kickers:**")
            goal_kickers = random.sample(st.session_state.selected_team, 3)
            for name in goal_kickers:
                st.write(f"{name}: {random.randint(1,4)} goals")

            # log match
            st.session_state.match_log.append({
                "opponent": opponent,
                "result": result,
                "xp": xp_gain,
                "coins": coin_gain
            })

    if st.session_state.match_log:
        st.subheader("Match History")
        for m in st.session_state.match_log[-5:]:
            st.write(f"{m['result']} vs {m['opponent']} (+{m['xp']} XP, +{m['coins']}¢)")

# --- TRAINING TAB -------------------------------------------------------------------
elif tab == "Training":
    st.header("Training Center")
    st.write(f"XP Available: {st.session_state.xp}")

    player_names = [p['name'] for p in st.session_state.squad]
    player = st.selectbox("Choose Player", player_names, key="trn_pl")
    stat = st.selectbox("Stat to Boost", ["goals", "disposals", "tackles", "inside50", "rebound50", "onepercenters", "hitouts"], key="trn_st")

    cost = 20
    if st.button(f"Train +0.5 {stat} for {cost} XP"):
        if st.session_state.xp >= cost:
            for p in st.session_state.squad:
                if p['name'] == player:
                    p[stat] += 0.5
                    p['ovr'] = round((p['ovr'] + 0.1), 1)  # modest increase on overall
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
        # Prevent removing Buddy Franklin
        if to_remove == "Lance Franklin":
            st.error("Buddy Franklin cannot be delisted!")
        else:
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
            commons = [p for p in player_pool if p['ovr'] < 90 and p not in st.session_state.squad]
            rares = [p for p in player_pool if p['ovr'] >= 90 and p not in st.session_state.squad]

            # Safeguard sample size
            pack = random.sample(commons, min(4, len(commons))) + random.sample(rares, min(1, len(rares)))

            new = 0
            for pl in pack:
                if pl not in st.session_state.squad:
                    st.session_state.squad.append(pl)
                    new += 1

            st.write("**Pack Contents:**")
            for pl in pack:
                display_player_card(pl)

            st.success(f"Added {new} new players.")
        else:
            st.error("Not enough coins!")
