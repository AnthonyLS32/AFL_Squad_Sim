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

# --- Inject CSS for card styling ---
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

# --- Helper to count position slots used ---
def count_position(pos):
    return len([p for p in st.session_state.selected_team if p['position'] == pos])

# --- Squad Display ---
st.title("AFL FUT Squad Manager")

st.header("Your Squad")
st.write(f"Selected Players: {len(st.session_state.selected_team)}/22")

for player in st.session_state.squad:
    is_selected = player in st.session_state.selected_team
    card_class = "player-card selected" if is_selected else "player-card"

    st.markdown(f"""
    <div class="{card_class}">
      <img src="{player['photo_url']}" width="100"><br>
      <b>{player['name']}</b><br>
      {player['position']} | OVR: {player['ovr']}<br>
    """, unsafe_allow_html=True)

    if not is_selected:
        if st.button(f"Select {player['name']}", key=f"sel_{player['name']}"):
            pos = player['position']
            if count_position(pos) < st.session_state.position_limits[pos]:
                st.session_state.selected_team.append(player)
                st.experimental_rerun()
            else:
                st.warning(f"No more slots for {pos}s!")
    else:
        if st.button(f"Deselect {player['name']}", key=f"desel_{player['name']}"):
            st.session_state.selected_team.remove(player)
            st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# --- Selected Team Summary ---
st.header("Selected Team")
if st.session_state.selected_team:
    for p in st.session_state.selected_team:
        st.write(f"{p['name']} | {p['position']} | OVR: {p['ovr']}")
else:
    st.info("No players selected yet.")

if st.button("Save Team"):
    if len(st.session_state.selected_team) < 13:
        st.warning("You must select at least 13 players to save a team.")
    else:
        st.success("Team saved!")

