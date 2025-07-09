import streamlit as st
import random

# --- Starter Squad: always includes Buddy ---
base_players = [
    # Buddy locked
    {"name": "Lance Franklin", "position": "Forward", "ovr": 90, "photo_url": "https://via.placeholder.com/100x130?text=Lance+Franklin"},
    # Forwards
    {"name": "Tom Lynch", "position": "Forward", "ovr": 78, "photo_url": "https://via.placeholder.com/100x130?text=Tom+Lynch"},
    {"name": "Charlie Cameron", "position": "Forward", "ovr": 76, "photo_url": "https://via.placeholder.com/100x130?text=Charlie+Cameron"},
    {"name": "Jack Higgins", "position": "Forward", "ovr": 74, "photo_url": "https://via.placeholder.com/100x130?text=Jack+Higgins"},
    {"name": "Bayley Fritsch", "position": "Forward", "ovr": 72, "photo_url": "https://via.placeholder.com/100x130?text=Bayley+Fritsch"},
    {"name": "Ben King", "position": "Forward", "ovr": 70, "photo_url": "https://via.placeholder.com/100x130?text=Ben+King"},
    {"name": "Oscar Allen", "position": "Forward", "ovr": 68, "photo_url": "https://via.placeholder.com/100x130?text=Oscar+Allen"},
    # Midfielders
    {"name": "Patrick Cripps", "position": "Midfield", "ovr": 85, "photo_url": "https://via.placeholder.com/100x130?text=Patrick+Cripps"},
    {"name": "Andrew Brayshaw", "position": "Midfield", "ovr": 80, "photo_url": "https://via.placeholder.com/100x130?text=Andrew+Brayshaw"},
    {"name": "Clayton Oliver", "position": "Midfield", "ovr": 82, "photo_url": "https://via.placeholder.com/100x130?text=Clayton+Oliver"},
    {"name": "Matt Rowell", "position": "Midfield", "ovr": 78, "photo_url": "https://via.placeholder.com/100x130?text=Matt+Rowell"},
    {"name": "Josh Daicos", "position": "Midfield", "ovr": 75, "photo_url": "https://via.placeholder.com/100x130?text=Josh+Daicos"},
    {"name": "Caleb Serong", "position": "Midfield", "ovr": 74, "photo_url": "https://via.placeholder.com/100x130?text=Caleb+Serong"},
    {"name": "James Worpel", "position": "Midfield", "ovr": 72, "photo_url": "https://via.placeholder.com/100x130?text=James+Worpel"},
    {"name": "Luke Davies-Uniacke", "position": "Midfield", "ovr": 70, "photo_url": "https://via.placeholder.com/100x130?text=LD+Uniacke"},
    # Defenders
    {"name": "Darcy Moore", "position": "Defender", "ovr": 82, "photo_url": "https://via.placeholder.com/100x130?text=Darcy+Moore"},
    {"name": "Tom Stewart", "position": "Defender", "ovr": 80, "photo_url": "https://via.placeholder.com/100x130?text=Tom+Stewart"},
    {"name": "Harris Andrews", "position": "Defender", "ovr": 79, "photo_url": "https://via.placeholder.com/100x130?text=Harris+Andrews"},
    {"name": "Luke Ryan", "position": "Defender", "ovr": 78, "photo_url": "https://via.placeholder.com/100x130?text=Luke+Ryan"},
    {"name": "Jake Lever", "position": "Defender", "ovr": 75, "photo_url": "https://via.placeholder.com/100x130?text=Jake+Lever"},
    {"name": "Alex Witherden", "position": "Defender", "ovr": 74, "photo_url": "https://via.placeholder.com/100x130?text=Alex+Witherden"},
    {"name": "Nick Haynes", "position": "Defender", "ovr": 72, "photo_url": "https://via.placeholder.com/100x130?text=Nick+Haynes"},
    {"name": "Will Powell", "position": "Defender", "ovr": 70, "photo_url": "https://via.placeholder.com/100x130?text=Will+Powell"},
    # Rucks
    {"name": "Max Gawn", "position": "Ruck", "ovr": 85, "photo_url": "https://via.placeholder.com/100x130?text=Max+Gawn"},
    {"name": "Brodie Grundy", "position": "Ruck", "ovr": 82, "photo_url": "https://via.placeholder.com/100x130?text=Brodie+Grundy"},
    {"name": "Tim English", "position": "Ruck", "ovr": 80, "photo_url": "https://via.placeholder.com/100x130?text=Tim+English"},
    {"name": "Darcy Cameron", "position": "Ruck", "ovr": 78, "photo_url": "https://via.placeholder.com/100x130?text=Darcy+Cameron"},
]

