import dataclasses
import datetime


@dataclasses.dataclass
class LfgUpdateData:
    channel_id: int = None
    message_id: int = None
    voice_channel_id: int = None

    activity: str = None
    description: str = None
    start_time: datetime.datetime = None
    max_joined_members: int = None
    joined_members: list[int] = None
    alternate_members: list[int] = None


@dataclasses.dataclass
class LfgInputData:
    activity: str
    description: str
    start_time: datetime.datetime
    max_joined_members: int
    joined_members: list[int]
    alternate_members: list[int]
