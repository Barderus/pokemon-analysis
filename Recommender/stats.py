def analyze_team_stats(team_df, global_df):
    stats = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
    avg_stats = team_df[stats].mean()
    median_stats = global_df[stats].median()
    print("\nTeam Stat Averages vs Global Medians:")
    for stat in stats:
        print(f"{stat}: {avg_stats[stat]:.1f} vs median {median_stats[stat]}")
