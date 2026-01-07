import pandas as pd

# Role weights define what "good" means for each team role. Each role rewards the stats it cares about and penalizes the ones it doesn’t.
# Example:
#   - DPS favors offense and speed, but avoids fragile or hard-to-use Pokémon
#   - Tanks and Walls heavily favor bulk and low damage taken
#   - Speedsters favor speed and pressure, not raw durability
ROLE_WEIGHTS = {
    "DPS": {
        "offense_score": 1.0,
        "base_total": 0.25,
        "avg_damage_taken": -0.6,
        "difficulty_score": -0.25,
    },
    "Tank": {
        "bulk_score": 1.0,
        "avg_damage_taken": -1.0,
        "base_total": 0.15,
        "difficulty_score": -0.20,
    },
    "Wall": {
        "bulk_score": 1.2,
        "avg_damage_taken": -1.3,
        "base_total": 0.10,
        "difficulty_score": -0.20,
    },
    "Speedster": {
        "speed": 0.7,
        "offense_score": 0.6,
        "avg_damage_taken": -0.4,
        "difficulty_score": -0.20,
    },
}

def get_against_cols(df):
    # Type matchup multipliers (ex: against_fire, against_water, etc.)
    return [c for c in df.columns if c.startswith("against_")]

def compute_role_score(row, role):
    # Weighted score to a specific team role
    score = 0
    for col, w in ROLE_WEIGHTS.get(role, {}).items():
        if pd.notna(row.get(col)):
            score += w * row[col]
    return score

# Scoring works in two modes:
# 1) Role-based scoring when filling a specific missing role
# 2) General scoring when filling flexible slots
# - Role-based scoring enforces team structure.
# - General scoring favors well-rounded Pokémon.
def general_score(row):
    score = 0
    if pd.notna(row.get("base_total")):
        score += 0.25 * row["base_total"]
    if pd.notna(row.get("offense_score")):
        score += 0.7 * row["offense_score"]
    if pd.notna(row.get("bulk_score")):
        score += 0.7 * row["bulk_score"]

    score -= 0.25 * row.get("difficulty_score", 0)
    score -= 0.6 * row.get("avg_damage_taken", 0)
    return score

def build_one_team(starter, df, team_size_target=6, top_n=12, non_legendaries=None):
    against_cols = get_against_cols(df)

    # Restrict candidate pool to non-legendary Pokémon
    if non_legendaries is None:
        non_legendaries = df.copy()
        if "is_legendary" in non_legendaries.columns:
            non_legendaries = non_legendaries[non_legendaries["is_legendary"] != 1]

    team = [starter]
    used_names = {starter["name"]}

    # Track used typing to ensure type diversity
    used_types = set()
    for t in [starter.get("type1"), starter.get("type2")]:
        if pd.notna(t):
            used_types.add(t)

    use_matchups = bool(against_cols)

    # Initialize team-wide matchup profile from starter
    if use_matchups:
        team_means = starter[against_cols].astype(float)
        current_worst = team_means.max()
    else:
        team_means = None
        current_worst = None

    running_n = 1

    def update_means(current_means, row):
        # Incremental mean update to avoid recomputing from scratch
        row_vals = row[against_cols]
        return (current_means * running_n + row_vals) / (running_n + 1)

    def score_candidate(row, role=None):
        score = compute_role_score(row, role) if role else general_score(row)

        # Reward candidates that reduce the team’s worst matchup
        if use_matchups:
            new_means = update_means(team_means, row)
            score += (current_worst - new_means.max()) * 50

        # Small bonus for introducing a new secondary type
        t2 = row.get("type2")
        if pd.notna(t2) and t2 not in used_types:
            score += 2

        return score

    def pick(candidates, role=None):
        nonlocal team_means, current_worst, running_n

        if candidates.empty:
            return None

        candidates = candidates.copy()
        candidates["score"] = candidates.apply(lambda r: score_candidate(r, role), axis=1)

        # Sample from top-N to preserve diversity across runs
        top = candidates.sort_values("score", ascending=False).head(top_n)
        chosen = top.sample(1).iloc[0]

        used_names.add(chosen["name"])
        for t in [chosen.get("type1"), chosen.get("type2")]:
            if pd.notna(t):
                used_types.add(t)

        if use_matchups:
            team_means = update_means(team_means, chosen)
            running_n += 1
            current_worst = team_means.max()
        else:
            running_n += 1

        return chosen

    roles_needed = ["Tank", "Speedster", "DPS", "Wall"]
    if starter.get("role") in roles_needed:
        roles_needed.remove(starter["role"])

    for role in roles_needed:
        # Tier 1: enforce role match
        role_pool = non_legendaries[
            (non_legendaries["role"] == role)
            & (~non_legendaries["name"].isin(used_names))
            ]
        chosen = pick(role_pool, role=role)

        # Tier 2: fallback to any available Pokémon
        if chosen is None:
            fallback_pool = non_legendaries[~non_legendaries["name"].isin(used_names)]
            chosen = pick(fallback_pool, role=None)

        if chosen is not None:
            team.append(chosen)

    # Fill remaining slots without role constraints
    while len(team) < team_size_target:
        pool = non_legendaries[~non_legendaries["name"].isin(used_names)]
        chosen = pick(pool, role=None)
        if chosen is None:
            break
        team.append(chosen)

    return team

def generate_teams(starter, df, n_teams=3, team_size_target=6):
    teams = []
    seen = set()

    # Pre-filter non-legendaries once for reuse
    non_legendaries = df.copy()
    if "is_legendary" in non_legendaries.columns:
        non_legendaries = non_legendaries[non_legendaries["is_legendary"] != 1]

    attempts = 0
    while len(teams) < n_teams and attempts < 30:
        attempts += 1
        team = build_one_team(
            starter,
            df,
            team_size_target=team_size_target,
            non_legendaries=non_legendaries,
        )

        # Signature prevents duplicate team compositions
        sig = tuple(sorted([p["name"] for p in team]))
        if sig in seen:
            continue

        seen.add(sig)
        teams.append(team)

    return teams

def select_team_members(starter, df):
    # wrapper for a single team build
    return build_one_team(starter, df, team_size_target=6)
