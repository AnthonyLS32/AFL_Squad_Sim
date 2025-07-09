import streamlit as st
import random

# ----------- Player Data (starter squad) -----------
players = [
    {"name": "Lance Franklin", "position": "Forward", "ovr": 90, "photo_url": "https://via.placeholder.com/100x140?text=Buddy+Franklin"},
    {"name": "Tom Lynch", "position": "Forward", "ovr": 78, "photo_url": "https://via.placeholder.com/100x140?text=Tom+Lynch"},
    {"name": "Charlie Cameron", "position": "Forward", "ovr": 76, "photo_url": "https://via.placeholder.com/100x140?text=Charlie+Cameron"},
    {"name": "Jack Higgins", "position": "Forward", "ovr": 75, "photo_url": "https://via.placeholder.com/100x140?text=Jack+Higgins"},
    {"name": "Ben King", "position": "Forward", "ovr": 73, "photo_url": "https://via.placeholder.com/100x140?text=Ben+King"},
    {"name": "Oscar Allen", "position": "Forward", "ovr": 72, "photo_url": "https://via.placeholder.com/100x140?text=Oscar+Allen"},
    {"name": "Patrick Cripps", "position": "Midfield", "ovr": 85, "photo_url": "https://via.placeholder.com/100x140?text=Patrick+Cripps"},
    {"name": "Clayton Oliver", "position": "Midfield", "ovr": 83, "photo_url": "https://via.placeholder.com/100x140?text=Clayton+Oliver"},
    {"name": "Andrew Brayshaw", "position": "Midfield", "ovr": 81, "photo_url": "https://via.placeholder.com/100x140?text=Andrew+Brayshaw"},
    {"name": "Matt Rowell", "position": "Midfield", "ovr": 78, "photo_url": "https://via.placeholder.com/100x140?text=Matt+Rowell"},
    {"name": "James Worpel", "position": "Midfield", "ovr": 76, "photo_url": "https://via.placeholder.com/100x140?text=James+Worpel"},
    {"name": "Caleb Serong", "position": "Midfield", "ovr": 74, "photo_url": "https://via.placeholder.com/100x140?text=Caleb+Serong"},
    {"name": "Darcy Moore", "position": "Defender", "ovr": 82, "photo_url": "https://via.placeholder.com/100x140?text=Darcy+Moore"},
    {"name": "Tom Stewart", "position": "Defender", "ovr": 80, "photo_url": "https://via.placeholder.com/100x140?text=Tom+Stewart"},
    {"name": "Harris Andrews", "position": "Defender", "ovr": 78, "photo_url": "https://via.placeholder.com/100x140?text=Harris+Andrews"},
    {"name": "Luke Ryan", "position": "Defender", "ovr": 77, "photo_url": "https://via.placeholder.com/100x140?text=Luke+Ryan"},
    {"name": "Jake Lever", "position": "Defender", "ovr": 75, "photo_url": "https://via.placeholder.com/100x140?text=Jake+Lever"},
    {"name": "Alex Witherden", "position": "Defender", "ovr": 73, "photo_url": "https://via.placeholder.com/100x140?text=Alex+Witherden"},
    {"name": "Max Gawn", "position": "Ruck", "ovr": 85, "photo_url": "https://via.placeholder.com/100x140?text=Max+Gawn"},
    {"name": "Brodie Grundy", "position": "Ruck", "ovr": 83, "photo_url": "https://via.placeholder.com/100x140?text=Brodie+Grundy"},
    {"name": "Tim English", "position": "Ruck", "ovr": 80, "photo_url": "https://via.placeholder.com/100x140?text=Tim+English"},
]

# Position max limits for selected team
position_limits = {"Forward": 6, "Midfield": 6, "Defender": 6, "Ruck": 2}

# ----------- Session State Initialization -----------
if "squad" not in st.session_state:
    st.session_state.squad = players.copy()
    st.session_state.selected_team = [players[0]]  # Buddy always selected initially
    st.session_state.xp = 0
    st.session_state.coins = 500
    st.session_state.match_log = []

# ----------- Helpers -----------
def render_player_card(player, selected=False):
    border_color = "green" if selected else "#ccc"
    return f"""
        <div style="border:2px solid {border_color}; border-radius:8px; padding:10px; margin:5px; width:120px; text-align:center; display:inline-block;">
            <img src="{player['photo_url']}" width="100" height="140" style="border-radius:5px;" />
            <br><b>{player['name']}</b>
            <br><small>{player['position']} | OVR: {player['ovr']}</small>
        </div>
    """

def autopick_team():
    new_team = []
    # Always include Buddy Franklin (first player)
    buddy = players[0]
    new_team.append(buddy)
    
    # For each position, pick top players (excluding buddy if applicable)
    for pos, max_count in position_limits.items():
        # Exclude buddy if in this position so he doesn't get duplicated
        pool = [p for p in st.session_state.squad if p["position"] == pos and p != buddy]
        top_players = sorted(pool, key=lambda x: x["ovr"], reverse=True)[:max_count]
        new_team.extend(top_players)
    
    # If the buddy is in a position and counted twice, fix the count below
    # But since we add buddy once and max_count players per pos, total is > max_count by one position
    
    # Trim to exactly position limits per position
    final_team = []
    counts = {pos: 0 for pos in position_limits}
    for p in new_team:
        if counts[p["position"]] < position_limits[p["position"]]:
            final_team.append(p)
            counts[p["position"]] += 1
    return final_team

