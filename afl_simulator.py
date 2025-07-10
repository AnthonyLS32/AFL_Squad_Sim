import streamlit as st
import json
import random

# --- Helper function for XP to OVR progression --------------------------------
def apply_xp_progression(player):
    """
    XP to OVR progression:
    - Every 20 XP = +1 OVR
    - Max +5 OVR boost above base OVR
    """
    if 'base_ovr' not in player:
        player['base_ovr'] = player['ovr']

    levels = player.get('xp', 0) // 20
    player['ovr'] = min(player['base_ovr'] + levels, player['base_ovr'] + 5)

    if player['ovr'] >= player['base_ovr'] + 5:
        player['xp'] = 100

# --- Load players data --------------------------------------------------------
with open('players.json') as f:
    player_pool = json.load(f)

# --- Ensure each player has XP field ------------------------------------------
for p in player_pool:
    if 'xp' not in p:
        p['xp'] = 0

# --- Initialize session state --------------------------------------------------
if 'squad' not in st.session_state:
    # Start with a fixed starter squad to ensure minimum position counts
    # 5 Forward, 5 Midfield, 3 Ruck, 5 Defender
    def pick_for_pos(pos, count):
        candidates = [p for p in player_pool if p['position'] == pos]
        return random.sample(candidates, count)

    # Pick fixed squad + always include Buddy Franklin (Lance Franklin) if in pool
    buddy = next((p for p in player_pool if p['name'] == 'Lance Franklin'), None)
    squad = []
    if buddy:
        squad.append(buddy)
    # Add rest ensuring position requirements with extra options
    squad += pick_for_pos('Forward', 4)
    squad += pick_for_pos('Midfield', 5)
    squad += pick_for_pos('Ruck', 3)
    squad += pick_for_pos('Defender', 5)
    # Remove duplicates if buddy already included
    squad = list({p['name']: p for p in squad}.values())

    # Initialize xp, coins, logs, selected team
    st.session_state.update(
        squad=squad,
        selected_team=[],
        xp=0,
        coins=500,
        match_log=[]
    )

# --- Sidebar navigation -------------------------------------------------------
tab = st.sidebar.radio("Menu", ["Squad", "Selected Team", "Play Match", "Training", "Trade/Delist", "Store"])

# --- Helper: full player stats line with image and border --------------------
def stats(p):
    return (
        f"### {p['name']} ({p['position']})  \n"
        f"OVR: {p['ovr']} | Goals: {p['goals']} | Disposals: {p['disposals']} | Tackles: {p['tackles']}  \n"
        f"Inside50: {p['inside50']} | Rebound50: {p['rebound50']} | 1%ers: {p['onepercenters']} | Hitouts: {p['hitouts']}  \n"
        f"XP: {p.get('xp',0)} / 100  \n"
        f"<img src='{p.get('photo_url','https://via.placeholder.com/80')}' width='80' style='border:2px solid #000; border-radius:5px;'>"
    )

# --- SQUAD TAB ---------------------------------------------------------------
if tab == "Squad":
    st.header("Your Squad")
    st.write(f"XP: {st.session_state.xp} | Coins: {st.session_state.coins}")
    for p in st.session_state.squad:
        st.markdown(stats(p), unsafe_allow_html=True)
        st.write("---")

# --- SELECTED TEAM TAB ------------------------------------------------------
elif tab == "Selected Team":
    st.header("Select & Save Your Team (22 Players)")

    positions = {
        "Forward": 5,
        "Midfield": 5,
        "Ruck": 3,
        "Defender": 5,
    }

    # Track selected players and locking per position
    if 'locked_positions' not in st.session_state:
        st.session_state.locked_positions = {}

    selected = st.session_state.selected_team if st.session_state.selected_team else []

    # Autopick function - picks highest OVR per position count
    def autopick():
        team = []
        for pos, count in positions.items():
            pos_players = sorted([p for p in st.session_state.squad if p['position'] == pos], key=lambda x: x['ovr'], reverse=True)
            team.extend([p['name'] for p in pos_players[:count]])
        st.session_state.selected_team = team
        st.session_state.locked_positions = {name: True for name in team}

    st.button("Auto-Pick Best Team", on_click=autopick)

    # Show selection rows per position
    new_selection = []
    for pos, count in positions.items():
        st.subheader(f"{pos}s ({count})")
        pos_players = [p for p in st.session_state.squad if p['position'] == pos]

        # Show available players for this position not already locked in another position
        selected_names = [pname for pname in selected if pname in [pp['name'] for pp in pos_players]]
        available = [p['name'] for p in pos_players]

        for i in range(count):
            default_idx = 0
            if len(selected) > 0 and len(selected) > sum(len(new_selection) for _ in []):
                if len(selected) > len(new_selection):
                    try:
                        default_idx = available.index(selected[len(new_selection)])
                    except:
                        default_idx = 0
            select_key = f"{pos}_{i}"
            chosen = st.selectbox(f"{pos} #{i+1}", available, index=default_idx, key=select_key)
            new_selection.append(chosen)

    if st.button("Save Selected Team"):
        # Validate team size
        if len(new_selection) != sum(positions.values()):
            st.error(f"Team must have exactly {sum(positions.values())} players.")
        else:
            st.session_state.selected_team = new_selection.copy()
            st.success("Selected team saved!")

    # Display current saved team
    if st.session_state.selected_team:
        st.write("### Current Saved Team:")
        for name in st.session_state.selected_team:
            st.write(f"- {name}")

