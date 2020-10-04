from commands.base_command  import BaseCommand

class mutepepe(BaseCommand):
    def __init__(self):
        description = "Toggles Pepes mute status"
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        pepe = message.guild.get_member(367385031569702912)

        try:
            mute_status = pepe.voice.mute
        except AttributeError:
            await message.channel.send(f"Pepe needs to be in a voice channel for this to work 🙃")
            return

        # change mute status
        await pepe.edit(mute=not mute_status)
        text = "no longer" if mute_status else "now"
        await message.channel.send(f"Pepe is {text} muted 🙃")
