import pandas as pd
import json

def build_cards(input_csv, output_json):
    df = pd.read_csv(input_csv)
    players = []

    for _, row in df.iterrows():
        try:
            name = row['Player']
            games = int(row['GM'])
            if games < 10: continue  # Ignore partial seasons

            goals = float(row['GL']) / games
            tackles = float(row['TK']) / games
            hitouts = float(row['HO']) / games if 'HO' in row else 0
            clearances = float(row['CL']) / games if 'CL' in row else 0
            disposals = float(row['DI']) / games if 'DI' in row else 0
            one_percenters = float(row['1%']) / games if '1%' in row else 0
            rebound50s = float(row['R50']) / games if 'R50' in row else 0
            marks = float(row['M']) / games if 'M' in row else 0

            # Determine position
            if hitouts >= 10:
                position = "Ruck"
            elif goals > 2.5 and marks >= 5:
                position = "Tall Forward"
            elif 0.5 <= goals <= 2.0 and tackles >= 2:
                position = "Small Forward"
            elif clearances >= 4:
                position = "Inside Mid"
            elif disposals >= 15 and tackles >= 2:
                position = "Outside Mid"
            elif goals < 0.3 and tackles >= 2 and (one_percenters >= 1 or rebound50s >= 2):
                position = "Small Defender"
            elif marks >= 5 and one_percenters >= 2:
                position = "Tall Defender"
            else:
                position = "Outside Mid"

            players.append({
                "name": name,
                "year": 2024,
                "games": games,
                "position": position,
                "goals": goals,
                "tackles": tackles,
                "hitouts": hitouts,
                "clearances": clearances,
                "disposals": disposals,
                "one_percenters": one_percenters,
                "rebound50s": rebound50s,
                "marks": marks
            })

        except Exception as e:
            print(f"Error with player {row}: {e}")

    with open(output_json, "w") as f:
        json.dump(players, f, indent=4)

    print(f"Saved {len(players)} cards to {output_json}")

if __name__ == "__main__":
    build_cards("afl_2024_stats.csv", "cards.json")
