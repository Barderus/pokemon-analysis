def calculate_thresholds(df):
    return {
        "Attack": df["Attack"].median(),
        "Sp. Atk": df["Sp. Atk"].median(),
        "HP": df["HP"].median(),
        "Defense": df["Defense"].median(),
        "Sp. Def": df["Sp. Def"].median(),
        "Speed": df["Speed"].median()
    }

def assign_single_role(row, thresholds):
    atk, sp_atk, hp, defense, sp_def, speed = row[["Attack", "Sp. Atk", "HP", "Defense", "Sp. Def", "Speed"]]
    if hp > thresholds["HP"] and (defense > thresholds["Defense"] or sp_def > thresholds["Sp. Def"]):
        return "Wall"
    elif atk > thresholds["Attack"] and sp_atk > thresholds["Sp. Atk"]:
        return "DPS"
    elif sp_atk > thresholds["Sp. Atk"]:
        return "Special DPS"
    elif hp > thresholds["HP"] or defense > thresholds["Defense"]:
        return "Tank"
    elif hp > thresholds["HP"] or sp_def > thresholds["Sp. Def"]:
        return "Special Tank"
    elif speed > thresholds["Speed"]:
        return "Speedster"
    elif atk > thresholds["Attack"] or sp_atk > thresholds["Sp. Atk"]:
        return "DPS 2"
    return "Unclassified"
