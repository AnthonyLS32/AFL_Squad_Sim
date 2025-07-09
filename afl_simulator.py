import streamlit as st
import json
import random

# --- Player Pool ---

# Sample players with photo URLs (make sure to replace this with your full player JSON list)
player_pool = [
    {"name": "Lance Franklin", "position": "Forward", "goals": 2.8, "disposals": 15.2, "tackles": 1.9, "inside50": 3.5, "rebound50": 0.2, "onepercenters": 0.5, "hitouts": 0, "ovr": 90, "photo_url": "https://content.api-sports.io/football/players/330/330.png"},
    {"name": "Tom Lynch", "position": "Forward", "goals": 2.3, "disposals": 13.1, "tackles": 1.6, "inside50": 2.9, "rebound50": 0.1, "onepercenters": 0.7, "hitouts": 0, "ovr": 85, "photo_url": "https://content.api-sports.io/football/players/331/331.png"},
    {"name": "Charlie Cameron", "position": "Forward", "goals": 2.1, "disposals": 12.8, "tackles": 3.4, "inside50": 3.7, "rebound50": 0.0, "onepercenters": 0.4, "hitouts": 0, "ovr": 83, "photo_url": "https://content.api-sports.io/football/players/332/332.png"},
    # Add your full 50+ players here...
]

# --- Initialize Session State ---
if "squad" not in st.session_state:
    # Build starting squad:
    # Buddy Franklin always included
    buddy = next((p for p in player_pool if p["name"] == "Lance Franklin"), None)
    
    # Pick 6 players for each position + Buddy if not already in list
    def pick_for_pos(pos, count):
        pos_players = [p for p in player_pool if p["position"] == pos and p != buddy]
        return random.sample(pos_players, count)

    forwards = pick_for_pos("Forward", 5)
    if buddy and buddy not in forwards:
        forwards.append(buddy)

    midfielders = pick_for_pos("Midfield", 6)
    defenders = pick_for_pos("Defender", 6)
    rucks = pick_for_pos("Ruck", 2)

    st.session_state.squad = forwards + midfielders + defenders + rucks
    st.session_state.selected_team = []
    st.session_state.locked_slots = {}
    st.session_state.xp = 0
    st.session_state.coins = 500
    st.session_state.match_log = []

# --- Helper: Player stats line ---
def stats(p):
    return (f"{p['name']} | {p['position']} | OVR:{p['ovr']} | "
            f"G:{p['goals']} D:{p['disposals']} T:{p['tackles']} "
            f"I50:{p['inside50']} R50:{p['rebound50']} 1%:{p['onepercenters']} HO:{p['hitouts']}")

# --- Sidebar Menu ---
tab = st.sidebar.radio("Menu", ["Squad","Selected Team","Play Match","Training","Trade/Delist","Store"])

