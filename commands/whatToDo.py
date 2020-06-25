from commands.base_command  import BaseCommand
from functions.formating    import embed_message
from static.dict            import requirementHashes
from functions.dataLoading  import getTriumphsJSON, getSeals
from functions.database     import lookupDestinyID
from functions.network      import getJSONfromURL

import discord
import json

class whatToDo(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Tells you what you can still achieve in Destiny / this Server"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        # if those get edited, need to change below as well
        types = [
            "roles",
            "triumphs",
            "seals"
        ]

        # check if message too long
        if len(params) > 2:
            await message.channel.send(embed=embed_message(
                'Error',
                'Incorrect formatting, correct usage is: \n.B\n `!whatToDo *<type> *<user>`'
            ))
            return

        # set user to the one that send the message, or if a 2nd param was used, the one mentioned
        # do the same, if the first param can be converted to a user
        user = message.author
        block = False
        ctx = await client.get_context(message)
        try:
            user = await discord.ext.commands.MemberConverter().convert(ctx, params[0])
            block = True
        except:
            pass
        if len(params) == 2:
            try:
                user = await discord.ext.commands.MemberConverter().convert(ctx, params[1])
            except:
                await message.channel.send(
                    embed=embed_message(
                        'Error',
                        'User not found, make sure the spelling/id is correct'
                    ))
                return

        # check if types is correct
        try:
            if (params[0] not in types) and (not block):
                await message.channel.send(embed=embed_message(
                    'Error',
                    f'Unrecognised type, currently supported are: \n.B\n`{", ".join(types)}`'
                ))
                return
        except IndexError:
            pass


        async with message.channel.typing():
            embed = embed_message(
                f"{message.author.name}'s ToDo List"
            )

            # do everything if no specific type was given
            do_all = False
            if (len(params) == 0) or block:
                do_all = True

            # do the missing roles display
            if do_all or (params[0] == "roles"):
                embed.add_field(name="⁣", value=f"__**Roles:**__", inline=False)

                roles = self.missingRoles(user)

                # only do this if there are roles to get
                if roles:
                    for topic in roles:
                        embed.add_field(name=topic, value=("\n".join(roles[topic]) or "None"), inline=True)
                else:
                    embed.add_field(name="Wow, you got every single role. Congrats!", value=".", inline=False)

            # do the missing triumphs display
            if do_all or (params[0] == "triumphs"):
                embed.add_field(name="⁣", value=f"__**Triumphs:**__", inline=False)

                missing = self.missingTriumphs(user)

                # only do this if there are triumphs to get
                if missing:
                    # if do_all, show only half of the triumphs
                    if do_all:
                        max = len(missing) / 2
                        i = 0
                    for name, val in missing.items():
                        if do_all:
                            if i >= max:
                                break
                            i += 1
                        if not name:
                            name = '.'
                        embed.add_field(name=name, value="\n".join(val), inline=True)

                    embed.add_field(name="You are pretty close to finishing those triumphs", value="⁣.", inline=False)
                else:
                    embed.add_field(name="Wow, you have done every triumph. Congrats!", value=".⁣", inline=False)

            # do the missing seals display
            if do_all or (params[0] == "seals"):
                icons = {
                    "Cursebreaker": "<:cursebreaker:724678413805420635>",
                    "Wayfarer": "<:wayfarer:724678414857928724>",
                    "Unbroken": "<:unbroken:724678414925168680>",
                    "Dredgen": "<:dredgen:724678414107148469>",
                    "Rivensbane": "<:rivensbane:724678414451212378>",
                    "Chronicler": "<:chronicler:724678413029212271>",
                    "Blacksmith": "<:blacksmith:724678411963859506>",
                    "Reckoner": "<:reckoner:724678413365018695>",
                    "Shadow": "<:shadow:724678413733986305>",
                    "MMXIX": "<:mmxix:724678413465681920>",
                    "Harbinger": "<:harbinger:724678412785942586>",
                    "Undying": "<:undying:724678413956284456>",
                    "Enlightened": "<:enlightened:724678413063028848>",
                    "Savior": "<:dawn:724678412484214885>",
                    "Flawless": "<:flawless:724678413528465467>",
                    "Conqueror": "<:conqueror:724678412077236254>",
                    "Almighty": "<:almighty:724678407488798770>",
                    "Forerunner": "<:forerunner:724678413830455307>"
                }

                embed.add_field(name="⁣", value=f"__**Seals:**__", inline=False)

                missing = self.missingSeals(client, user)

                if missing:
                    for seal in missing:
                        name = seal[2]
                        try:
                            name = icons[seal[2]] + " " + seal[2]
                        except:
                            pass
                        if not name:
                            name = '.'
                        embed.add_field(name=str(int(seal[4] * 100)) + "% done", value=name, inline=True)
                else:
                    embed.add_field(name="Wow, you got every single seal that is available right now. Congrats, but I hope you haven't missed one like **@MysticShadow** :upside_down:", value="⁣.", inline=False)

        await message.channel.send(embed=embed)

    def missingRoles(self, user):
        roles = {}

        # get list of roles available
        for category, x in requirementHashes.items():
            for role, _ in x.items():
                try:
                    roles[category].append(role)
                except KeyError:
                    roles[category] = [role]

        # remove the roles from dict(roles) that are already earned
        user_roles = [role.name for role in user.roles]
        for role in user_roles:
            for category in roles:
                try:
                    roles[category].remove(role)
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
        return roles

    def missingTriumphs(self, user):
        destinyID = lookupDestinyID(user.id)
        triumphs = getTriumphsJSON(destinyID)

        user_triumphs = {}
        if triumphs is None:
            return False
        # converting to python dict
        triumphs = json.loads(json.dumps(triumphs))
        for triumph in triumphs:
            try:
                # ignore if done
                if not triumphs[triumph]["objectives"][0]["complete"]:
                    # ignore if invisible
                    if triumphs[triumph]["objectives"][0]["visible"]:
                        user_triumphs[triumph] = int(triumphs[triumph]["objectives"][0]["progress"]) / int(triumphs[triumph]["objectives"][0]["completionValue"])
            except:
                pass

        # get the 12 triumphs that are the closest to be done
        nearly_done_info = {}
        while len(nearly_done_info) < 12:
            maximum = max(user_triumphs, key=user_triumphs.get)

            # test if triumph has a name / description, some do not for some reason. Ignore if no name
            rep = getJSONfromURL(f"https://www.bungie.net/Platform/Destiny2/Manifest/DestinyRecordDefinition/{maximum}/")
            if rep and rep['Response']:
                name = rep['Response']["displayProperties"]["name"]
                desc = rep['Response']["displayProperties"]["description"]
                if (name != "") and (desc != ""):
                    nearly_done_info[name] = [desc, "**" + str(int(user_triumphs[maximum] * 100)) + "% done**"]

            # remove element from list
            user_triumphs.pop(maximum)

        return nearly_done_info

    def missingSeals(self, client, user):
        missing_seals = []
        seals = getSeals(client)

        destinyID = lookupDestinyID(user.id)
        triumphs = getTriumphsJSON(destinyID)
        if triumphs is None:
            return False
        # converting to python dict (for true -> True conversion)
        triumphs = json.loads(json.dumps(triumphs))

        # add to list if seal is incomplete
        for seal in seals:
            # ignore if seal is done
            if not triumphs[str(seal[0])]["objectives"][0]["complete"]:
                # ignore if not available anymore
                if seal[3]:
                    completion_rate = int(triumphs[seal[0]]["objectives"][0]["progress"]) / int(triumphs[seal[0]]["objectives"][0]["completionValue"])
                    # sometimes the api shows not every step completed, even tho I have the title unlocked
                    if triumphs[seal[0]]["objectives"][0]["complete"]:
                        completion_rate = 1

                    seal.append(completion_rate)
                    missing_seals.append(seal)

        return missing_seals








