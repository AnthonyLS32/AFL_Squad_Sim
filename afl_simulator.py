import streamlit as st
import json
import random

# --- Load player pool ---
with open('players.json') as f:
    player_pool = json.load(f)

# --- Init session state ---
if 'squad' not in st.session_state:
    st.session_state.squad = random.sample(player_pool, 30)
if 'selected_team' not in st.session_state:
    st.session_state.selected_team = []
if 'position_limits' not in st.session_state:
    st.session_state.position_limits = {
        'Forward': 6, 'Midfield': 6, 'Ruck': 2, 'Defender': 6, 'Bench': 2
    }
if 'click_action' not in st.session_state:
    st.session_state.click_action = None
if 'click_player' not in st.session_state:
    st.session_state.click_player = None

# --- Inject CSS for player card styling ---
st.markdown("""
<style>
.player-card {
  border: 2px solid #444; border-radius: 10px; padding: 10px; text-align: center; width: 180px;
  margin: 10px; display: inline-block; vertical-align: top; background: #f0f0f0;
  transition: transform 0.2s, box-shadow 0.2s;
}
.player-card:hover {
  transform: scale(1.05); box-shadow: 0 0 10px #aaa;
}
.selected {
  border: 3px solid #2c7be5; background: #d0e8ff;
}
</style>
""", unsafe_allow_html=True)

# --- Helper: count how many players already picked in this position ---
def count_position(pos):
    return len([p for p in st.session_state.selected_team if p['position'] == pos])

# --- Title and status ---
st.title("AFL FUT Squad Manager")
st.header("Your Squad")
st.write(f"Selected Players: {len(st.session_state.selected_team)}/22")

# --- Show Squad ---
for player in st.session_state.squad:
    is_selected = player in st.session_state.selected_team
    card_class = "player-card selected" if is_selected else "player-card"

    st.markdown(f"""
    <div class="{card_class}">
      <img src="{player['photo_url']}" width="100"><br>
      <b>{player['name']}</b><br>
      {player['position']} | OVR: {player['ovr']}<br>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if not is_selected:
            if st.button(f"Select {player['name']}", key=f"sel_{player['name']}"):
                st.session_state.click_action = "select"
                st.session_state.click_player = player
    with col2:
        if is_selected:
            if st.button(f"Deselect {player['name']}", key=f"desel_{player['name']}"):
                st.session_state.click_action = "deselect"
                st.session_state.click_player = player

# --- Handle click actions AFTER loop ---
if st.session_state.click_action == "select":
    p = st.session_state.click_player
    if count_position(p['position']) < st.session_state.position_limits[p['position']]:
        st.session_state.selected_team.append(p)
    else:
        st.warning(f"No more slots for {p['position']}s!")
    st.session_state.click_action = None
    st.session_state.click_player = None
    st.experimental_rerun()

elif st.session_state.click_action == "deselect":
    p = st.session_state.click_player
    st.session_state.selected_team.remove(p)
    st.session_state.click_action = None
    st.session_state.click_player = None
    st.experimental_rerun()

# --- Show selected team summary ---
st.header("Selected Team")
if st.session_state.selected_team:
    for p in st.session_state.selected_team:
        st.write(f"{p['name']} | {p['position']} | OVR: {p['ovr']}")
else:
    st.info("No players selected yet.")

# --- Save Team ---
if st.button("Save Team"):
    if len(st.session_state.selected_team) < 13:
        st.warning("Select at least 13 players to save a team.")
    else:
        st.success("Team saved!")
