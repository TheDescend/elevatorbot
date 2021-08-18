from Backend.crud.base import CRUDBase
from Backend.database.models import PersistentMessage


class CRUDPersistentMessages(CRUDBase):
    pass


persistent_messages = CRUDPersistentMessages(PersistentMessage)
