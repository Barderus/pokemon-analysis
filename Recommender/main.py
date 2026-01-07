import pandas as pd
from team import select_team_members, generate_teams
from stats import analyze_team_stats
from roles import calculate_thresholds, assign_single_role

# Load dataset and assign a single role per Pokémon using computed thresholds
df = pd.read_csv("../data/preprocessed/pokemon_preprocessed.csv")
thresholds = calculate_thresholds(df)
df["role"] = df.apply(assign_single_role, axis=1, thresholds=thresholds)

def get_starter_list():
    return {
        "Kanto": ["Bulbasaur", "Charmander", "Squirtle"],
        "Johto": ["Chikorita", "Cyndaquil", "Totodile"],
        "Hoenn": ["Treecko", "Torchic", "Mudkip"],
        "Sinnoh": ["Turtwig", "Chimchar", "Piplup"],
        "Unova": ["Snivy", "Tepig", "Oshawott"],
        "Kalos": ["Chespin", "Fennekin", "Froakie"],
        "Alola": ["Rowlet", "Litten", "Popplio"]
    }

starter_dict = get_starter_list()

all_starters = [s for gen in starter_dict.values() for s in gen]

while True:
    print("\nChoose your starter from this list (or enter 0 to quit):")
    for gen, starters in starter_dict.items():
        print(f"{gen}: {', '.join(starters)}")

    raw_input_name = input("> ").strip()

    if raw_input_name == "0":
        break

    # Match starter ignoring capitalization
    matches = [s for s in all_starters if s.lower() == raw_input_name.lower()]
    if not matches:
        print(f"'{raw_input_name}' is not a valid starter. Please try again.")
        continue

    starter_name = matches[0]

    # Pull the selected starter row from the dataset
    starter_rows = df[df["name"].str.lower() == starter_name.lower()]
    if starter_rows.empty:
        print(f"Starter '{starter_name}' not found in dataset.")
        continue

    starter = starter_rows.iloc[0]

    # Build multiple team variants around the chosen starter
    teams = generate_teams(starter, df, n_teams=3, team_size_target=6)

    for i, team in enumerate(teams, 1):
        team_df = pd.DataFrame(team)
        print(f"\n=== Recommended Team #{i} ===\n")
        print(team_df[["name", "type1", "role"]])
        analyze_team_stats(team_df, df)

    if input("\nSave this team to CSV? (y/n): ").strip().lower() == "y":
        team_df.to_csv(f"team_{starter_name.lower()}.csv", index=False)
