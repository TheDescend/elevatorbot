
from discord.ext import commands
from discord import File
from io import BytesIO

from commands.base_command import BaseCommand

from functions.miscFunctions import hasAdminOrDevPermissions


class reply(BaseCommand):
    def __init__(self):
        description = "[Admin] Send a message to whoever got tagged above"
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, mentioned_user, client):
        if not (await hasAdminOrDevPermissions(message)):
            return

        ctx = await client.get_context(message)
        
        #gets the previous message
        previousMessage = (await message.channel.history(limit=2).flatten())[1]
        mentionedMembersInPreviousMessage = []
        #if previous message is posted by the bot and mentions at least 1 member
        if previousMessage.author == client.user and previousMessage.mentions:
            mentionedMembersInPreviousMessage = previousMessage.mentions

        #someone is tagged, noone is mentioned in the previous message
        if mentioned_user and not mentionedMembersInPreviousMessage:
            messageText = ' '.join(params)
            user = mentioned_user
        else:
            if len(mentionedMembersInPreviousMessage) == 1:
                #if the previous message mentions 1
                if '@' in message.clean_content:
                    #but wait, the current message also mentions someone
                    await message.channel.send('Not sure if you meant to ping someone or reply above')
                    return
                #take the only mentioned member
                user = mentionedMembersInPreviousMessage[0]
                messageText = ' '.join(params)
            else:
                #if the previous message mentions more than 1
                await message.channel.send('Make sure my message above mentions the user or you mention them as the last argument')
                return

        assert(user is not None)

        userAnswer = messageText#+ ('\n' if messageText else '') + '-' + message.author.mention

        if message.attachments:
            attached_files = [File(BytesIO(await attachment.read()),filename=attachment.filename) for attachment in message.attachments]
            await user.send(userAnswer or '_', files=attached_files)
            await message.channel.send(f'{message.author.name} Answered\n`{messageText}`\nto {user.mention}', files=attached_files)
        else:
            await user.send(userAnswer)
            await message.channel.send(f'{message.author.name} Answered\n`{messageText}`\nto {user.mention}')
