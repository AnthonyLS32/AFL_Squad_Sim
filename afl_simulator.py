import streamlit as st

# --- Starter Squad ---
player_pool = [
    # Forwards (7)
    {"name": "Lance Franklin", "position": "Forward", "ovr": 90, "photo_url": "https://via.placeholder.com/100x130?text=Lance+Franklin"},
    {"name": "Tom Lynch", "position": "Forward", "ovr": 85, "photo_url": "https://via.placeholder.com/100x130?text=Tom+Lynch"},
    {"name": "Charlie Cameron", "position": "Forward", "ovr": 83, "photo_url": "https://via.placeholder.com/100x130?text=Charlie+Cameron"},
    {"name": "Isaac Heeney", "position": "Forward", "ovr": 82, "photo_url": "https://via.placeholder.com/100x130?text=Isaac+Heeney"},
    {"name": "Harry McKay", "position": "Forward", "ovr": 80, "photo_url": "https://via.placeholder.com/100x130?text=Harry+McKay"},
    {"name": "Jack Higgins", "position": "Forward", "ovr": 78, "photo_url": "https://via.placeholder.com/100x130?text=Jack+Higgins"},
    {"name": "Bayley Fritsch", "position": "Forward", "ovr": 77, "photo_url": "https://via.placeholder.com/100x130?text=Bayley+Fritsch"},

    # Midfielders (7)
    {"name": "Patrick Cripps", "position": "Midfield", "ovr": 92, "photo_url": "https://via.placeholder.com/100x130?text=Patrick+Cripps"},
    {"name": "Andrew Brayshaw", "position": "Midfield", "ovr": 88, "photo_url": "https://via.placeholder.com/100x130?text=Andrew+Brayshaw"},
    {"name": "Clayton Oliver", "position": "Midfield", "ovr": 89, "photo_url": "https://via.placeholder.com/100x130?text=Clayton+Oliver"},
    {"name": "Jack Steele", "position": "Midfield", "ovr": 87, "photo_url": "https://via.placeholder.com/100x130?text=Jack+Steele"},
    {"name": "Touk Miller", "position": "Midfield", "ovr": 86, "photo_url": "https://via.placeholder.com/100x130?text=Touk+Miller"},
    {"name": "Matt Rowell", "position": "Midfield", "ovr": 82, "photo_url": "https://via.placeholder.com/100x130?text=Matt+Rowell"},
    {"name": "Josh Daicos", "position": "Midfield", "ovr": 80, "photo_url": "https://via.placeholder.com/100x130?text=Josh+Daicos"},

    # Defenders (7)
    {"name": "Darcy Moore", "position": "Defender", "ovr": 87, "photo_url": "https://via.placeholder.com/100x130?text=Darcy+Moore"},
    {"name": "Tom Stewart", "position": "Defender", "ovr": 88, "photo_url": "https://via.placeholder.com/100x130?text=Tom+Stewart"},
    {"name": "Harris Andrews", "position": "Defender", "ovr": 85, "photo_url": "https://via.placeholder.com/100x130?text=Harris+Andrews"},
    {"name": "Luke Ryan", "position": "Defender", "ovr": 86, "photo_url": "https://via.placeholder.com/100x130?text=Luke+Ryan"},
    {"name": "Jake Lever", "position": "Defender", "ovr": 84, "photo_url": "https://via.placeholder.com/100x130?text=Jake+Lever"},
    {"name": "Alex Witherden", "position": "Defender", "ovr": 82, "photo_url": "https://via.placeholder.com/100x130?text=Alex+Witherden"},
    {"name": "Nick Haynes", "position": "Defender", "ovr": 80, "photo_url": "https://via.placeholder.com/100x130?text=Nick+Haynes"},

    # Rucks (3)
    {"name": "Max Gawn", "position": "Ruck", "ovr": 91, "photo_url": "https://via.placeholder.com/100x130?text=Max+Gawn"},
    {"name": "Brodie Grundy", "position": "Ruck", "ovr": 89, "photo_url": "https://via.placeholder.com/100x130?text=Brodie+Grundy"},
    {"name": "Tim English", "position": "Ruck", "ovr": 86, "photo_url": "https://via.placeholder.com/100x130?text=Tim+English"},
]

# --- Required Slots ---
position_limits = {
    "Forward": 6,
    "Midfield": 6,
    "Defender": 6,
    "Ruck": 2
}

# --- Session State ---
if 'squad' not in st.session_state:
    st.session_state.squad = player_pool.copy()
if 'selected_team' not in st.session_state:
    st.session_state.selected_team = []

# --- Helpers ---
def count_position(pos):
    return len([p for p in st.session_state.selected_team if p['position'] == pos])

# --- Title ---
st.title("AFL Career Squad Manager")

st.write(f"**Selected Players:** {len(st.session_state.selected_team)}/20")

# --- Squad Display ---
for player in st.session_state.squad:
    is_selected = player in st.session_state.selected_team
    card_class = "player-card selected" if is_selected else "player-card"

    st.markdown(f"""
    <div class="{card_class}">
        <img src="{player['photo_url']}" width="100">
        <h4>{player['name']}</h4>
        <b>{player['position']}</b> | OVR: {player['ovr']}
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if not is_selected and st.button(f"Add {player['name']}", key=f"add_{player['name']}"):
            limit = position_limits.get(player['position'], 0)
            if count_position(player['position']) < limit:
                st.session_state.selected_team.append(player)
            else:
                st.warning(f"Max {player['position']} slots filled.")

    with col2:
        if is_selected and st.button(f"Remove {player['name']}", key=f"rem_{player['name']}"):
            st.session_state.selected_team.remove(player)

# --- Final Save ---
if st.button("Save Team"):
    if len(st.session_state.selected_team) != 20:
        st.error("Your team must have exactly 20 players.")
    else:
        st.success("Team saved!")

# --- CSS ---
st.markdown("""
<style>
.player-card {
  border: 2px solid #333; border-radius: 8px; padding: 10px; text-align: center;
  width: 180px; margin: 10px; display: inline-block; vertical-align: top;
  background: #f0f0f0;
}
.selected {
  border: 3px solid green; background: #e0ffe0;
}
</style>
""", unsafe_allow_html=True)
