import requests
import random
import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Style
from ttkbootstrap.widgets import Label, Frame, Button, Entry
from PIL import Image, ImageTk
from io import BytesIO

TYPE_COLORS = {
    "normal": "#A8A878",
    "fire": "#F08030",
    "water": "#6890F0",
    "electric": "#F8D030",
    "grass": "#78C850",
    "ice": "#98D8D8",
    "fighting": "#C03028",
    "poison": "#A040A0",
    "ground": "#E0C068",
    "flying": "#A890F0",
    "psychic": "#F85888",
    "bug": "#A8B820",
    "rock": "#B8A038",
    "ghost": "#705898",
    "dragon": "#7038F8",
    "dark": "#705848",
    "steel": "#B8B8D0",
    "fairy": "#EE99AC"
}

def get_pokemon_info(pokemon_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        types = [t['type']['name'] for t in data['types']]
        stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
        sprite_url = data['sprites']['front_default']
        return {"types": types, "stats": stats, "sprite_url": sprite_url}
    else:
        return None

def get_effective_types(enemy_types):
    effective_types = set()
    for etype in enemy_types:
        type_url = f"https://pokeapi.co/api/v2/type/{etype}"
        response = requests.get(type_url)
        if response.status_code == 200:
            data = response.json()
            for damage_relation in data['damage_relations']['double_damage_from']:
                effective_types.add(damage_relation['name'])
    return list(effective_types)

def get_moves_by_type(type_name):
    url = f"https://pokeapi.co/api/v2/type/{type_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        moves = [move['name'] for move in data['moves']]
        return moves
    else:
        return []

def get_recommended_pokemon(effective_types, limit=4):
    recommended_pokemon = []
    for etype in effective_types:
        type_url = f"https://pokeapi.co/api/v2/type/{etype}"
        response = requests.get(type_url)
        if response.status_code == 200:
            data = response.json()
            pokemon_of_type = [pokemon['pokemon']['name'] for pokemon in data['pokemon']]
            recommended_pokemon.extend(pokemon_of_type)

    recommended_pokemon = list(set(recommended_pokemon))
    random.shuffle(recommended_pokemon)
    recommended_pokemon = recommended_pokemon[:limit]
    
    pokemon_data = []
    for pokemon_name in recommended_pokemon:
        pokemon_info = get_pokemon_info(pokemon_name)
        if pokemon_info:
            pokemon_data.append({"name": pokemon_name, "types": pokemon_info["types"], "stats": pokemon_info["stats"], "sprite_url": pokemon_info["sprite_url"]})
    
    return pokemon_data

def display_sprite(url, label):
    response = requests.get(url)
    img_data = Image.open(BytesIO(response.content))
    img_data = img_data.resize((80, 80), Image.LANCZOS)
    img = ImageTk.PhotoImage(img_data)
    label.config(image=img)
    label.image = img

def create_type_label(frame, type_name):
    color = TYPE_COLORS.get(type_name, "#FFFFFF")
    label = Label(frame, text=type_name.capitalize(), font=("Arial", 10, "bold"), padding=(5, 2), bootstyle="primary")
    label.configure(background=color, foreground="white")
    label.pack(side="left", padx=2)

def display_battle_helper():
    enemy_pokemon = pokemon_entry.get()
    if not enemy_pokemon:
        messagebox.showwarning("Advertencia", "Por favor ingrese un nombre de Pokémon.")
        return

    result = battle_helper(enemy_pokemon)
    if result is None:
        return
    
    results_frame.pack(fill="both", padx=10, pady=10)

    for widget in enemy_types_container.winfo_children():
        widget.destroy()
    for widget in counter_types_container.winfo_children():
        widget.destroy()

    moves_value.config(text=", ".join(result['recommended_moves'][:10]))

    if result['enemy_sprite']:
        display_sprite(result['enemy_sprite'], enemy_sprite_label)
    
    for t in result['enemy_types']:
        create_type_label(enemy_types_container, t)
    
    for t in result['effective_types']:
        create_type_label(counter_types_container, t)

    for widget in recommended_pokemon_frame.winfo_children():
        widget.destroy()

    for pokemon in result['recommended_pokemon']:
        frame = Frame(recommended_pokemon_frame, padding=10, relief="solid", borderwidth=1)
        frame.pack(fill="x", padx=10, pady=5)

        pokemon_label = Label(frame, text=pokemon['name'].capitalize(), font=("Arial", 12, "bold"), bootstyle="inverse")
        pokemon_label.pack(anchor="w", padx=5)

        sprite_label = Label(frame)
        sprite_label.pack(side="left", padx=5)
        display_sprite(pokemon["sprite_url"], sprite_label)

        types_frame = Frame(frame)
        types_frame.pack(anchor="w", padx=5)
        for t in pokemon['types']:
            create_type_label(types_frame, t)

        stats = ", ".join([f"{k}: {v}" for k, v in pokemon["stats"].items()])
        stats_label = Label(frame, text="Stats: " + stats, font=("Arial", 10))
        stats_label.pack(anchor="w", padx=5)

def battle_helper(enemy_pokemon):
    enemy_info = get_pokemon_info(enemy_pokemon)
    if enemy_info is None:
        messagebox.showerror("Error", f"No se pudo encontrar el Pokémon '{enemy_pokemon}'.")
        return None

    enemy_types = enemy_info['types']
    effective_types = get_effective_types(enemy_types)
    
    recommended_moves = []
    for etype in effective_types:
        moves = get_moves_by_type(etype)
        recommended_moves.extend(moves)

    recommended_pokemon = get_recommended_pokemon(effective_types)
    
    return {
        "enemy_types": enemy_types,
        "effective_types": effective_types,
        "recommended_moves": recommended_moves,
        "recommended_pokemon": recommended_pokemon,
        "enemy_sprite": enemy_info['sprite_url']
    }

style = Style(theme="litera")
root = style.master
root.title("Battle Helper - Pokémon")
root.geometry("850x900")
root.iconbitmap("./sources/icon.ico")  
root.config(padx=10, pady=10)

title_label = Label(root, text="Battle Helper", font=("Arial", 24, "bold"), bootstyle="dark", anchor="w")
title_label.pack(anchor="w", padx=10, pady=(10, 0))

search_frame = Frame(root)
search_frame.pack(fill="x", padx=10, pady=(5, 10))

pokemon_entry = Entry(search_frame, font=("Arial", 12))
pokemon_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

search_button = Button(search_frame, text="Buscar", command=display_battle_helper, bootstyle="success", style="Custom.TButton")
search_button.pack(side="left")

results_frame = Frame(root, bootstyle="light", padding=10, relief="solid", borderwidth=2)
results_frame.pack_forget() 

enemy_sprite_label = Label(results_frame)
enemy_sprite_label.grid(row=0, column=0, rowspan=3, padx=10, pady=5)

enemy_types_label = Label(results_frame, text="Tipos del Pokémon:", font=("Arial", 12, "bold"))
enemy_types_label.grid(row=0, column=1, sticky="w")
enemy_types_container = Frame(results_frame)
enemy_types_container.grid(row=0, column=2, sticky="w")

counter_types_label = Label(results_frame, text="Tipos recomendados para counter:", font=("Arial", 12, "bold"))
counter_types_label.grid(row=1, column=1, sticky="w")
counter_types_container = Frame(results_frame)
counter_types_container.grid(row=1, column=2, sticky="w")

moves_label = Label(results_frame, text="Movimientos recomendados:", font=("Arial", 12, "bold"))
moves_label.grid(row=2, column=1, sticky="w")
moves_value = Label(results_frame, font=("Arial", 12), wraplength=400, justify="left")
moves_value.grid(row=2, column=2, sticky="w")

recommended_pokemon_label = Label(root, text="Pokémon recomendados:", font=("Arial", 16, "bold"), bootstyle="dark")
recommended_pokemon_label.pack(anchor="w", padx=10)

recommended_pokemon_frame = Frame(root)
recommended_pokemon_frame.pack(fill="both", expand=True, padx=10, pady=5)

footer_label = Label(root, text="Battle Helper - Pokémon | Versión 1.0 | © 2024", font=("Arial", 10), bootstyle="dark", anchor="center")
footer_label.pack(side="bottom", fill="x", pady=5)

root.mainloop()
