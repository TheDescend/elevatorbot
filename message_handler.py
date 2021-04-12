import logging
from discord.ext.commands import MemberConverter, MemberNotFound

from commands.base_command import BaseCommand
from functions.database import getToken
from functions.formating import embed_message
from functions.miscFunctions import show_help

# This, in addition to tweaking __all__ on commands/__init__.py,
# imports all classes inside the commands package.
from commands import *
from static.config import COMMAND_PREFIX

# Register all available commands
COMMAND_HANDLERS = {c.__name__.lower(): c()
                    for c in BaseCommand.__subclasses__()}

###############################################################################


async def handle_command(command, params, message, client):
    # Check whether the command is supported, stop silently if it's not
    # (to prevent unnecesary spam if our bot shares the same command prefix 
    # with some other bot)
    COMMAND_HANDLERS = {c.__name__.lower(): c()
                    for c in BaseCommand.__subclasses__()}
                    
    if command not in COMMAND_HANDLERS:
        return

    print(f"{message.author.name}: {COMMAND_PREFIX}{command} "
          + " ".join(params))

    # log the command - <discordID,command,arg1 arg2>
    logger = logging.getLogger('commands')
    logger.info(f"""<{message.author.id},{command},{" ".join(params)}>""")

    # check if user is registered, otherwise command will be blocked and he will be informed
    # ignore that check if message is !register or !registerdesc
    if message.guild and message.guild.id == 669293365900214293:
        if (command != "register") and (command != "registerdesc"):
            if not await getToken(message.author.id):
                await message.reply(embed=embed_message(
                    'Additional Action Necessary',
                    f'{message.author.name}, please first link your Destiny account by using `!register`'
                ))
                return

    # set mentioned_user params[-1] and if that is not valid to message.author
    mentioned_user = message.author
    if len(params) > 0:
        ctx = await client.get_context(message)
        try:
            temp = await MemberConverter().convert(ctx, params[-1])
            mentioned_user = temp
            params = params[:-1]
        except MemberNotFound:
            pass
            #print(f"Tried to convert last parameter '{params[-1]}' to mentioned_user and failed")

    # Retrieve the command
    cmd_obj = COMMAND_HANDLERS[command]
    relevant_params = []
    for param in cmd_obj.params:
        if not param.startswith("*"):
            relevant_params.append(param)
    if (cmd_obj.params and len(params) < len(relevant_params)) or command.lower() == "help" or (params and 'help' in params):
        # show help msg
        await show_help(message, command, cmd_obj.params)
    else:
        await cmd_obj.handle(params, message, mentioned_user, client)
