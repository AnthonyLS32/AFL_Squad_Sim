elif tab == "Selected Team":
    st.title("Select Your Team")
    st.write("Build your 17 + Bench squad. Position limits apply:")

    # Count current picks by position line
    line_counts = {
        "Forward": sum(1 for p in st.session_state['selected_team'] if p['line'] == "Forward"),
        "Mid": sum(1 for p in st.session_state['selected_team'] if p['line'] == "Mid"),
        "Ruck": sum(1 for p in st.session_state['selected_team'] if p['line'] == "Ruck"),
        "Back": sum(1 for p in st.session_state['selected_team'] if p['line'] == "Back"),
        "Bench": sum(1 for p in st.session_state['selected_team'] if p['line'] == "Bench")
    }

    st.write(
        f"**Forwards:** {line_counts['Forward']} / 4 | "
        f"**Mids:** {line_counts['Mid']} / 4 | "
        f"**Rucks:** {line_counts['Ruck']} / 2 | "
        f"**Backs:** {line_counts['Back']} / 4 | "
        f"**Bench:** {line_counts['Bench']} / 3"
    )

    available_names = [p['name'] for p in st.session_state['squad'] if p not in st.session_state['selected_team']]
    selected_name = st.selectbox(
        "Select a player to add to your team:", available_names
    )

    if st.button("Add Player"):
        player = next(p for p in st.session_state['squad'] if p['name'] == selected_name)
        player_line = player['line']

        # If line is not one of the main four, default to Bench
        if player_line not in ["Forward", "Mid", "Ruck", "Back"]:
            player_line = "Bench"

        max_per_line = {"Forward": 4, "Mid": 4, "Ruck": 2, "Back": 4, "Bench": 3}

        if line_counts[player_line] >= max_per_line[player_line]:
            st.warning(f"⚠️ Cannot add: Max {player_line}s reached!")
        else:
            st.session_state['selected_team'].append(player)
            st.success(f"✅ Added {player['name']} ({player_line})")
            line_counts[player_line] += 1

    st.subheader("Selected Team")
    for p in st.session_state['selected_team']:
        st.write(
            f"{p['name']} | {p['year']} | {p['line']} | OVR: {p['ovr']}"
        )
