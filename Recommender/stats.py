def analyze_team_stats(team_df, global_df):
    # Identify type matchup columns (damage multipliers)
    against_cols = [c for c in team_df.columns if c.startswith("against_")]

    # Aggregate team-wide matchup strengths/weaknesses
    if against_cols:
        team_profile = team_df[against_cols].mean().sort_values(ascending=False)

        print("\nWorst Team Matchups (higher = worse):")
        for col, val in team_profile.head(5).items():
            atk_type = col.replace("against_", "")
            print(f"vs {atk_type:<10}: {val:.2f}")
        print()

        print("Best Team Matchups (lower = better):")
        for col, val in team_profile.tail(5).items():
            atk_type = col.replace("against_", "")
            print(f"vs {atk_type:<10}: {val:.2f}")
