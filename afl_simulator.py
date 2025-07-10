import streamlit as st
import json
import random
from collections import defaultdict

# --- Load player pool ----------------------------------------------------------------
@st.cache_data
def load_players():
    with open('players.json') as f:
        players = json.load(f)
    # Initialize XP and base_ovr if missing
    for p in players:
        p.setdefault('xp', 0)
        p.setdefault('base_ovr', p['ovr'])
    return players

player_pool = load_players()

# --- Teams setup ---------------------------------------------------------------------
TEAM_NAMES = [
    "Melbourne", "Hawthorn", "Fremantle", "Richmond", "Geelong",
    "Collingwood", "West Coast", "Brisbane", "Essendon", "Carlton"
]

# Create empty teams dict (team_name: list of players)
teams = {team: [] for team in TEAM_NAMES}

# --- Auto Draft Function --------------------------------------------------------------
def auto_draft(player_pool, teams, team_size=22):
    """
    Automatically drafts players to teams based on overall rating and position balance.
    """
    sorted_players = sorted(player_pool, key=lambda x: x['ovr'], reverse=True)
    
    pos_needs = {
        "Forward": 6,
        "Midfield": 8,
        "Defender": 6,
        "Ruck": 2
    }
    team_pos_counts = {team: defaultdict(int) for team in teams}
    available_players = sorted_players.copy()
    
    # Round-robin draft until all teams full or no players left
    while available_players and any(len(plyrs) < team_size for plyrs in teams.values()):
        for team in teams:
            if len(teams[team]) >= team_size:
                continue
            needed_positions = [pos for pos, count in pos_needs.items() if team_pos_counts[team][pos] < count]
            candidates = [p for p in available_players if p['position'] in needed_positions]
            if not candidates:
                candidates = available_players
            if not candidates:
                break
            selected_player = candidates[0]
            teams[team].append(selected_player)
            team_pos_counts[team][selected_player['position']] += 1
            available_players.remove(selected_player)
    return teams

# --- Initialize session state -------------------------------------------------------
if 'career_started' not in st.session_state:
    # Run auto draft once at career start
    st.session_state.teams = auto_draft(player_pool, teams)
    # Default user's club = Melbourne for example
    st.session_state.user_team = "Melbourne"
    st.session_state.selected_team = []  # Player names from user's team
    st.session_state.xp = 0
    st.session_state.coins = 500
    st.session_state.match_log = []
    st.session_state.career_started = True

# --- Helper: player stats display ----------------------------------------------------
def stats(p):
    return (f"{p['name']} | {p['position']} | OVR:{p['ovr']} | "
            f"G:{p['goals']} D:{p['disposals']} T:{p['tackles']} "
            f"I50:{p['inside50']} R50:{p['rebound50']} 1%:{p['onepercenters']} HO:{p['hitouts']}")

# --- Sidebar navigation -------------------------------------------------------------
tab = st.sidebar.radio("Menu", ["Career Mode", "Selected Team", "Play Match", "Training", "Trade/Delist", "Store"])

# --- CAREER MODE TAB --------------------------------------------------------------
if tab == "Career Mode":
    st.header("Career Mode: Team Rosters and Draft")
    st.write(f"Your Club: **{st.session_state.user_team}**")
    
    # Show user's team squad with images and stats
    st.subheader(f"{st.session_state.user_team} Squad ({len(st.session_state.teams[st.session_state.user_team])} players)")
    team_squad = st.session_state.teams[st.session_state.user_team]
    cols = st.columns(4)
    for idx, p in enumerate(team_squad):
        with cols[idx % 4]:
            st.image(p.get('photo_url', ''), width=120)
            st.write(stats(p))

    st.markdown("---")
    st.subheader("All Teams and Their Squads")
    for team_name, squad in st.session_state.teams.items():
        if team_name == st.session_state.user_team:
            continue  # skip user's team here, already displayed
        st.write(f"### {team_name} ({len(squad)} players)")
        names = ", ".join(p['name'] for p in squad)
        st.write(names)

# --- SELECTED TEAM TAB --------------------------------------------------------------
elif tab == "Selected Team":
    st.header("Select & Save Your Matchday Team (22 players)")

    user_squad = st.session_state.teams[st.session_state.user_team]
    user_names = [p['name'] for p in user_squad]

    # Slots per position
    slots = [("Forward", 6), ("Midfield", 8), ("Ruck", 2), ("Defender", 6)]
    
    # Track selected names and their position locks
    if 'selected_positions' not in st.session_state:
        st.session_state.selected_positions = {pos: [None]*count for pos, count in slots}
    
    # Build selected team selectors
    for pos, count in slots:
        st.subheader(f"{pos}s ({count})")
        available = [p['name'] for p in user_squad if p['position'] == pos]
        
        # Remove already selected players from available options for other slots
        selected_flat = [name for names in st.session_state.selected_positions.values() for name in names if name]
        
        for i in range(count):
            # Current selection
            current_sel = st.session_state.selected_positions[pos][i]
            # Options exclude those already selected except current selection
            options = [current_sel] if current_sel else []
            options += [n for n in available if n not in selected_flat or n == current_sel]
            sel = st.selectbox(f"{pos} #{i+1}", options, key=f"{pos}_{i}")
            st.session_state.selected_positions[pos][i] = sel

    # Flatten selections to list
    selections = [name for pos_list in st.session_state.selected_positions.values() for name in pos_list if name]

    if st.button("Save Selected Team"):
        if len(selections) == 22:
            st.session_state.selected_team = selections
            st.success("Selected team saved!")
        else:
            st.error(f"Please select all 22 players before saving. Currently selected: {len(selections)}")

    if st.session_state.selected_team:
        st.write("**Current Saved Team:**")
        for nm in st.session_state.selected_team:
            st.write(nm)

    if st.button("Auto Select Best Team"):
        # Auto select best 22 by position and overall rating
        selected = []
        for pos, count in slots:
            pos_players = sorted([p for p in user_squad if p['position'] == pos], key=lambda x: x['ovr'], reverse=True)
            selected.extend([p['name'] for p in pos_players[:count]])
        st.session_state.selected_team = selected
        
        # Update session_state.selected_positions accordingly
        idx = 0
        for pos, count in slots:
            st.session_state.selected_positions[pos] = selected[idx:idx+count]
            idx += count
        st.success("Auto-selected best team saved!")

