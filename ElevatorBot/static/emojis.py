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

    # Emote Server
    among_us: CustomEmoji | int = 751020830376591420
    barotrauma: CustomEmoji | int = 756077724870901830
    gta: CustomEmoji | int = 751020831382962247
    valorant: CustomEmoji | int = 751020830414209064
    lol: CustomEmoji | int = 756076309527920661
    eft: CustomEmoji | int = 800866459286503445
    minecraft: CustomEmoji | int = 860099796123123712
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
