from discord_slash.utils.manage_commands import create_choice


choices_mode = [
    create_choice(
        name="Everything (Default)",
        value="0"
    ),
    create_choice(
        name="Raids",
        value="4"
    ),
    create_choice(
        name="Dungeon",
        value="82"
    ),
    create_choice(
        name="Story (including stuff like Presage)",
        value="2"
    ),
    create_choice(
        name="Strike",
        value="3"
    ),
    create_choice(
        name="Nightfall",
        value="46"
    ),
    create_choice(
        name="Everything PvE",
        value="7"
    ),
    create_choice(
        name="Trials",
        value="84"
    ),
    create_choice(
        name="Iron Banner",
        value="19"
    ),
    create_choice(
        name="Everything PvP",
        value="5"
    ),
    create_choice(
        name="Gambit",
        value="63"
    ),
]