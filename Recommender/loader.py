import pandas as pd

def load_all_data():
    df = pd.read_csv("../all_pokemon.csv")
    starter_df = pd.read_csv("../starter_pokemon.csv")
    legendary_df = pd.read_csv("../legendary_pokemon.csv")
    return df, starter_df, legendary_df

def get_starter_list():
    return {
        "Kanto": ["Bulbasaur", "Charmander", "Squirtle"],
        "Johto": ["Chikorita", "Cyndaquil", "Totodile"],
        "Hoenn": ["Treecko", "Torchic", "Mudkip"],
        "Sinnoh": ["Turtwig", "Chimchar", "Piplup"],
        "Unova": ["Snivy", "Tepig", "Oshawott"],
        "Kalos": ["Chespin", "Fennekin", "Froakie"],
        "Alola": ["Rowlet", "Litten", "Popplio"],
        "Galar": ["Grookey", "Scorbunny", "Sobble"],
        "Paldea": ["Sprigatito", "Fuecoco", "Quaxly"]
    }

