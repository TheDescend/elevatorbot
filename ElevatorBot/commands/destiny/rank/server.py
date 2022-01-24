import copy

from dis_snek import Snake

from ElevatorBot.commandHelpers.autocomplete import autocomplete_send_activity_name, autocomplete_send_weapon_name
from ElevatorBot.commands.destiny.rank.clan import RankClan


# inherit the rank command, just change the sub command name
class RankServer(RankClan):
    clan_mode = False

    def __new__(cls, bot: Snake, *args, **kwargs):
        # copy the command
        cls.rank = copy.copy(cls.rank)

        # set the subcommand to the correct name
        cls.rank.sub_cmd_name = "server"
        cls.rank.sub_cmd_description = "Show all server members on the leaderboard"

        super().__new__(cls=cls, bot=bot, *args, **kwargs)
        return cls


def setup(client):
    command = RankServer(client)

    # register the autocomplete callback
    command.rank.autocomplete("weapon")(autocomplete_send_weapon_name)
    command.rank.autocomplete("activity")(autocomplete_send_activity_name)
