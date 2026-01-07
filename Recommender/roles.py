def calculate_thresholds(df):
    return {
        "attack": df["attack"].median(),
        "sp_attack": df["sp_attack"].median(),
        "hp": df["hp"].median(),
        "defense": df["defense"].median(),
        "sp_defense": df["sp_defense"].median(),
        "speed": df["speed"].median(),
        "offense_score": df["offense_score"].median(),
        "bulk_score": df["bulk_score"].median(),
        "avg_damage_taken": df["avg_damage_taken"].median(),
    }

def assign_single_role(row, thresholds):
    atk = row["attack"]
    sp_atk = row["sp_attack"]
    speed = row["speed"]

    offense = row["offense_score"]
    bulk = row["bulk_score"]
    avg_dmg = row["avg_damage_taken"]

    # WALL: extremely bulky, low damage taken
    if bulk >= thresholds["bulk_score"] and avg_dmg <= thresholds["avg_damage_taken"]:
        return "Wall"

    # TANK: bulky but not a full wall
    if bulk >= thresholds["bulk_score"]:
        return "Tank"

    # SPEEDSTER: fast + decent offense
    if speed >= thresholds["speed"] and offense >= thresholds["offense_score"]:
        return "Speedster"

    # DPS: high offensive output (physical or special)
    if offense >= thresholds["offense_score"]:
        return "DPS"

    # FALLBACKS (keeps everything classified)
    if atk >= thresholds["attack"] or sp_atk >= thresholds["sp_attack"]:
        return "DPS"

    return "Unclassified"