# Required slots
position_limits = {
    "Forward": 6,
    "Midfield": 6,
    "Defender": 6,
    "Ruck": 2
}

# Session state
if 'squad' not in st.session_state:
    st.session_state.squad = base_players.copy()
    st.session_state.selected_team = [base_players[0]]  # Buddy auto-picked
    st.session_state.xp = 0
    st.session_state.coins = 500

# Helpers
def count_position(pos):
    return len([p for p in st.session_state.selected_team if p['position'] == pos])

# UI
st.title("AFL Squad Career Manager")

st.write(f"**Selected Players:** {len(st.session_state.selected_team)}/20")
st.write(f"XP: {st.session_state.xp} | Coins: {st.session_state.coins}")

# Show Squad
for player in st.session_state.squad:
    is_selected = player in st.session_state.selected_team
    st.markdown(f"""
    <div style="border:2px solid {'green' if is_selected else '#333'}; border-radius:8px; padding:8px; display:inline-block; margin:5px; width:140px; text-align:center;">
        <img src="{player['photo_url']}" width="100">
        <br><b>{player['name']}</b><br>{player['position']} | OVR {player['ovr']}
    </div>
    """, unsafe_allow_html=True)
    cols = st.columns(2)
    with cols[0]:
        if not is_selected and st.button(f"Add {player['name']}", key=f"add_{player['name']}"):
            if count_position(player['position']) < position_limits[player['position']]:
                st.session_state.selected_team.append(player)
            else:
                st.warning(f"Max {player['position']} slots filled.")
    with cols[1]:
        if is_selected and player['name'] != "Lance Franklin" and st.button(f"Remove {player['name']}", key=f"remove_{player['name']}"):
            st.session_state.selected_team.remove(player)

# Save
if st.button("Save Team"):
    if len(st.session_state.selected_team) != 20:
        st.error("Team must have 20 players.")
    else:
        st.success("Team saved!")

# Play Match
st.header("Play Match")
if st.button("Play vs AI"):
    if len(st.session_state.selected_team) != 20:
        st.warning("Team must be full to play.")
    else:
        result = random.choice(["Win", "Loss", "Draw"])
        xp_gain = {"Win": 50, "Draw": 25, "Loss": 10}[result]
        coin_gain = {"Win": 100, "Draw": 50, "Loss": 0}[result]
        st.session_state.xp += xp_gain
        st.session_state.coins += coin_gain
        st.success(f"Result: {result}! +{xp_gain} XP, +{coin_gain} coins")

# Store
st.header("Store")
if st.button("Buy Pack (200 coins)"):
    if st.session_state.coins >= 200:
        st.session_state.coins -= 200
        st.session_state.xp += 50
        st.success("Bought a pack: +50 XP")
    else:
        st.error("Not enough coins!")

# Training
st.header("Training")
player_names = [p['name'] for p in st.session_state.selected_team]
player_choice = st.selectbox("Train Player", player_names)
if st.button("Train (20 XP)"):
    if st.session_state.xp >= 20:
        st.session_state.xp -= 20
        st.success(f"{player_choice} trained! +0.5 OVR")
        for p in st.session_state.squad:
            if p['name'] == player_choice:
                p['ovr'] += 0.5
    else:
        st.error("Not enough XP!")
