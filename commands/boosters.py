from commands.base_command  import BaseCommand
from functions.formating import embed_message


class boosters(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Prints all premium subscribers"
        params = []
        super().__init__(description, params)
    
    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        embed = embed_message(
            f"{message.guild.name} Nitro Boosters",
            ", ".join(["**" + m.display_name + "** - since: " + m.premium_since.strftime('%d/%m/%Y %H:%M') for m in message.guild.premium_subscribers])
        )

        await message.reply(embed=embed)


