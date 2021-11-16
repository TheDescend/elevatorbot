from dis_snek.client import Snake
from dis_snek.models import CustomEmoji


class __ElevatorEmojis:
    """To add an emoji add it to the class variables"""

    # Descend Font
    tile_left: CustomEmoji | int = 768906489309822987
    tile_mid: CustomEmoji | int = 768906489103384657
    tile_right: CustomEmoji | int = 768906489729122344

    yes: CustomEmoji | int = 768908985557844028
    question: CustomEmoji | int = 768906489686655016
    enter: CustomEmoji | int = 768906489103384688
    circle: CustomEmoji | int = 768906489464619008

    destiny: CustomEmoji | int = 768906489472876574
    descend_logo: CustomEmoji | int = 768907515193720874
    elevator_logo: CustomEmoji | int = 768907515386921020

    kinetic: CustomEmoji | int = 906180170875031562
    stasis: CustomEmoji | int = 897797463799369769
    arc: CustomEmoji | int = 897797463933583401
    solar: CustomEmoji | int = 897797463937798174
    void: CustomEmoji | int = 897797464013307905

    unstoppable: CustomEmoji | int = 897797463807774752
    barrier: CustomEmoji | int = 897797463988142091
    overload: CustomEmoji | int = 897797463988142090

    auto_rifle: CustomEmoji | int = 906180170778546226
    shotgun: CustomEmoji | int = 906180170971484220
    machine_gun: CustomEmoji | int = 906180170833100820
    hand_cannon: CustomEmoji | int = 906180170979881000
    rocket_launcher: CustomEmoji | int = 906180170799521812
    fusion_rifle: CustomEmoji | int = 906180170929565777
    sniper_rifle: CustomEmoji | int = 906180170807906366
    pulse_rifle: CustomEmoji | int = 906180170820485190
    scout_rifle: CustomEmoji | int = 906180170858250261
    sidearm: CustomEmoji | int = 906180170833096774
    sword: CustomEmoji | int = 906180170929565776
    linear_fusion_rifle: CustomEmoji | int = 906180170807906365
    grenade_launcher: CustomEmoji | int = 906180170405249025
    submachine_gun: CustomEmoji | int = 906180170799521815
    trace_rifle: CustomEmoji | int = 906180170858250260  # todo missing
    bow: CustomEmoji | int = 906180170799538206

    primary: CustomEmoji | int = 906180170887622656
    special: CustomEmoji | int = 906180170858250260
    heavy: CustomEmoji | int = 906180170451410985

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

    zoom: CustomEmoji | int = 906503515642425396
    ping_sock: CustomEmoji | int = 586436224013565992

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
