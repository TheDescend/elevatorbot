from Backend.crud.base import CRUDBase
from Backend.database.models import LfgMessage, LfgUser


class CRUDLfgMessages(CRUDBase):
    pass


class CRUDLfgUsers(CRUDBase):
    pass


lfg_message = CRUDLfgMessages(LfgMessage)
lfg_user = CRUDLfgUsers(LfgUser)
