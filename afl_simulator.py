import streamlit as st
import json

# --- Hardcoded safe starter squad ---
player_pool = [
    {"name": "Lance Franklin", "position": "Forward", "ovr": 90, "photo_url": "https://via.placeholder.com/100x130.png?text=Lance+Franklin"},
    {"name": "Tom Lynch", "position": "Forward", "ovr": 85, "photo_url": "https://via.placeholder.com/100x130.png?text=Tom+Lynch"},
    {"name": "Charlie Cameron", "position": "Forward", "ovr": 83, "photo_url": "https://via.placeholder.com/100x130.png?text=Charlie+Cameron"},
    {"name": "Isaac Heeney", "position": "Forward", "ovr": 82, "photo_url": "https://via.placeholder.com/100x130.png?text=Isaac+Heeney"},
    {"name": "Harry McKay", "position": "Forward", "ovr": 80, "photo_url": "https://via.placeholder.com/100x130.png?text=Harry+McKay"},
    {"name": "Jack Higgins", "position": "Forward", "ovr": 78, "photo_url": "https://via.placeholder.com/100x130.png?text=Jack+Higgins"},

    {"name": "Patrick Cripps", "position": "Midfield", "ovr": 92, "photo_url": "https://via.placeholder.com/100x130.png?text=Patrick+Cripps"},
    {"name": "Andrew Brayshaw", "position": "Midfield", "ovr": 88, "photo_url": "https://via.placeholder.com/100x130.png?text=Andrew+Brayshaw"},
    {"name": "Clayton Oliver", "position": "Midfield", "ovr": 89, "photo_url": "https://via.placeholder.com/100x130.png?text=Clayton+Oliver"},
    {"name": "Jack Steele", "position": "Midfield", "ovr": 87, "photo_url": "https://via.placeholder.com/100x130.png?text=Jack+Steele"},
    {"name": "Touk Miller", "position": "Midfield", "ovr": 86, "photo_url": "https://via.placeholder.com/100x130.png?text=Touk+Miller"},
    {"name": "Matt Rowell", "position": "Midfield", "ovr": 82, "photo_url": "https://via.placeholder.com/100x130.png?text=Matt+Rowell"},

    {"name": "Darcy Moore", "position": "Defender", "ovr": 87, "photo_url": "https://via.placeholder.com/100x130.png?text=Darcy+Moore"},
    {"name": "Tom Stewart", "position": "Defender", "ovr": 88, "photo_url": "https://via.placeholder.com/100x130.png?text=Tom+Stewart"},
    {"name": "Harris Andrews", "position": "Defender", "ovr": 85, "photo_url": "https://via.placeholder.com/100x130.png?text=Harris+Andrews"},
    {"name": "Luke Ryan", "position": "Defender", "ovr": 86, "photo_url": "https://via.placeholder.com/100x130.png?text=Luke+Ryan"},
    {"name": "Jake Lever", "position": "Defender", "ovr": 84, "photo_url": "https://via.placeholder.com/100x130.png?text=Jake+Lever"},
    {"name": "Alex Witherden", "position": "Defender", "ovr": 82, "photo_url": "https://via.placeholder.com/100x130.png?text=Alex+Witherden"},

    {"name": "Max Gawn", "position": "Ruck", "ovr": 91, "photo_url": "https://via.placeholder.com/100x130.png?text=Max+Gawn"},
    {"name": "Brodie Grundy", "position": "Ruck", "ovr": 89, "photo_url": "https://via.placeholder.com/100x130.png?text=Brodie+Grundy"},

    {"name": "Wildcard 1", "position": "Forward", "ovr": 75, "photo_url": "https://via.placeholder.com/100x130.png?text=Wildcard+1"},
    {"name": "Wildcard 2", "position": "Midfield", "ovr": 74, "photo_url": "https://via.placeholder.com/100x130.png?text=Wildcard+2"},
    {"name": "Wildcard 3", "position": "Defender", "ovr": 72, "photo_url": "https://via.placeholder.com/100x130.png?text=Wildcard+3"},
    {"name": "Wildcard 4", "position": "Ruck", "ovr": 70, "photo_url": "https://via.placeholder.com/100x130.png?text=Wildcard+4"}
]

# --- Init state ---
if 'squad' not in st.session_state:
    st.session_state.squad = player_pool.copy()
if 'selected_team' not in st.session_state:
    st.session_state.selected_team = []
if 'position_limits' not in st.session_state:
    st.session_state.position_limits = {
        'Forward': 6, 'Midfield': 6, 'Defender': 6, 'Ruck': 2, 'Bench': 2
    }
if 'click_action' not in st.session_state:
    st.session_state.click_action = None
if 'click_player' not in st.session_state:
    st.session_state.click_player = None

# --- CSS ---
st.markdown("""
<style>
.player-card {
  border: 2px solid #333; border-radius: 8px; padding: 10px; text-align: center;
  width: 180px; margin: 10px; display: inline-block; vertical-align: top;
  background: #f9f9f9; transition: transform 0.2s, box-shadow 0.2s;
}
.player-card:hover {
  transform: scale(1.02); box-shadow: 0 0 6px #aaa;
}
.selected {
  border: 3px solid #2c7be5; background: #e7f2ff;
}
</style>
""", unsafe_allow_html=True)

# --- Helpers ---
def count_position(pos):
    return len([p for p in st.session_state.selected_team if p['position'] == pos])

# --- UI ---
st.title("AFL Career Starter Squad")
st.write(f"Selected: {len(st.session_state.selected_team)}/22")

for player in st.session_state.squad:
    is_selected = player in st.session_state.selected_team
    cls = "player-card selected" if is_selected else "player-card"

    st.markdown(f"""
    <div class="{cls}">
      <img src="{player['photo_url']}" width="100"><br>
      <b>{player['name']}</b><br>
      {player['position']} | OVR: {player['ovr']}
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if not is_selected and st.button(f"Select {player['name']}", key=f"sel_{player['name']}"):
            st.session_state.click_action = "select"
            st.session_state.click_player = player
    with c2:
        if is_selected and st.button(f"Deselect {player['name']}", key=f"des_{player['name']}"):
            st.session_state.click_action = "deselect"
            st.session_state.click_player = player

# --- Process click ---
if st.session_state.click_action == "select":
    p = st.session_state.click_player
    if count_position(p['position']) < st.session_state.position_limits[p['position']]:
        st.session_state.selected_team.append(p)
    else:
        st.warning(f"Max {p['position']}s reached.")
    st.session_state.click_action = None
    st.session_state.click_player = None
    st.experimental_rerun()

elif st.session_state.click_action == "deselect":
    p = st.session_state.click_player
    st.session_state.selected_team.remove(p)
    st.session_state.click_action = None
    st.session_state.click_player = None
    st.experimental_rerun()

# --- Selected team view ---
st.header("Selected Team")
if st.session_state.selected_team:
    for p in st.session_state.selected_team:
        st.write(f"{p['name']} | {p['position']} | OVR: {p['ovr']}")
else:
    st.info("No players selected yet.")

if st.button("Save Team"):
    if len(st.session_state.selected_team) < 13:
        st.warning("Pick at least 13 players.")
    else:
        st.success("Team saved!")
