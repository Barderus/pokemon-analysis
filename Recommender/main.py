import pandas as pd
from loader import load_all_data, get_starter_list
from team import select_team_members
from stats import analyze_team_stats

# Load data
df, starter_df, legendary_df = load_all_data()

# Remove Mythicals
mythical_names = [
    "Mew", "Celebi", "Jirachi", "Manaphy", "Darkrai", "Shaymin", "Arceus",
    "Victini", "Keldeo", "Meloetta", "Genesect", "Diancie", "Hoopa", "Volcanion",
    "Magearna", "Marshadow", "Zeraora", "Meltan", "Melmetal", "Zarude"
]
df = df[~df["Name"].isin(mythical_names)]
starter_df = starter_df[~starter_df["Name"].isin(mythical_names)]
legendary_df = df[df["Category"].str.lower() == "legendary"]

starter_dict = get_starter_list()
all_starters = [name for gen in starter_dict.values() for name in gen]

while True:
    print("\nChoose your starter from this list (or enter 0 to quit):")
    for gen, starters in starter_dict.items():
        print(f"{gen}: {', '.join(starters)}")

    starter_name = input("> ").strip().title()

    if starter_name == "0":
        print("Exiting the team builder. Goodbye!")
        break

    if starter_name not in all_starters:
        print(f"'{starter_name}' is not a valid starter. Please try again.")
        continue

    starter = starter_df[starter_df["Name"] == starter_name].iloc[0]

    team = select_team_members(starter, df, legendary_df)
    team_df = pd.DataFrame(team)

    print("\nYour Recommended Team:")
    print(team_df[["Name", "Type 1", "Type 2", "Role", "Total"]])

    print("\n Team Stat Analysis:\n")
    analyze_team_stats(team_df, df)

    save_choice = input("\n Would you like to save this team to a CSV file? (y/n): ").strip().lower()
    if save_choice == "y":
        filename = f"team_{starter_name.lower()}.csv"
        team_df.to_csv(filename, index=False)
        print(f" Team saved as '{filename}'")
