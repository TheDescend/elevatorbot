from Backend.crud.base import CRUDBase
from Backend.database.models import DiscordGuardiansToken


class CRUDDiscordUsers(CRUDBase):
    pass


discord_users = CRUDDiscordUsers(DiscordGuardiansToken)
