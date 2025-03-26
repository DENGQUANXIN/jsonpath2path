from copy import deepcopy

from jsonpath2path.common.constants import AssignType, PickType
from jsonpath2path.examples.example_data import game_character
from jsonpath2path.core.transformer import JsonTransformer

if __name__ == '__main__':
    # Create a JSON transformer
    transformer = JsonTransformer()

    # ========== Addition ==========
    # Add "agility" with an initial value of 50, and "lucky" with an initial value of 20.
    data = deepcopy(game_character)
    (transformer.source([["agility", 50], ["lucky", 20]]) # Set source data
                .pick(pick_type=PickType.CREATE) # Create edge and node by given data
                .assign("$.character.attributes", AssignType.MOUNT) # Set slot JSONPath and assign type
                .to(data)) # Transform to target json data
    assert data['character']['attributes']['agility'] == 50
    assert data['character']['attributes']['lucky'] == 20

    # ========== Deletion ==========
    # Delete all skills with a cooldown time greater than 4.
    data = deepcopy(game_character)
    (transformer.source(data)
                .pick("$.character.skills[?(@.cooldown > 4)]", PickType.PLUCK))
    for skill in data['character']['skills']:
        assert (skill['cooldown'] <= 4)

    # Delete the character's current weapon and armor information.
    data = deepcopy(game_character)
    (transformer.source(data)
                .pick("$.character.equipment.*", PickType.PLUCK))
    assert len(data['character']['equipment']) == 0

    # Clear the data
    data = deepcopy(game_character)
    transformer.source(data).pick("$", PickType.PLUCK)
    assert len(data) == 0

    # ========== Modification ==========
    # Add 5 to all cooldowns.
    data = deepcopy(game_character)
    (transformer.source(data)
                .pick("$.character.skills[*].cooldown", PickType.PLUCK)
                .v_map(lambda v: v+5)
                .assign("$.character.skills[*]", AssignType.MOUNT)
                .to(data))
    assert data['character']['skills'][0]['cooldown'] == 8
    assert data['character']['skills'][1]['cooldown'] == 10

    # Change the character's race from "Human" to "Elf", reduce strength to 70 and increase mana to 200.
    data = deepcopy(game_character)
    (transformer.source([["race", "Elf"]])
                .pick(pick_type=PickType.CREATE)
                .assign("$.character.race", AssignType.OCCUPY)
                .to(data))
    (transformer.source([["strength", 70], ["mana", 200]])
                .pick(pick_type=PickType.CREATE)
                .assign("$.character.attributes", AssignType.MOUNT)
                .to(data))
    assert data['character']['race'] == 'Elf'
    assert data['character']['attributes']['strength'] == 70
    assert data['character']['attributes']['mana'] == 200

    # Adjust the cooldown times of all skills with a cooldown time less than 10 to 10 uniformly.
    data = deepcopy(game_character)
    (transformer.source(data)
                .pick("$.character.skills[?(@.cooldown < 10)].cooldown")
                .v_map(lambda v: 10)
                .assign("$.character.skills[?(@.cooldown < 10)].cooldown", AssignType.OCCUPY)
                .to(data))
    for skill in data['character']['skills']:
        assert (skill['cooldown'] >= 10)

    # ========== Another Target JSON Data ==========
    # Move skills to a new JSON
    data = deepcopy(game_character)
    to_data = {}
    (transformer.source(data)
                .pick("$.character.skills", PickType.PLUCK)
                .assign("$", AssignType.MOUNT)
                .to(to_data))
    assert "skills" not in data['character']
    assert len(to_data["skills"]) == 2

    # Copy attributes to a new JSON
    data = deepcopy(game_character)
    to_data = {}
    (transformer.source(data)
                .pick("$.character.attributes", PickType.COPY)
                .assign("$", AssignType.MOUNT)
                .to(to_data))
    assert "attributes" in data['character']
    assert len(to_data["attributes"]) == 4
