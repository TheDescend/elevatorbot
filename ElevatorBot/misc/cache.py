import dataclasses

from dis_snek.models import ThreadChannel


@dataclasses.dataclass
class ReplyCache:
    """This saves the user_id and thread to prevent the same user from opening new threads all the time"""

    user_to_thread: dict[int, ThreadChannel] = dataclasses.field(init=False, default_factory={})
    thread_to_user: dict[ThreadChannel, int] = dataclasses.field(init=False, default_factory={})


reply_cache = ReplyCache()
