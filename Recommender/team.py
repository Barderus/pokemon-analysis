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

ENEMY_OFFENSE_WEIGHT = 20.0   # prefer types that enemy is weak to
ENEMY_DEFENSE_WEIGHT = 12.0   # avoid types that enemy will hit super effectively
# Add extra weights to stop the rec system from just picking the strongest pokemon (smart-pants)
TEAM_COVERAGE_WEIGHT = 50
TEAM_COVERAGE_WEIGHT_VS_ENEMY = 10


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

def enemy_attack_types(enemy_team_df):
    """
    Enemy offensive "threat types" approximated by their type1/type2.
    """
    types = set()
    for _, r in enemy_team_df.iterrows():
        t1, t2 = r.get("type1"), r.get("type2")
        if pd.notna(t1):
            types.add(str(t1).lower())
        if pd.notna(t2):
            types.add(str(t2).lower())
    return list(types)

def build_enemy_profiles(enemy_team_df, against_cols):
    """
    Returns:
      - enemy_weakness_profile: mean of enemy against_* (higher = they take more damage)
      - enemy_attack_type_list: enemy types to defend against
    """
    # Mean damage enemy takes from each attacking type
    enemy_weakness_profile = enemy_team_df[against_cols].mean()

    # Types enemy likely attacks with (approx via their typing)
    enemy_types = enemy_attack_types(enemy_team_df)

    return enemy_weakness_profile, enemy_types

def build_one_team(starter, df, team_size_target=6, top_n=12, non_legendaries=None, enemy_team_df=None):
    against_cols = get_against_cols(df)

    # Restrict candidate pool to non-legendary Pokémon
    if non_legendaries is None:
        non_legendaries = df.copy()
        if "is_legendary" in non_legendaries.columns:
            non_legendaries = non_legendaries[non_legendaries["is_legendary"] != 1]

    if "base_total" in non_legendaries.columns and pd.notna(starter.get("base_total")):
        power_cap = starter["base_total"] + 150
        non_legendaries = non_legendaries[non_legendaries["base_total"] <= power_cap]


    enemy_profile = None
    enemy_types = []
    if enemy_team_df is not None and not enemy_team_df.empty and against_cols:
        enemy_profile, enemy_types = build_enemy_profiles(enemy_team_df, against_cols)

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

    def enemy_offense_bonus(row):
        """
        Bonus if candidate's type(s) hit enemy weaknesses.
        Uses enemy's against_type multipliers directly (higher = better for us).
        """
        if enemy_profile is None:
            return 0

        best = 1.0
        for t in [row.get("type1"), row.get("type2")]:
            if pd.notna(t):
                col = "against_" + str(t).lower()
                if col in enemy_profile.index:
                    best = max(best, float(enemy_profile[col]))

        return best - 1.0

        # Center at 1.0 so neutral = 0 bonus; super-effective > 0; resisted < 0
        return best - 1.0

    def enemy_defense_penalty(row):
        """
        Penalty if candidate takes high damage from enemy types (their likely attacks).
        Uses candidate against_enemy_type columns (higher = worse for us).
        """
        if not enemy_types or not use_matchups:
            return 0

        vals = []
        for t in enemy_types:
            col = "against_" + str(t).lower()
            if col in row.index and pd.notna(row[col]):
                vals.append(float(row[col]))

        if not vals:
            return 0

        return (sum(vals) / len(vals)) - 1.0

    def score_candidate(row, role=None):
        score = compute_role_score(row, role) if role else general_score(row)

        # Reward candidates that reduce the team’s worst matchup and add coverage weight to avoid the system from picking the strongest pokemon
        if use_matchups:
            new_means = update_means(team_means, row)
            coverage_w = TEAM_COVERAGE_WEIGHT_VS_ENEMY if enemy_team_df is not None else TEAM_COVERAGE_WEIGHT
            score += (current_worst - new_means.max()) * coverage_w

        # Small bonus for introducing a new secondary type
        t2 = row.get("type2")
        if pd.notna(t2) and t2 not in used_types:
            score += 2

        # Enemy-aware scoring (if enemy team provided)
        score += ENEMY_OFFENSE_WEIGHT * enemy_offense_bonus(row)
        score -= ENEMY_DEFENSE_WEIGHT * enemy_defense_penalty(row)

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

def generate_teams(starter, df, n_teams=3, team_size_target=6, enemy_team_df=None):
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
            enemy_team_df=enemy_team_df,
        )
        if len(team) != team_size_target:
            continue

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
