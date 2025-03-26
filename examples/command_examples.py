from copy import deepcopy

from jsonpath2path.core.transformer import CommandTransformer

# The JSON represents a game character named "WarriorX".
json_data = {
    "character": {
        "name": "WarriorX",
        "race": "Human",
        "class": "Warrior",
        "level": 25,
        "skills": [
            {
                "name": "Sword Slash",
                "damage": 50,
                "cooldown": 3
            },
            {
                "name": "Shield Bash",
                "damage": 30,
                "cooldown": 5
            }
        ],
        "equipment": {
            "weapon": "Great Sword",
            "armor": "Heavy Plate Armor"
        },
        "attributes": {
            "health": 500,
            "mana": 100,
            "strength": 80,
            "defense": 70
        }
    }
}

if __name__ == '__main__':
    transformer = CommandTransformer()
    # ========== Addition ==========
    # Add "agility" with an initial value of 50, and "lucky" with an initial value of 20.
    data = deepcopy(json_data)
    transformer.source(data).by('`[["agility", 50], ["lucky", 20]]` => $.character.attributes').to(data)
    assert data['character']['attributes']['agility'] == 50
    assert data['character']['attributes']['lucky'] == 20

    # ========== Deletion ==========
    # Delete all skills with a cooldown time greater than 4.
    data = deepcopy(json_data)
    transformer.source(data).by('$.character.skills[?(@.cooldown > 4)] ->')
    for skill in data['character']['skills']:
        assert (skill['cooldown'] <= 4)

    # Delete the character's current weapon and armor information.
    data = deepcopy(json_data)
    transformer.source(data).by('$.character.equipment.* ->')
    assert len(data['character']['equipment']) == 0

    # Clear the data
    data = deepcopy(json_data)
    transformer.source(data).by('$ ->')
    assert len(data) == 0

    # ========== Modification ==========
    # Add 5 to all cooldowns.
    data = deepcopy(json_data)
    transformer.source(data).by('$.character.skills[*].cooldown | v_add 5 => $.character.skills[*]').to(data)
    assert data['character']['skills'][0]['cooldown'] == 8
    assert data['character']['skills'][1]['cooldown'] == 10

    # Change the character's race from "Human" to "Elf", reduce strength to 70 and increase mana to 200.
    data = deepcopy(json_data)
    transformer.source(data).by('`[["race", "Elf"]]` -> $.character.race').to(data)
    transformer.source(data).by('`[["strength", 70], ["mana", 200]]` => $.character.attributes').to(data)
    assert data['character']['race'] == 'Elf'
    assert data['character']['attributes']['strength'] == 70
    assert data['character']['attributes']['mana'] == 200

    # Adjust the cooldown times of all skills with a cooldown time less than 10 to 10 uniformly.
    data = deepcopy(json_data)
    transformer.source(data).by('@$.character.skills[?(@.cooldown < 10)].cooldown | v_set 10 -> $.character.skills[?(@.cooldown < 10)].cooldown').to(data)
    for skill in data['character']['skills']:
        assert (skill['cooldown'] >= 10)