# ----------- UI: Squad Tab -----------
st.title("AFL FUT Manager")
st.sidebar.title("Menu")
tab = st.sidebar.radio("Select Tab:", ["Squad", "Selected Team", "Play Match", "Training", "Store"])

st.sidebar.markdown(f"**XP:** {st.session_state.xp}  \n**Coins:** {st.session_state.coins}")

if tab == "Squad":
    st.header("Your Squad")
    for p in st.session_state.squad:
        selected = p in st.session_state.selected_team
        st.markdown(render_player_card(p, selected), unsafe_allow_html=True)

elif tab == "Selected Team":
    st.header("Select Your Team (Must match position limits)")

    if st.button("Auto Pick Best Team"):
        team = autopick_team()
        st.session_state.selected_team = team
        st.success("Auto-picked best team!")

    # Build selection UI per position
    new_selection = []

    for pos, max_count in position_limits.items():
        st.subheader(f"{pos}s ({max_count})")
        available_players = [p for p in st.session_state.squad if p["position"] == pos]
        selected_names = [p["name"] for p in st.session_state.selected_team if p["position"] == pos]

        for i in range(max_count):
            default_index = 0
            if i < len(selected_names):
                default_index = next((idx for idx, p in enumerate(available_players) if p["name"] == selected_names[i]), 0)
            player_names = [p["name"] for p in available_players]
            chosen_name = st.selectbox(f"{pos} #{i+1}", player_names, index=default_index, key=f"{pos}_{i}")
            chosen_player = next(p for p in available_players if p["name"] == chosen_name)
            new_selection.append(chosen_player)

    if st.button("Save Selected Team"):
        # Validate counts
        counts = {pos: 0 for pos in position_limits}
        for p in new_selection:
            counts[p["position"]] += 1
        if counts == position_limits:
            st.session_state.selected_team = new_selection
            st.success("Team saved!")
        else:
            st.error(f"Selection invalid! Positions: {counts}")

    # Show current selected team
    st.markdown("### Current Selected Team")
    for p in st.session_state.selected_team:
        st.markdown(render_player_card(p, True), unsafe_allow_html=True)

elif tab == "Play Match":
    st.header("Play Match")

    # Check valid team
    counts = {pos: 0 for pos in position_limits}
    for p in st.session_state.selected_team:
        counts[p["position"]] += 1
    if counts != position_limits:
        st.warning(f"Your selected team is invalid! Current counts: {counts}")
    else:
        if st.button("Kick Off vs AI Club"):
            opponent = random.choice(["Melbourne", "Hawthorn", "Fremantle", "Richmond", "Geelong"])
            result = random.choices(["Win", "Draw", "Loss"], weights=[0.5, 0.2, 0.3])[0]
            xp_gain = 50 if result == "Win" else 25 if result == "Draw" else 10
            coin_gain = 100 if result == "Win" else 50 if result == "Draw" else 0
            st.session_state.xp += xp_gain
            st.session_state.coins += coin_gain

            st.subheader(f"Result: {result} vs {opponent}")
            st.write(f"You earned {xp_gain} XP & {coin_gain} coins.")

            st.write("**Top Disposal Getters:**")
            for p in random.sample(st.session_state.selected_team, 3):
                disposals = random.randint(10, 30)
                st.write(f"{p['name']}: {disposals} disposals")

            st.write("**Goal Kickers:**")
            for p in random.sample(st.session_state.selected_team, 3):
                goals = random.randint(1, 4)
                st.write(f"{p['name']}: {goals} goals")

            # Log match
            st.session_state.match_log.append({
                "opponent": opponent,
                "result": result,
                "xp": xp_gain,
                "coins": coin_gain,
            })

    if st.session_state.match_log:
        st.subheader("Match History (Last 5)")
        for m in st.session_state.match_log[-5:]:
            st.write(f"{m['result']} vs {m['opponent']} (+{m['xp']} XP, +{m['coins']} coins)")

elif tab == "Training":
    st.header("Training Center")
    st.write(f"XP Available: {st.session_state.xp}")

    if len(st.session_state.selected_team) == 0:
        st.warning("No selected team to train.")
    else:
        player_names = [p["name"] for p in st.session_state.selected_team]
        player_name = st.selectbox("Choose Player", player_names)
        stat = st.selectbox("Stat to Boost", ["ovr"])
        cost = 20
        if st.button(f"Train +0.5 {stat} for {cost} XP"):
            if st.session_state.xp >= cost:
                for p in st.session_state.squad:
                    if p["name"] == player_name:
                        p[stat] += 0.5
                        st.session_state.xp -= cost
                        st.success(f"{player_name}'s {stat} improved by 0.5!")
                        break
            else:
                st.error("Not enough XP!")

elif tab == "Store":
    st.header("Store")
    st.write(f"Coins: {st.session_state.coins}")
    price = 200
    if st.button(f"Buy 5-Player Pack for {price} Coins"):
        if st.session_state.coins >= price:
            st.session_state.coins -= price
            # Pack contains 4 commons (ovr < 80) + 1 rare (ovr >= 80)
            commons = [p for p in players if p["ovr"] < 80]
            rares = [p for p in players if p["ovr"] >= 80]
            pack = random.sample(commons, 4) + random.sample(rares, 1)
            new_count = 0
            for pl in pack:
                if pl not in st.session_state.squad:
                    st.session_state.squad.append(pl)
                    new_count += 1
            st.write("**Pack Contents:**")
            for pl in pack:
                st.markdown(render_player_card(pl), unsafe_allow_html=True)
            st.success(f"Added {new_count} new players to your squad!")
        else:
            st.error("Not enough coins!")
