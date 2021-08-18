from Backend.crud.base import CRUDBase
from Backend.database.models import Poll


class CRUDPolls(CRUDBase):
    pass


polls = CRUDPolls(Poll)
