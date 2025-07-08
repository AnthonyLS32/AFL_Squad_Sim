import streamlit as st
import json
import random

# Load players.json
with open('players.json') as f:
    player_pool = json.load(f)

# Initialize session state
if 'squad' not in st.session_state:
    # Load whole player pool as squad (all players)
    st.session_state['squad'] = player_pool.copy()

if 'selected_team' not in st.session_state:
    # Prepopulate selected_team with 4 forwards, 4 mids, 2 rucks, 4 backs, 3 bench
    forwards = [p for p in player_pool if p['line'] == "Forward"]
    mids = [p for p in player_pool if p['line'] == "Mid"]
    rucks = [p for p in player_pool if p['line'] == "Ruck"]
    backs = [p for p in player_pool if p['line'] == "Back"]
    bench = [p for p in player_pool if p['line'] == "Bench"]

    # Randomly sample players for each line or fallback to fill if not enough players
    selected_team = []
    selected_team += random.sample(forwards, min(4, len(forwards)))
    selected_team += random.sample(mids, min(4, len(mids)))
    selected_team += random.sample(rucks, min(2, len(rucks)))
    selected_team += random.sample(backs, min(4, len(backs)))
    selected_team += random.sample(bench, min(3, len(bench)))

    st.session_state['selected_team'] = selected_team

if 'xp' not in st.session_state:
    st.session_state['xp'] = 0

if 'coins' not in st.session_state:
    st.session_state['coins'] = 500

tab = st.sidebar.selectbox(
    "Choose tab",
    ["Squad", "Selected Team", "Training", "Trade/Delist", "Store"]
)

def player_full_stats_str(p):
    return (
        f"{p['name']} | Line: {p['line']} | "
        f"OVR: {p['ovr']} | G:{p.get('goals',0)} "
        f"D:{p.get('disposals',0)} T:{p.get('tackles',0)} "
        f"I50:{p.get('inside50',0)} R50:{p.get('rebound50',0)} "
        f"1%:{p.get('onepercenters',0)} HO:{p.get('hitouts',0)}"
    )

if tab == "Squad":
    st.title("Full Squad")
    st.write(f"XP: {st.session_state['xp']} | Coins: {st.session_state['coins']}")
    for p in st.session_state['squad']:
        st.write(player_full_stats_str(p))

elif tab == "Selected Team":
    st.title("Selected Team")
    st.write(f"XP: {st.session_state['xp']} | Coins: {st.session_state['coins']}")

    # Group players by line for display
    lines = ["Back", "Mid", "Ruck", "Forward", "Bench"]
    limits = {"Forward": 4, "Mid": 4, "Ruck": 2, "Back": 4, "Bench": 3}

    # Count current lineup numbers
    line_counts = {line: 0 for line in lines}
    for p in st.session_state['selected_team']:
        line_counts[p['line']] += 1

    st.write(
        f"Selected Team Counts: Forwards {line_counts['Forward']}/4, "
        f"Mids {line_counts['Mid']}/4, Rucks {line_counts['Ruck']}/2, "
        f"Backs {line_counts['Back']}/4, Bench {line_counts['Bench']}/3"
    )

    # Show players by line
    for line in lines:
        st.subheader(f"{line}s:")
        for p in [pl for pl in st.session_state['selected_team'] if pl['line'] == line]:
            st.write(player_full_stats_str(p))

elif tab == "Training":
    st.title("Training")
    st.write("Training features coming soon...")

elif tab == "Trade/Delist":
    st.title("Trade / Delist")
    st.write("Manage players coming soon...")

elif tab == "Store":
    st.title("Store")
    st.write("Purchase packs and items coming soon...")
