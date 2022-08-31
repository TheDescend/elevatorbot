from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ElevatorBot.elevator import Elevator


_ERROR_CODES_AND_RESPONSES: Optional[dict[str, str]] = None


def get_error_codes_and_responses(client: Optional["Elevator"] = None):
    global _ERROR_CODES_AND_RESPONSES
    if not _ERROR_CODES_AND_RESPONSES and client:
        _ERROR_CODES_AND_RESPONSES = {
            "DestinyIdNotFound": f"""I don't possess information for the user with the DestinyID `{{destiny_id}}` \nPlease {client.get_command_by_name("register").mention()} to use my commands""",
            "DiscordIdNotFound": f"""I don't possess information for {{discord_member.mention}} \nPlease {client.get_command_by_name("register").mention()} to use my commands""",
            "CharacterIdNotFound": "{discord_member.mention} does not have a character with that ID",
            "NoToken": f"""{{discord_member.mention}} registration is outdated \nPlease {client.get_command_by_name("register").mention()} again""",
            "BungieUnauthorized": "The request was not authorized correctly",
            "BungieDed": "The Bungie API is down at the moment \nPlease try again later",
            "BungieNoDestinyId": "You do not seem to have a Destiny 2 account",
            "BungieBadRequest": "I got a 404 error. This shouldn't happen, my bad. Consider me punished",
            "BungieDestinyItemNotFound": "{discord_member.mention} doesn't own this item",
            "BungieDestinyItemNotExist": "I tried to find an item that does not exist \nPlease excuse this mishap while I punish myself",
            "BungieDestinyPrivacyRestriction": "{discord_member.mention} has a private profile \nPlease change your [privacy settings](https://www.bungie.net/en/Profile/Settings/)",
            "BungieClanTargetDisallowsInvites": "{discord_member.mention} is not allowing clan invites \nPlease change your [privacy settings](https://www.bungie.net/en/Profile/Settings/)",
            "BungieGroupMembershipNotFound": "{discord_member.mention} is not in the clan and can thus not be removed \nI felt like adding them just to remove them was going too far",
            "BungieClanInviteAlreadyMember": "{discord_member.mention} is already in the clan",
            "UnknownError": "I got an unknown error while handling your request \nPlease contact a developer",
            "ProgrammingError": "The impossible happened... I was programmed incorrectly :( \nPlease contact a developer",
            "NoClanLink": f"""This guild does not have a linked clan\nPlease have an admin run {client.get_command_by_name("setup clan link").mention()} to set this up""",
            "NoClan": f"""The linked clan could not be found. Either bungie is having problems, or the clan link is broken\nPlease consider having an admin run {client.get_command_by_name("setup clan link").mention()} again""",
            "UserNoClan": "{discord_member.mention} is not in any clan",
            "ClanNoPermissions": f"""Could not invite {{discord_member.mention}} to the linked clan, since the user who linked the clan to this discord guild is no longer a Destiny 2 clan admin\nPlease have an Admin re-link the clan by running {client.get_command_by_name("setup clan link").mention()} to fix this""",
            "NoLfgEventWithIdForGuild": "No LFG event was found for that ID \nPlease try again",
            "NoLfgChannelForGuild": f"""No LFG channel has been setup for this guild\nPlease have an admin use {client.get_command_by_name("setup lfg channel").mention()} and then try again""",
            "NoLfgEventPermissions": "{discord_member.mention} does not have permissions to edit this LFG event \nOnly the creator and discord admins can do that",
            "RoleLookupTimedOut": "The role lookup for {discord_member.mention} timed out. This shouldn't happen, my bad. Consider me punished",
            "PollNoPermission": "{discord_member.mention} does not have permissions to modify this poll",
            "PollOptionNotExist": "This option does not exist. Make sure you spelled it correctly",
            "PollNotExist": "This poll ID does not exist",
            "NoActivityFound": "{discord_member.mention} has never done an activity that fulfills the given requirements",
            "WeaponUnused": "{discord_member.mention} has never used the specified weapon in any activity that fulfills the given requirements",
            "WeaponTypeMismatch": "This weapon does not belong to the specified weapon type",
            "WeaponDamageTypeMismatch": "This weapon does not have the specified damage type",
            "PersistentMessageNotExist": "This persistent message does not exist",
            "RoleNotExist": "This role is not achievable through me",
            "NoGiveaway": "This is not a giveaway I am hosting",
            "AlreadyInGiveaway": "I would never forget you, do not worry <3\nYou have already entered the giveaway",
        }
    return _ERROR_CODES_AND_RESPONSES
