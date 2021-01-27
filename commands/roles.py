import json

from commands.base_command import BaseCommand
from functions.dataLoading import getTriumphsJSON, getSeals
from functions.database import lookupDestinyID
from functions.formating import embed_message
from functions.miscFunctions import show_help
from functions.network import getJSONfromURL
from static.dict import requirementHashes


class Roles(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Shows you what roles you can still achieve in this clan"
        params = []
        topic = "Destiny"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        async with message.channel.typing():
            embed = embed_message(
                f"{mentioned_user.display_name}'s missing Roles"
            )

            roles, deprecated_roles = self.missingRoles(mentioned_user)

            # do the missing roles display
            embed.add_field(name="⁣", value=f"__**Achievable Roles:**__", inline=False)

            # only do this if there are roles to get
            if roles:
                for topic in roles:
                    embed.add_field(name=topic, value=("\n".join(roles[topic]) or "None"), inline=True)
            else:
                embed.add_field(name="Wow, you got every single role that is currently achievable. Congrats!", value="⁣", inline=False)

            # Do the same for the deprecated roles
            if deprecated_roles:
                embed.add_field(name="⁣", value=f"__**Deprecated Roles:**__", inline=False)
                for topic in deprecated_roles:
                    embed.add_field(name=topic, value=("\n".join(deprecated_roles[topic]) or "None"), inline=True)

            await message.reply(embed=embed)

    def missingRoles(self, user):
        roles = {}
        deprecated_roles = {}

        # get list of roles available
        for category, x in requirementHashes.items():
            for role, req in x.items():
                # depending on if its deprecated or not, add to respective dict
                if "deprecated" not in req:
                    try:
                        roles[category].append(role)
                    except KeyError:
                        roles[category] = [role]
                else:
                    try:
                        deprecated_roles[category].append(role)
                    except KeyError:
                        deprecated_roles[category] = [role]

        # remove the roles from dict(roles) that are already earned
        user_roles = [role.name for role in user.roles]
        for role in user_roles:
            for category in roles:
                try:
                    roles[category].remove(role)
                    break
                except ValueError:
                    pass
            for category in deprecated_roles:
                try:
                    deprecated_roles[category].remove(role)
                    break
                except ValueError:
                    pass

        # remove those roles, where a superior role exists
        for category, x in requirementHashes.items():
            for role, roledata in x.items():
                if 'replaced_by' in roledata.keys():
                    for superior in roledata['replaced_by']:
                        if superior in user_roles:
                            for category in roles:
                                try:
                                    roles[category].remove(role)
                                    break
                                except ValueError:
                                    pass
                            for category in deprecated_roles:
                                try:
                                    deprecated_roles[category].remove(role)
                                    break
                                except ValueError:
                                    pass

        # remove the empty categories
        for role, roledata in roles.copy().items():
            if not roledata:
                roles.pop(role)
        for role, roledata in deprecated_roles.copy().items():
            if not roledata:
                deprecated_roles.pop(role)

        return roles, deprecated_roles
