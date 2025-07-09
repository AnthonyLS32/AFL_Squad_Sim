import streamlit as st
import json
import random

# --- Load player pool ---
with open('players.json') as f:
    player_pool = json.load(f)

# --- Balanced squad builder ---
def balanced_squad():
    squad = []
    squad += random.sample([p for p in player_pool if p['position'] == "Forward"], 8)
    squad += random.sample([p for p in player_pool if p['position'] == "Midfield"], 8)
    squad += random.sample([p for p in player_pool if p['position'] == "Ruck"], 3)
    squad += random.sample([p for p in player_pool if p['position'] == "Defender"], 8)
    extras = [p for p in player_pool if p not in squad]
    squad += random.sample(extras, 3)
    return squad

# --- Init session state ---
if 'squad' not in st.session_state:
    st.session_state.squad = balanced_squad()
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

# --- CSS styling ---
st.markdown("""
<style>
.player-card {
  border: 2px solid #444; border-radius: 8px; padding: 10px; text-align: center;
  width: 180px; margin: 10px; display: inline-block; vertical-align: top;
  background: #f9f9f9; transition: transform 0.2s, box-shadow 0.2s;
}
.player-card:hover {
  transform: scale(1.03); box-shadow: 0 0 8px #aaa;
}
.selected {
  border: 3px solid #007bff; background: #e8f4ff;
}
</style>
""", unsafe_allow_html=True)

# --- Count how many already selected for this position ---
def count_position(pos):
    return len([p for p in st.session_state.selected_team if p['position'] == pos])

# --- App header ---
st.title("AFL FUT Career Squad Manager")
st.write(f"**Selected Players:** {len(st.session_state.selected_team)}/22")

# --- Display squad cards ---
for player in st.session_state.squad:
    is_selected = player in st.session_state.selected_team
    card_class = "player-card selected" if is_selected else "player-card"

    # fallback if photo_url is empty or invalid
    photo = player.get('photo_url') or "https://via.placeholder.com/100x130.png?text=Player"

    st.markdown(f"""
    <div class="{card_class}">
      <img src="{photo}" width="100"><br>
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

# --- Process click action AFTER loop ---
if st.session_state.click_action == "select":
    p = st.session_state.click_player
    limit = st.session_state.position_limits[p['position']]
    if count_position(p['position']) < limit:
        st.session_state.selected_team.append(p)
    else:
        st.warning(f"Position limit reached for {p['position']}!")
    st.session_state.click_action = None
    st.session_state.click_player = None
    st.experimental_rerun()

elif st.session_state.click_action == "deselect":
    p = st.session_state.click_player
    if p in st.session_state.selected_team:
        st.session_state.selected_team.remove(p)
    st.session_state.click_action = None
    st.session_state.click_player = None
    st.experimental_rerun()

# --- Selected team summary ---
st.header("Your Selected Team")
if st.session_state.selected_team:
    for p in st.session_state.selected_team:
        st.write(f"{p['name']} | {p['position']} | OVR: {p['ovr']}")
else:
    st.info("No players selected yet.")

# --- Save button ---
if st.button("Save Team"):
    if len(st.session_state.selected_team) < 13:
        st.warning("Pick at least 13 players before saving your team!")
    else:
        st.success("Team saved! 🚀")
