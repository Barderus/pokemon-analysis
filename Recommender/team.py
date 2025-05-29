import random

# Define type weaknesses
type_weaknesses = {
    "Grass": ["Fire", "Ice", "Poison", "Flying", "Bug"],
    "Fire": ["Water", "Ground", "Rock"],
    "Water": ["Electric", "Grass"],
    "Electric": ["Ground"],
    "Flying": ["Electric", "Ice", "Rock"],
    "Poison": ["Psychic", "Ground"],
    "Bug": ["Fire", "Flying", "Rock"],
    "Psychic": ["Bug", "Ghost", "Dark"],
    "Rock": ["Water", "Grass", "Fighting", "Steel", "Ground"],
    "Ground": ["Water", "Ice", "Grass"],
    "Ice": ["Fire", "Fighting", "Rock", "Steel"],
    "Fighting": ["Psychic", "Flying", "Fairy"],
    "Dragon": ["Ice", "Dragon", "Fairy"],
    "Dark": ["Bug", "Fighting", "Fairy"],
    "Steel": ["Fire", "Fighting", "Ground"],
    "Fairy": ["Poison", "Steel"],
}

# Define counters for those weaknesses
counter_map = {
    "Fire": ["Water", "Rock", "Dragon"],
    "Water": ["Grass", "Electric"],
    "Ice": ["Fire", "Steel", "Fighting"],
    "Electric": ["Ground", "Grass"],
    "Poison": ["Psychic", "Steel"],
    "Flying": ["Electric", "Rock", "Steel"],
    "Bug": ["Fire", "Flying", "Rock"],
    "Psychic": ["Dark", "Steel"],
    "Rock": ["Steel", "Fighting", "Ground"],
    "Ground": ["Water", "Grass", "Ice"],
    "Fighting": ["Fairy", "Flying", "Psychic"],
    "Ghost": ["Dark"],
    "Dark": ["Fairy", "Fighting", "Bug"],
    "Steel": ["Fire", "Fighting", "Ground"],
    "Fairy": ["Poison", "Steel"],
}


def find_counter_types(starter_type):
    weaknesses = type_weaknesses.get(starter_type, [])
    counter_types = set()
    for weakness in weaknesses:
        counter_types.update(counter_map.get(weakness, []))
    return list(counter_types)


def select_team_members(starter, df, legendary_df):
    team = [starter]
    used_names = {starter["Name"]}
    used_types = {starter["Type 1"]}
    roles_needed = {"Tank", "Speedster", "DPS", "Special Tank", "Wall"}
    roles_needed.discard(starter["Role"])

    starter_type = starter["Type 1"]
    counter_types = find_counter_types(starter_type)

    def pick(role, pool, top_n=5):
        candidates = pool[
            (pool["Role"] == role) &
            (~pool["Name"].isin(used_names)) &
            (~pool["Type 1"].isin(used_types))
            ].copy()

        if not candidates.empty:
            candidates["priority"] = candidates["Type 1"].apply(lambda t: 1 if t in counter_types else 0)
            top_candidates = candidates.sort_values(by=["priority", "Total"], ascending=[False, False]).head(top_n)
            chosen = top_candidates.sample(1).iloc[0]
            used_names.add(chosen["Name"])
            used_types.add(chosen["Type 1"])
            return chosen
        return None

    non_legendaries = df[df["Category"].str.lower() != "legendary"]

    for role in roles_needed:
        mon = pick(role, non_legendaries)
        if mon is not None:
            team.append(mon)

    # Add one legendary, if any Type 1 is still unused
    available_legends = legendary_df[
        (~legendary_df["Name"].isin(used_names)) &
        (~legendary_df["Type 1"].isin(used_types))
        ]
    if not available_legends.empty:
        chosen = available_legends.sort_values(by="Total", ascending=False).iloc[0]
        team.append(chosen)

    return team
