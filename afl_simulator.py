import streamlit as st
import json
import random

# Load players.json
with open('players.json') as f:
    player_pool = json.load(f)

# Initialize session state variables
if 'squad' not in st.session_state:
    st.session_state['squad'] = player_pool.copy()

if 'selected_team' not in st.session_state:
    defenders = [p for p in player_pool if p['position'] == "Defender"]
    midfields = [p for p in player_pool if p['position'] == "Midfield"]
    forwards = [p for p in player_pool if p['position'] == "Forward"]
    rucks = [p for p in player_pool if p['position'] == "Ruck"]
    bench = [p for p in player_pool if p['position'] == "Bench"]

    selected_team = []
    selected_team += random.sample(forwards, min(4, len(forwards)))
    selected_team += random.sample(midfields, min(4, len(midfields)))
    selected_team += random.sample(rucks, min(2, len(rucks)))
    selected_team += random.sample(defenders, min(4, len(defenders)))
    selected_team += random.sample(bench, min(3, len(bench)))

    st.session_state['selected_team'] = selected_team

if 'xp' not in st.session_state:
    st.session_state['xp'] = 0

if 'coins' not in st.session_state:
    st.session_state['coins'] = 500

if 'training_log' not in st.session_state:
    st.session_state['training_log'] = []

if 'game_results' not in st.session_state:
    st.session_state['game_results'] = []

# Tabs for navigation
tab = st.sidebar.selectbox(
    "Choose tab",
    ["Squad", "Selected Team", "Training", "Trade/Delist", "Store", "Play Game"]
)

def player_stats_str(p):
    return (
        f"{p['name']} | Pos: {p['position']} | OVR: {p['ovr']} | "
        f"G:{p.get('goals', 0)} D:{p.get('disposals', 0)} T:{p.get('tackles', 0)} "
        f"I50:{p.get('inside50', 0)} R50:{p.get('rebound50', 0)} 1%:{p.get('onepercenters', 0)} HO:{p.get('hitouts', 0)}"
    )

def recalc_overall(player):
    # Simple average of key stats as a placeholder
    stats = [
        player.get('goals',0),
        player.get('disposals',0),
        player.get('tackles',0),
        player.get('inside50',0),
        player.get('rebound50',0),
        player.get('onepercenters',0),
        player.get('hitouts',0)
    ]
    player['ovr'] = round(sum(stats)/len(stats))

if tab == "Squad":
    st.title("Full Squad")
    st.write(f"XP: {st.session_state['xp']} | Coins: {st.session_state['coins']}")
    for p in st.session_state['squad']:
        st.write(player_stats_str(p))

elif tab == "Selected Team":
    st.title("Selected Team")
    st.write(f"XP: {st.session_state['xp']} | Coins: {st.session_state['coins']}")

    position_limits = {"Forward": 4, "Midfield": 4, "Ruck": 2, "Defender": 4, "Bench": 3}
    pos_counts = {pos: 0 for pos in position_limits.keys()}

    for p in st.session_state['selected_team']:
        pos = p.get('position', 'Bench')
        if pos not in pos_counts:
            pos = 'Bench'
        pos_counts[pos] += 1

    st.write(f"Team Composition: Forwards {pos_counts['Forward']}/4, Midfield {pos_counts['Midfield']}/4, "
             f"Rucks {pos_counts['Ruck']}/2, Defenders {pos_counts['Defender']}/4, Bench {pos_counts['Bench']}/3")

    for pos in ["Defender", "Midfield", "Ruck", "Forward", "Bench"]:
        st.subheader(f"{pos}s:")
        players = [pl for pl in st.session_state['selected_team'] if pl.get('position', 'Bench') == pos]
        for p in players:
            st.write(player_stats_str(p))

    available_players = [p for p in st.session_state['squad'] if p not in st.session_state['selected_team']]
    available_names = [p['name'] for p in available_players]
    selected_name = st.selectbox("Add player to team:", available_names)

    if st.button("Add Player"):
        player = next(p for p in st.session_state['squad'] if p['name'] == selected_name)
        pos = player.get('position', 'Bench')
        if pos not in position_limits:
            pos = 'Bench'
        if pos_counts[pos] >= position_limits[pos]:
            st.warning(f"Max {pos}s already selected.")
        else:
            st.session_state['selected_team'].append(player)
            st.success(f"{player['name']} added to {pos}.")

