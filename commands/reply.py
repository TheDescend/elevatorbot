
from discord.ext import commands
from discord import File
from io import BytesIO

from commands.base_command import BaseCommand

from functions.miscFunctions import hasAdminOrDevPermissions


class reply(BaseCommand):
    def __init__(self):
        description = "Send a message to whoever got tagged above"
        topic = "Destiny"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        if not (await hasAdminOrDevPermissions(message)):
            return

        ctx = await client.get_context(message)
        user = None
        try:
            user = await commands.MemberConverter().convert(ctx, params[-1])
            messageText = ' '.join(params[:-1])
        except:
            pass
        previousMessage = (await message.channel.history(limit=2).flatten())[1]
        mentionedMembers = []
        if previousMessage.author == client.user:
            mentionedMembers = previousMessage.mentions

        if not user:
            if len(mentionedMembers) == 1:
                if '@' in message.clean_content:
                    await message.channel.send('Not sure if you meant to ping someone or reply above')
                    return
                user = mentionedMembers[0]
                messageText = ' '.join(params)
            else:
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
