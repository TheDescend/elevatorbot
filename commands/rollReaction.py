import random

from commands.base_command import BaseCommand


# todo wait until hideable
class rollreaction(BaseCommand):
    def __init__(self):
        # A quick description for the help tmessage
        description = "Picks a random reactor from the post above"
        params = ['Number of people to draw']
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        #if len(params) == 0:
        tmessage = (await message.channel.history(limit=2).flatten())[1]
        # elif len(params) == 2:
        #     messageid = int(params[0])
        #     channelid = int(params[1])
        #     channel = client.get_channel(channelid)
        #     if not channel:
        #         await message.channel.send('invalid channel id')
        #         return
        #     tmessage = await channel.fetch_message(messageid)
        if not tmessage:
            await message.channel.send('getting message failed')
            return
        reactionlist = tmessage.reactions
        userlist = []
        for reaction in reactionlist:
            userlist += await reaction.users().flatten()
        uniqueusers = []
        for u in userlist:
            if u not in uniqueusers:
                uniqueusers.append(u)
        
        if len(params) == 1:
            numDraws = int(params[0])
        else:
            numDraws = 1
            
        if len(uniqueusers) < numDraws:
            await message.channel.send('not enough reactions found')
            return
        winners = [winner.mention for winner in random.sample(uniqueusers, numDraws)]
        await message.channel.send(f'Selected users {", ".join(winners)}')