elif tab == "Training":
    st.title("Training")
    st.write(f"XP: {st.session_state['xp']}")

    trainable_stats = ["goals", "disposals", "tackles", "inside50", "rebound50", "onepercenters", "hitouts"]

    player_names = [p['name'] for p in st.session_state['squad']]
    selected_player_name = st.selectbox("Select player to train:", player_names)
    selected_stat = st.selectbox("Select stat to train:", trainable_stats)
    xp_cost = 10

    if st.button(f"Train {selected_stat} (+1) for {xp_cost} XP"):
        if st.session_state['xp'] >= xp_cost:
            for p in st.session_state['squad']:
                if p['name'] == selected_player_name:
                    p[selected_stat] = p.get(selected_stat, 0) + 1
                    recalc_overall(p)
                    st.session_state['xp'] -= xp_cost
                    st.session_state['training_log'].append(f"Trained {selected_stat} for {selected_player_name}.")
                    st.success(f"{selected_stat} increased by 1 for {selected_player_name}.")
                    break
        else:
            st.warning("Not enough XP.")

    if st.session_state['training_log']:
        st.subheader("Training Log")
        for log_entry in st.session_state['training_log'][-10:]:
            st.write(log_entry)

elif tab == "Trade/Delist":
    st.title("Trade / Delist")
    st.write("Manage your squad below:")

    squad_names = [p['name'] for p in st.session_state['squad']]
    selected_name = st.selectbox("Select player to delist:", squad_names)

    if st.button("Delist Player"):
        player_to_remove = next((p for p in st.session_state['squad'] if p['name'] == selected_name), None)
        if player_to_remove:
            if player_to_remove in st.session_state['selected_team']:
                st.warning("Cannot delist player currently in selected team.")
            else:
                st.session_state['squad'].remove(player_to_remove)
                st.success(f"{selected_name} has been delisted.")

elif tab == "Store":
    st.title("Store")
    pack_price = 300
    st.write(f"Coins: {st.session_state['coins']} | Pack Price: {pack_price} Coins")
    if st.button("Buy Pack (5 players with 1 legend/rare)"):
        if st.session_state['coins'] >= pack_price:
            st.session_state['coins'] -= pack_price
            # Create pack of 5 players: 1 legend/rare guaranteed
            legends = [p for p in player_pool if p.get('ovr',0) >= 90]
            commons = [p for p in player_pool if p.get('ovr',0) < 90]

            pack = random.sample(commons, 4)
            pack.append(random.choice(legends))

            # Add to squad without duplicates
            added = []
            for pl in pack:
                if pl not in st.session_state['squad']:
                    st.session_state['squad'].append(pl)
                    added.append(pl['name'])

            st.write("You got these players:")
            for pl in pack:
                st.write(player_stats_str(pl))
            if added:
                st.success(f"Added {len(added)} new players to your squad.")
            else:
                st.info("No new players added (duplicates).")
        else:
            st.warning("Not enough coins to buy a pack.")

elif tab == "Play Game":
    st.title("Play Game")

    # Simple opponent team random selection
    opponent_team = random.sample(player_pool, 22)

    st.subheader("Your Team")
    for p in st.session_state['selected_team']:
        st.write(player_stats_str(p))

    st.subheader("Opponent Team")
    for p in opponent_team:
        st.write(player_stats_str(p))

    if st.button("Play Match"):
        your_score = sum(p['ovr'] for p in st.session_state['selected_team']) + random.randint(-10,10)
        opp_score = sum(p['ovr'] for p in opponent_team) + random.randint(-10,10)

        result = "Draw"
        if your_score > opp_score:
            result = "Win"
            st.session_state['xp'] += 20
            st.session_state['coins'] += 100
        elif your_score < opp_score:
            result = "Loss"

        st.write(f"Result: {result} | Your score: {your_score} | Opponent score: {opp_score}")

        st.session_state['game_results'].append({
            'result': result,
            'your_score': your_score,
            'opp_score': opp_score
        })

        if result == "Win":
            st.success("You earned 20 XP and 100 Coins!")
        elif result == "Loss":
            st.warning("Better luck next time!")
        else:
            st.info("It's a draw!")