# --- SQUAD TAB ---
if tab == "Squad":
    st.header("Your Squad")
    st.write(f"XP: {st.session_state.xp} | Coins: {st.session_state.coins}")
    for p in st.session_state.squad:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; margin-bottom:10px;">
                <img src="{p['photo_url']}" alt="{p['name']}" style="width:50px; height:50px; border-radius:5px; object-fit:cover; margin-right:10px;">
                <div>{stats(p)}</div>
            </div>
            """, unsafe_allow_html=True)

# --- SELECTED TEAM TAB ---
elif tab == "Selected Team":
    st.header("Select Your Team")

    position_limits = {"Forward": 6, "Midfield": 6, "Defender": 6, "Ruck": 2}

    # Reset all locks function
    def reset_all_locks():
        st.session_state.locked_slots = {}

    locked_player_names = set(st.session_state.locked_slots.values())
    new_selection = []

    for pos, max_count in position_limits.items():
        st.subheader(f"{pos}s ({max_count})")
        for idx in range(max_count):
            locked_name = st.session_state.locked_slots.get((pos, idx), None)
            col1, col2, col3 = st.columns([1, 6, 1])

            with col1:
                if locked_name:
                    img_url = next((p['photo_url'] for p in st.session_state.squad if p['name'] == locked_name), '')
                    st.markdown(
                        f"""
                        <div style="border: 3px solid #4CAF50; border-radius: 5px; width: 60px; height: 60px; overflow: hidden;">
                            <img src="{img_url}" alt="{locked_name}" style="width: 60px; height: 60px; object-fit: cover;" />
                        </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(
                        f"""
                        <div style="border: 2px solid #ccc; border-radius: 5px; width: 60px; height: 60px;"></div>
                        """, unsafe_allow_html=True)

            with col2:
                if locked_name:
                    st.text_input(f"{pos} #{idx+1}", value=locked_name, key=f"{pos}_locked_{idx}", disabled=True)
                else:
                    available_players = [p['name'] for p in st.session_state.squad if p['position'] == pos and p['name'] not in locked_player_names]
                    available_players = ["-- Select --"] + available_players
                    sel = st.selectbox(f"{pos} #{idx+1}", options=available_players, key=f"{pos}_select_{idx}")
                    if sel != "-- Select --":
                        new_selection.append(sel)
                    else:
                        new_selection.append(None)

            with col3:
                if locked_name:
                    if st.button(f"Unlock", key=f"unlock_{pos}_{idx}"):
                        del st.session_state.locked_slots[(pos, idx)]
                        st.experimental_rerun()
                else:
                    sel_name = st.session_state.get(f"{pos}_select_{idx}", None)
                    if sel_name and sel_name != "-- Select --":
                        if st.button("Lock", key=f"lock_{pos}_{idx}"):
                            st.session_state.locked_slots[(pos, idx)] = sel_name
                            st.experimental_rerun()

    st.markdown("---")
    if st.button("Reset All Locks"):
        reset_all_locks()
        st.experimental_rerun()

    if st.button("Save Selected Team"):
        selected_team = []
        counts = {pos: 0 for pos in position_limits}

        for (pos, idx), player_name in st.session_state.locked_slots.items():
            player = next((p for p in st.session_state.squad if p['name'] == player_name), None)
            if player:
                selected_team.append(player)
                counts[pos] += 1

        if counts == position_limits:
            st.session_state.selected_team = selected_team
            st.success("Team saved successfully!")
        else:
            st.error(f"Team incomplete or invalid! Position counts: {counts}")

    # Preview saved team
    st.markdown("## Current Selected Team Preview")
    if st.session_state.selected_team:
        for pos in position_limits:
            st.markdown(f"### {pos}s")
            players_for_pos = [p for p in st.session_state.selected_team if p['position'] == pos]
            for p in players_for_pos:
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <img src="{p['photo_url']}" alt="{p['name']}" style="width:50px; height:50px; border-radius: 5px; object-fit: cover; margin-right: 10px;">
                        <div>
                            <strong>{p['name']}</strong><br>
                            OVR: {p['ovr']} | Goals: {p['goals']} | Disposals: {p['disposals']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.write("No team saved yet.")

# --- PLAY MATCH TAB ---
elif tab == "Play Match":
    st.header("Play a Match")
    if not st.session_state.selected_team or len(st.session_state.selected_team) < 20:
        st.warning("Select & save a full 20-player team first.")
    else:
        if st.button("Kick Off vs AI Club"):
            opponent = random.choice(["Melbourne","Hawthorn","Fremantle","Richmond","Geelong"])
            result = random.choices(["Win","Draw","Loss"], weights=[0.5,0.2,0.3])[0]
            xp_gain = 50 if result=="Win" else 25 if result=="Draw" else 10
            coin_gain = 100 if result=="Win" else 50 if result=="Draw" else 0
            st.session_state.xp += xp_gain
            st.session_state.coins += coin_gain

            st.subheader(f"{result} vs {opponent}!")
            st.write(f"You earned {xp_gain} XP & {coin_gain} coins.")

            # simple box score - top 3 disposals
            box = []
            for player in random.sample(st.session_state.selected_team, 3):
                box.append(f"{player['name']}: {random.randint(10,30)} disposals")
            st.write("**Top Disposal Getters:**")
            for line in box:
                st.write(line)

            st.write("**Goal Kickers:**")
            for player in random.sample(st.session_state.selected_team, 3):
                st.write(f"{player['name']}: {random.randint(1,4)} goals")

            # log match
            st.session_state.match_log.append({
                "opponent": opponent, "result": result,
                "xp": xp_gain, "coins": coin_gain
            })

    if st.session_state.match_log:
        st.subheader("Match History")
        for m in st.session_state.match_log[-5:]:
            st.write(f"{m['result']} vs {m['opponent']} (+{m['xp']} XP, +{m['coins']}¢)")

# --- TRAINING TAB ---
elif tab == "Training":
    st.header("Training Center")
    st.write(f"XP Available: {st.session_state.xp}")
    player = st.selectbox("Choose Player", [p['name'] for p in st.session_state.squad], key="trn_pl")
    stat = st.selectbox("Stat to Boost", ["goals","disposals","tackles","inside50","rebound50","onepercenters","hitouts"], key="trn_st")
    cost = 20
    if st.button(f"Train +0.5 {stat} for {cost} XP"):
        if st.session_state.xp >= cost:
            for p in st.session_state.squad:
                if p['name'] == player:
                    p[stat] += 0.5
                    p['ovr'] = round((p['ovr'] + p[stat] * 0.1), 1)
                    st.session_state.xp -= cost
                    st.success(f"{player}'s {stat} improved!")
                    break
        else:
            st.error("Not enough XP!")

# --- TRADE/DELIST TAB ---
elif tab == "Trade/Delist":
    st.header("Trade / Delist")
    to_remove = st.selectbox("Select Player to Remove", [p['name'] for p in st.session_state.squad], key="del_pl")
    if st.button("Delist Player"):
        st.session_state.squad = [p for p in st.session_state.squad if p['name'] != to_remove]
        # Remove from selected team & locked slots if exists
        st.session_state.selected_team = [p for p in st.session_state.selected_team if p['name'] != to_remove]
        locked_to_remove = [k for k,v in st.session_state.locked_slots.items() if v == to_remove]
        for k in locked_to_remove:
            del st.session_state.locked_slots[k]
        st.success(f"{to_remove} has been delisted.")

# --- STORE TAB ---
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
            for pl in pack:
                if pl not in st.session_state.squad:
                    st.session_state.squad.append(pl)
                    new += 1
            st.write("**Pack Contents:**")
            for pl in pack:
                st.markdown(
                    f"""
                    <div style="display:flex; align-items:center; margin-bottom:10px;">
                        <img src="{pl['photo_url']}" alt="{pl['name']}" style="width:50px; height:50px; border-radius:5px; object-fit:cover; margin-right:10px;">
                        <div>{stats(pl)}</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.success(f"Added {new} new players.")
        else:
            st.error("Not enough coins!")