# --- PLAY MATCH TAB --------------------------------------------------------
elif tab == "Play Match":
    st.title("Play a Match")

    if not st.session_state.selected_team or len(st.session_state.selected_team) < 12:
        st.warning("Select & save at least 12 players first.")
    else:
        if st.button("Kick Off vs AI Club"):
            opponent = random.choice(["Melbourne", "Hawthorn", "Fremantle", "Richmond", "Geelong"])

            # Calculate Team OVR
            team_players = [
                p for p in st.session_state.squad if p['name'] in st.session_state.selected_team
            ]
            team_ovr = sum(p['ovr'] for p in team_players) / len(team_players)
            ai_ovr = random.randint(75, 90)

            # Determine match result based on team vs AI OVR
            if team_ovr > ai_ovr + 5:
                result = "Win"
            elif team_ovr < ai_ovr - 5:
                result = "Loss"
            else:
                result = random.choices(["Win", "Draw", "Loss"], weights=[0.4, 0.2, 0.4])[0]

            xp_gain = 50 if result == "Win" else 25 if result == "Draw" else 10
            coin_gain = 100 if result == "Win" else 50 if result == "Draw" else 0

            st.session_state.xp += xp_gain
            st.session_state.coins += coin_gain

            st.subheader(f"{result} vs {opponent}")
            st.write(f"You earned {xp_gain} XP & {coin_gain} coins.")

            # Add XP to each player & apply progression
            for p in team_players:
                p['xp'] = min(p.get('xp', 0) + random.randint(5, 10), 100)
                apply_xp_progression(p)

            # Simple match stats output
            st.write("**Top Disposal Getters:**")
            for p in random.sample(team_players, min(3, len(team_players))):
                st.write(f"{p['name']}: {random.randint(15, 35)} disposals")

            st.write("**Goal Kickers:**")
            for p in random.sample(team_players, min(3, len(team_players))):
                st.write(f"{p['name']}: {random.randint(1, 4)} goals")

            # Log the match
            st.session_state.match_log.append({
                "opponent": opponent,
                "result": result,
                "xp": xp_gain,
                "coins": coin_gain,
                "team_ovr": team_ovr,
                "ai_ovr": ai_ovr
            })

    # Show last 5 matches
    if st.session_state.match_log:
        st.subheader("Match History")
        for m in st.session_state.match_log[-5:]:
            st.write(f"{m['result']} vs {m['opponent']} | Team OVR: {round(m['team_ovr'],1)} | AI OVR: {m['ai_ovr']} (+{m['xp']} XP, +{m['coins']} coins)")

# --- TRAINING TAB -----------------------------------------------------------
elif tab == "Training":
    st.title("Training Center")
    st.write(f"XP Available: {st.session_state.xp}")

    squad_names = [p['name'] for p in st.session_state.squad]
    selected_players = st.multiselect("Choose up to 5 Players to Train", squad_names, max_selections=5, key="train_players")

    stat_options = ["goals", "disposals", "tackles", "inside50", "rebound50", "onepercenters", "hitouts"]
    selected_stats = st.multiselect("Select Stats to Boost for Selected Players", stat_options, key="train_stats")

    cost_per_stat = 10
    total_cost = len(selected_players) * len(selected_stats) * cost_per_stat

    if total_cost > 0:
        st.write(f"Total Training Cost: {total_cost} XP")
    else:
        st.write("Select players and stats to see training cost.")

    if st.button(f"Train Selected Players"):
        if total_cost == 0:
            st.warning("Please select at least one player and one stat to train.")
        elif st.session_state.xp < total_cost:
            st.error("Not enough XP to train those players/stats.")
        else:
            for p in st.session_state.squad:
                if p['name'] in selected_players:
                    for stat in selected_stats:
                        p[stat] += 0.2  # nerfed progression
                    p['xp'] = min(p.get('xp', 0) + 5, 100)
                    apply_xp_progression(p)

            st.session_state.xp -= total_cost
            st.success(f"Trained {len(selected_players)} players on {len(selected_stats)} stats for {total_cost} XP.")

    st.subheader("Player XP Levels")
    for p in st.session_state.squad:
        xp_pct = int((p.get('xp', 0) / 100) * 100)
        st.write(f"{p['name']} - OVR: {p['ovr']} - XP: {xp_pct}%")
        st.progress(xp_pct)

# --- TRADE/DELIST TAB -------------------------------------------------------
elif tab == "Trade/Delist":
    st.header("Trade / Delist Player")
    to_remove = st.selectbox("Select Player to Remove", [p['name'] for p in st.session_state.squad], key="del_pl")
    if st.button("Delist Player"):
        st.session_state.squad = [p for p in st.session_state.squad if p['name'] != to_remove]
        # Also remove from selected team if present
        if to_remove in st.session_state.selected_team:
            st.session_state.selected_team.remove(to_remove)
        st.success(f"{to_remove} has been delisted.")

# --- STORE TAB --------------------------------------------------------------
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
                st.markdown(stats(pl), unsafe_allow_html=True)
                st.write("---")
            st.success(f"Added {new} new players.")
        else:
            st.error("Not enough coins!")
