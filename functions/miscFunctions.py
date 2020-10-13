from functions.formating import embed_message
from functions.database import getToken



async def checkIfUserIsRegistered(user):
    if getToken(user.id):
        return True
    else:
        embed = embed_message(
            "Error",
            "Please register with `!register` first (not via DMs)"
        )
        await user.send(embed=embed)
        return False
