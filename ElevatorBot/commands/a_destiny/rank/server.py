import copy

from dis_snek import Snake

from ElevatorBot.commandHelpers import autocomplete
from ElevatorBot.commands.a_destiny.rank.clan import RankClan


# inherit the rank command, just change the sub command name
class RankServer(RankClan):
    clan_mode = False

    def __new__(cls, bot: Snake, *args, **kwargs):
        # copy the command
        cls.rank = copy.copy(cls.rank)

        # set the subcommand to the correct name
        cls.rank.name = "rank_server"
        cls.rank.description = "Display Destiny 2 leaderboards. Pick **only** one leaderboard from all options"

        super().__new__(cls=cls, bot=bot, *args, **kwargs)
        return cls


def setup(client):
    command = RankServer(client)

    # register the autocomplete callback
    command.rank.autocomplete("weapon")(autocomplete.autocomplete_send_weapon_name)
    command.rank.autocomplete("activity")(autocomplete.autocomplete_send_activity_name)
