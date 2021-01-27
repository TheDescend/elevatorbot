""" Shows stats for your destiny Account """

"Old stuff I used for seals / triumphs. Maybe useful"
# # do the missing triumphs display
# if do_all or (params[0] == "triumphs"):
#     embed.add_field(name="⁣", value=f"__**Triumphs:**__", inline=False)
#
#     missing = await self.missingTriumphs(mentioned_user)
#
#     # only do this if there are triumphs to get
#     if missing:
#         # if do_all, show only half of the triumphs
#         if do_all:
#             max = len(missing) / 2
#             i = 0
#         for name, val in missing.items():
#             if do_all:
#                 if i >= max:
#                     break
#                 i += 1
#             if not name:
#                 name = '.'
#             embed.add_field(name=name, value="\n".join(val), inline=True)
#
#         embed.add_field(name="You are pretty close to finishing those triumphs", value="⁣", inline=False)
#     else:
#         embed.add_field(name="Wow, you have done every triumph. Congrats!", value="⁣", inline=False)
#
# # do the missing seals display
# if do_all or (params[0] == "seals"):
#     icons = {
#         "Cursebreaker": "<:cursebreaker:724678413805420635>",
#         "Wayfarer": "<:wayfarer:724678414857928724>",
#         "Unbroken": "<:unbroken:724678414925168680>",
#         "Dredgen": "<:dredgen:724678414107148469>",
#         "Rivensbane": "<:rivensbane:724678414451212378>",
#         "Chronicler": "<:chronicler:724678413029212271>",
#         "Blacksmith": "<:blacksmith:724678411963859506>",
#         "Reckoner": "<:reckoner:724678413365018695>",
#         "Shadow": "<:shadow:724678413733986305>",
#         "MMXIX": "<:mmxix:724678413465681920>",
#         "Harbinger": "<:harbinger:724678412785942586>",
#         "Undying": "<:undying:724678413956284456>",
#         "Enlightened": "<:enlightened:724678413063028848>",
#         "Savior": "<:dawn:724678412484214885>",
#         "Flawless": "<:flawless:724678413528465467>",
#         "Conqueror": "<:conqueror:724678412077236254>",
#         "Almighty": "<:almighty:724678407488798770>",
#         "Forerunner": "<:forerunner:724678413830455307>"
#     }
#
#     embed.add_field(name="⁣", value=f"__**Seals:**__", inline=False)
#
#     missing = await self.missingSeals(client, mentioned_user)
#
#     if missing:
#         for seal in missing:
#             name = seal[2]
#             try:
#                 name = icons[seal[2]] + " " + seal[2]
#             except:
#                 pass
#             if not name:
#                 name = '.'
#             embed.add_field(name=str(int(seal[4] * 100)) + "% done", value=name, inline=True)
#     else:
#         embed.add_field(
#             name="Wow, you got every single seal that is available right now. Congrats, but I hope you haven't missed one like **@MysticShadow** :upside_down:",
#             value="⁣.", inline=False)
#
# await message.channel.send(embed=embed)
#
#
# async def missingTriumphs(self, user):
#     destinyID = lookupDestinyID(user.id)
#     triumphs = await getTriumphsJSON(destinyID)
#
#     user_triumphs = {}
#     if triumphs is None:
#         return False
#     # converting to python dict
#     triumphs = json.loads(json.dumps(triumphs))
#     for triumph in triumphs:
#         try:
#             # ignore if done
#             if not triumphs[triumph]["objectives"][0]["complete"]:
#                 # ignore if invisible
#                 if triumphs[triumph]["objectives"][0]["visible"]:
#                     user_triumphs[triumph] = int(triumphs[triumph]["objectives"][0]["progress"]) / int(
#                         triumphs[triumph]["objectives"][0]["completionValue"])
#         except:
#             pass
#
#     # get the 12 triumphs that are the closest to be done
#     nearly_done_info = {}
#     while len(nearly_done_info) < 12:
#         maximum = max(user_triumphs, key=user_triumphs.get)
#
#         # test if triumph has a name / description, some do not for some reason. Ignore if no name
#         rep = await getJSONfromURL(
#             f"https://www.bungie.net/Platform/Destiny2/Manifest/DestinyRecordDefinition/{maximum}/")
#         if rep and rep['Response']:
#             name = rep['Response']["displayProperties"]["name"]
#             desc = rep['Response']["displayProperties"]["description"]
#             if (name != "") and (desc != ""):
#                 nearly_done_info[name] = [desc, "**" + str(int(user_triumphs[maximum] * 100)) + "% done**"]
#
#         # remove element from list
#         user_triumphs.pop(maximum)
#
#     return nearly_done_info
#
#
# async def missingSeals(self, client, user):
#     missing_seals = []
#     seals = getSeals(client)
#
#     destinyID = lookupDestinyID(user.id)
#     triumphs = await getTriumphsJSON(destinyID)
#     if triumphs is None:
#         return False
#     # converting to python dict (for true -> True conversion)
#     triumphs = json.loads(json.dumps(triumphs))
#
#     # add to list if seal is incomplete
#     for seal in seals:
#         # ignore if seal is done
#         if not triumphs[str(seal[0])]["objectives"][0]["complete"]:
#             # ignore if not available anymore
#             if seal[3]:
#                 completion_rate = int(triumphs[seal[0]]["objectives"][0]["progress"]) / int(
#                     triumphs[seal[0]]["objectives"][0]["completionValue"])
#                 # sometimes the api shows not every step completed, even tho I have the title unlocked
#                 if triumphs[seal[0]]["objectives"][0]["complete"]:
#                     completion_rate = 1
#
#                 seal.append(completion_rate)
#                 missing_seals.append(seal)
#
#     return missing_seals








