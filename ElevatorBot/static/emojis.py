from dis_snek.client import Snake
from dis_snek.models import CustomEmoji


class __ElevatorEmojis:
    """To add an emoji add it to the class variables"""

    # Descend Font
    yes: CustomEmoji | int = 768908985557844028
    question: CustomEmoji | int = 768906489686655016
    enter: CustomEmoji | int = 768906489103384688
    circle: CustomEmoji | int = 768906489464619008

    destiny: CustomEmoji | int = 768906489472876574
    descend_logo: CustomEmoji | int = 768907515193720874
    elevator_logo: CustomEmoji | int = 768907515386921020

    kinetic: CustomEmoji | int = 1  # todo
    stasis: CustomEmoji | int = 897797463799369769
    arc: CustomEmoji | int = 897797463933583401
    solar: CustomEmoji | int = 897797463937798174
    void: CustomEmoji | int = 897797464013307905

    unstoppable: CustomEmoji | int = 897797463807774752
    barrier: CustomEmoji | int = 897797463988142091
    overload: CustomEmoji | int = 897797463988142090

    # todo emotes for the weapon types
    # todo emotes for the ammo types

    # Emote Server
    among_us: CustomEmoji | int = 905844106914332682
    barotrauma: CustomEmoji | int = 905846654316445758
    gta: CustomEmoji | int = 905847049059197009
    valorant: CustomEmoji | int = 905849958601744385
    lol: CustomEmoji | int = 905843726583226449
    eft: CustomEmoji | int = 905846654211620865
    minecraft: CustomEmoji | int = 905846654211620866
    new_world: CustomEmoji | int = 900640805784522762

    warlock: CustomEmoji | int = 830747907488612402
    hunter: CustomEmoji | int = 830747907829006346
    titan: CustomEmoji | int = 830747907576823808
    light_level_icon: CustomEmoji | int = 830750430816108564

    join: CustomEmoji | int = 850000522101391400
    leave: CustomEmoji | int = 850000522048045106
    backup: CustomEmoji | int = 850000522107027466

    # Descend [Test 01]

    # Descend [Test 02]
    thumps_up: CustomEmoji | int = 754946723612196975
    thumps_down: CustomEmoji | int = 754946723503276124

    async def init_emojis(self, client: Snake):
        """Runs on startup to get the emojis we use"""

        emojis = []

        # get all emojis from the emote servers
        for guild_id in [768902336914391070, 724676552175910934, 556418279015448596, 697720309847162921]:
            guild = await client.get_guild(guild_id)
            emojis.extend(await guild.get_all_custom_emojis())

        # loop through found emojis
        for emoji in emojis:
            # loop through all class attributes
            # this is inefficient but dynamic and only called once
            for attr, value in self.__dict__.items():
                if emoji.id == value:
                    setattr(self, attr, emoji)


custom_emojis: __ElevatorEmojis = __ElevatorEmojis()
