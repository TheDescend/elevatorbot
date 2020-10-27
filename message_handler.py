import logging

from commands.base_command import BaseCommand
from functions.database import getToken
from functions.formating import embed_message
# This, in addition to tweaking __all__ on commands/__init__.py,
# imports all classes inside the commands package.
from commands import *
from static.config import COMMAND_PREFIX

# Register all available commands
COMMAND_HANDLERS = {c.__name__.lower(): c()
                    for c in BaseCommand.__subclasses__()}

###############################################################################


async def handle_command(command, args, message, bot_client):
    # Check whether the command is supported, stop silently if it's not
    # (to prevent unnecesary spam if our bot shares the same command prefix 
    # with some other bot)
    COMMAND_HANDLERS = {c.__name__.lower(): c()
                    for c in BaseCommand.__subclasses__()}
                    
    if command not in COMMAND_HANDLERS:
        return

    print(f"{message.author.name}: {COMMAND_PREFIX}{command} " 
          + " ".join(args))

    # log the command - <discordID,command,arg1 arg2>
    logger = logging.getLogger('commands')
    logger.info(f"""<{message.author.id},{command},{" ".join(args)}>""")

    # check if user is registered, otherwise command will be blocked and he will be informed
    # ignore that check if message is !register or !registerdesc
    if message.guild and message.guild.id == 669293365900214293:
        if (command != "register") and (command != "registerdesc"):
            if not getToken(message.author.id):
                await message.channel.send(embed=embed_message(
                    'Additional Action Necessary',
                    f'{message.author.name}, please first link your Destiny account by using `!register`'
                ))
                return

    # Retrieve the command
    cmd_obj = COMMAND_HANDLERS[command]
    if cmd_obj.params and not len(args) == len(cmd_obj.params):
        await message.channel.send(message.author.mention
                                      + f" Params should be {', '.join(cmd_obj.params)}")
    else:
        await cmd_obj.handle(args, message, bot_client)
        
