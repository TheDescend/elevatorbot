from discord_slash.utils.manage_commands import create_choice, create_option

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


options_stat = create_option(
    name="name",
    description="The name of the leaderboard you want to see",
    option_type=3,
    required=True,
    choices=[
        create_choice(
            name="Kills",
            value="kills"
        ),
        create_choice(
            name="Precision Kills",
            value="precisionKills"
        ),
        create_choice(
            name="Assists",
            value="assists"
        ),
        create_choice(
            name="Deaths",
            value="deaths"
        ),
        create_choice(
            name="Suicides",
            value="suicides"
        ),
        create_choice(
            name="KDA",
            value="efficiency"
        ),
        create_choice(
            name="Longest Kill Distance",
            value="longestKillDistance"
        ),
        create_choice(
            name="Average Kill Distance",
            value="averageKillDistance"
        ),
        create_choice(
            name="Total Kill Distance",
            value="totalKillDistance"
        ),
        create_choice(
            name="Longest Kill Spree",
            value="longestKillSpree"
        ),
        create_choice(
            name="Average Lifespan",
            value="averageLifespan"
        ),
        create_choice(
            name="Resurrections Given",
            value="resurrectionsPerformed"
        ),
        create_choice(
            name="Resurrections Received",
            value="resurrectionsReceived"
        ),
        create_choice(
            name="Number of Players Played With",
            value="allParticipantsCount"
        ),
        create_choice(
            name="Longest Single Life (in s)",
            value="longestSingleLife"
        ),
        create_choice(
            name="Orbs of Power Dropped",
            value="orbsDropped"
        ),
        create_choice(
            name="Orbs of Power Gathered",
            value="orbsGathered"
        ),
        create_choice(
            name="Time Played (in s)",
            value="secondsPlayed"
        ),
        create_choice(
            name="Activities Cleared",
            value="activitiesCleared"
        ),
        create_choice(
            name="Public Events Completed",
            value="publicEventsCompleted"
        ),
        create_choice(
            name="Heroic Public Events Completed",
            value="heroicPublicEventsCompleted"
        ),
        create_choice(
            name="Kills with: Super",
            value="weaponKillsSuper"
        ),
        create_choice(
            name="Kills with: Melee",
            value="weaponKillsMelee"
        ),
        create_choice(
            name="Kills with: Grenade",
            value="weaponKillsGrenade"
        ),
        create_choice(
            name="Kills with: Ability",
            value="weaponKillsAbility"
        )
    ]
)


def options_user(flavor_text: str = "The name of the user you want to look up"):
    return create_option(
        name="user",
        description=flavor_text,
        option_type=6,
        required=False
    )