# --- PLAY MATCH TAB -----------------------------------------------------------------
elif tab == "Play Match":
    st.header("Play a Match")

    if not st.session_state.selected_team or len(st.session_state.selected_team) < 22:
        st.warning("Select & save 22 players in Selected Team first.")
    else:
        if st.button("Kick Off vs AI Club"):
            opponent = random.choice([t for t in TEAM_NAMES if t != st.session_state.user_team])
            # Simple match result weighted by average team ovr
            user_team_players = [p for p in st.session_state.teams[st.session_state.user_team] if p['name'] in st.session_state.selected_team]
            opp_team_players = st.session_state.teams[opponent]

            user_avg_ovr = sum(p['ovr'] for p in user_team_players) / len(user_team_players)
            opp_avg_ovr = sum(p['ovr'] for p in opp_team_players) / len(opp_team_players)

            # Win probability influenced by avg ovr
            base_probs = [0.4, 0.2, 0.4]  # Win, Draw, Loss base weights
            diff = user_avg_ovr - opp_avg_ovr
            # Adjust weights by ovr difference
            if diff > 0:
                base_probs[0] += min(diff * 0.02, 0.3)  # increase win chance
                base_probs[2] -= min(diff * 0.02, 0.3)  # decrease loss chance
            else:
                base_probs[0] += max(diff * 0.02, -0.3)  # decrease win chance
                base_probs[2] -= max(diff * 0.02, -0.3)  # increase loss chance

            # Normalize probabilities
            total = sum(base_probs)
            weights = [p / total for p in base_probs]
            result = random.choices(["Win", "Draw", "Loss"], weights=weights)[0]

            xp_gain = 50 if result == "Win" else 25 if result == "Draw" else 10
            coin_gain = 100 if result == "Win" else 50 if result == "Draw" else 0
            st.session_state.xp += xp_gain
            st.session_state.coins += coin_gain

            st.subheader(f"{result} vs {opponent}!")
            st.write(f"You earned {xp_gain} XP & {coin_gain} coins.")

            # Simple box score for disposals
            box = []
            for name in random.sample(st.session_state.selected_team, 3):
                box.append(f"{name}: {random.randint(10, 30)} disposals")
            st.write("**Top Disposal Getters:**")
            for line in box:
                st.write(line)

            st.write("**Goal Kickers:**")
            for name in random.sample(st.session_state.selected_team, 3):
                st.write(f"{name}: {random.randint(1, 4)} goals")

            # Log match
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
    
    user_squad = st.session_state.teams[st.session_state.user_team]
    user_names = [p['name'] for p in user_squad]

    # Allow selecting up to 5 players to train
    selected_players = st.multiselect("Choose up to 5 Players to Train", user_names, max_selections=5, key="trn_players")
    if selected_players:
        # Select attribute to train
        stat = st.selectbox("Stat to Boost", ["goals", "disposals", "tackles", "inside50", "rebound50", "onepercenters", "hitouts"], key="trn_stat")
        cost_per_player = 10  # reduce XP cost per player since multiple
        total_cost = cost_per_player * len(selected_players)

        if st.button(f"Train +0.5 {stat} for {total_cost} XP"):
            if st.session_state.xp >= total_cost:
                for p in user_squad:
                    if p['name'] in selected_players:
                        p[stat] += 0.5
                        # Update OVR based on stat increase
                        p['ovr'] = round(p['base_ovr'] + (p[stat] * 0.1), 1)
                        p['xp'] += 5  # XP gained for the player
                st.session_state.xp -= total_cost
                st.success(f"Trained {len(selected_players)} players on {stat}!")
            else:
                st.error("Not enough XP!")

    # Show players XP bar (simplified)
    st.subheader("Player Experience (XP)")
    cols = st.columns(5)
    for idx, p in enumerate(user_squad):
        with cols[idx % 5]:
            st.write(p['name'])
            xp_pct = min(p['xp'] / 100, 1.0)  # cap at 100 XP for full bar
            st.progress(xp_pct)

# --- TRADE/DELIST TAB ---------------------------------------------------------------
elif tab == "Trade/Delist":
    st.header("Trade / Delist")
    user_squad = st.session_state.teams[st.session_state.user_team]
    to_remove = st.selectbox("Select Player to Remove", [p['name'] for p in user_squad], key="del_pl")
    if st.button("Delist Player"):
        st.session_state.teams[st.session_state.user_team] = [p for p in user_squad if p['name'] != to_remove]
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
            # add new players to user's team
            new = 0
            user_squad = st.session_state.teams[st.session_state.user_team]
            for pl in pack:
                if pl not in user_squad:
                    user_squad.append(pl)
                    new += 1
            st.session_state.teams[st.session_state.user_team] = user_squad
            st.write("**Pack Contents:**")
            for pl in pack:
                st.write(stats(pl))
            st.success(f"Added {new} new players to your team.")
        else:
            st.error("Not enough coins!")
