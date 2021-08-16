from sqlalchemy import ARRAY, BigInteger, Boolean, Column, Date, DateTime, Integer, JSON, Numeric, SmallInteger, Table, Text, UniqueConstraint, text
from sqlalchemy.ext.asyncio import AsyncConnection

from Backend.database.base import Base


metadata = Base.metadata


# all table models are in here, allowing for easy generation
class Activity(Base):
    __tablename__ = 'activities'

    instanceid = Column(BigInteger, primary_key=True)
    activityhash = Column(BigInteger)
    activitydurationseconds = Column(Integer)
    period = Column(DateTime)
    startingphaseindex = Column(Integer)
    deaths = Column(Integer)
    playercount = Column(Integer)
    mode = Column(Integer)


class Bountygoblin(Base):
    __tablename__ = 'bountygoblins'

    discordsnowflake = Column(BigInteger, primary_key=True)
    exp_pve = Column(Integer)
    exp_pvp = Column(Integer)
    exp_raids = Column(Integer)
    points_bounties_pve = Column(Integer)
    points_bounties_pvp = Column(Integer)
    points_bounties_raids = Column(Integer)
    points_competition_pve = Column(Integer)
    points_competition_pvp = Column(Integer)
    points_competition_raids = Column(Integer)
    active = Column(Integer)
    notifications = Column(Integer, server_default=text("0"))


t_characters = Table(
    'characters', metadata,
    Column('destinyid', BigInteger),
    Column('characterid', BigInteger, unique=True),
    Column('systemid', Integer, server_default=text("3")),
    UniqueConstraint('destinyid', 'characterid')
)


class D2steamplayer(Base):
    __tablename__ = 'd2steamplayers'

    dateobj = Column(DateTime, primary_key=True)
    numberofplayers = Column(Integer)


class Destinyactivitydefinition(Base):
    __tablename__ = 'destinyactivitydefinition'

    referenceid = Column(BigInteger, primary_key=True)
    description = Column(Text)
    name = Column(Text)
    activitylevel = Column(SmallInteger)
    activitylightlevel = Column(Integer)
    destinationhash = Column(BigInteger)
    placehash = Column(BigInteger)
    activitytypehash = Column(BigInteger)
    ispvp = Column(Boolean)
    directactivitymodehash = Column(BigInteger)
    directactivitymodetype = Column(SmallInteger)
    activitymodehashes = Column(ARRAY(BigInteger()))
    activitymodetypes = Column(ARRAY(SmallInteger()))


class Destinyactivitymodedefinition(Base):
    __tablename__ = 'destinyactivitymodedefinition'

    referenceid = Column(SmallInteger, primary_key=True)
    description = Column(Text)
    name = Column(Text)
    hash = Column(BigInteger)
    activitymodecategory = Column(SmallInteger)
    isteambased = Column(Boolean)
    friendlyname = Column(Text)


class Destinyactivitytypedefinition(Base):
    __tablename__ = 'destinyactivitytypedefinition'

    referenceid = Column(BigInteger, primary_key=True)
    description = Column(Text)
    name = Column(Text)


class Destinycollectibledefinition(Base):
    __tablename__ = 'destinycollectibledefinition'

    referenceid = Column(BigInteger, primary_key=True)
    description = Column(Text)
    name = Column(Text)
    sourcehash = Column(BigInteger)
    itemhash = Column(BigInteger)
    parentnodehashes = Column(ARRAY(BigInteger()))


class Destinyinventorybucketdefinition(Base):
    __tablename__ = 'destinyinventorybucketdefinition'

    referenceid = Column(BigInteger, primary_key=True)
    description = Column(Text)
    name = Column(Text)
    category = Column(SmallInteger)
    itemcount = Column(SmallInteger)
    location = Column(SmallInteger)


class Destinyinventoryitemdefinition(Base):
    __tablename__ = 'destinyinventoryitemdefinition'

    referenceid = Column(BigInteger, primary_key=True)
    description = Column(Text)
    name = Column(Text)
    classtype = Column(SmallInteger)
    buckettypehash = Column(BigInteger)
    tiertypehash = Column(BigInteger)
    tiertypename = Column(Text)
    equippable = Column(Boolean)


class Destinypresentationnodedefinition(Base):
    __tablename__ = 'destinypresentationnodedefinition'

    referenceid = Column(BigInteger, primary_key=True)
    description = Column(Text)
    name = Column(Text)
    objectivehash = Column(BigInteger)
    presentationnodetype = Column(SmallInteger)
    childrenpresentationnodehash = Column(ARRAY(BigInteger()))
    childrencollectiblehash = Column(ARRAY(BigInteger()))
    childrenrecordhash = Column(ARRAY(BigInteger()))
    childrenmetrichash = Column(ARRAY(BigInteger()))
    parentnodehashes = Column(ARRAY(BigInteger()))
    index = Column(SmallInteger)
    redacted = Column(Boolean)


class Destinyrecorddefinition(Base):
    __tablename__ = 'destinyrecorddefinition'

    referenceid = Column(BigInteger, primary_key=True)
    description = Column(Text)
    name = Column(Text)
    hastitle = Column(Boolean)
    titlename = Column(Text)
    objectivehashes = Column(ARRAY(BigInteger()))
    scorevalue = Column(Integer)
    parentnodehashes = Column(ARRAY(BigInteger()))


class DiscordGuardiansToken(Base):
    __tablename__ = 'discordGuardiansToken'

    discordsnowflake = Column(BigInteger, primary_key=True)
    destinyid = Column(BigInteger)
    signupdate = Column(Date)
    serverid = Column(BigInteger)
    token = Column(Text)
    refresh_token = Column(Text)
    systemid = Column(Integer)
    token_expiry = Column(DateTime)
    refresh_token_expiry = Column(DateTime)
    steamjoinid = Column(BigInteger)
    activitieslastupdated = Column(DateTime, server_default=text("'2000-01-01 00:00:00'::timestamp without time zone"))


class Discordguardian(Base):
    __tablename__ = 'discordguardians'

    discordsnowflake = Column(BigInteger, primary_key=True)
    destinyid = Column(BigInteger, nullable=False, unique=True)
    signupdate = Column(Date)
    serverid = Column(BigInteger)


class Discordguardianstoken(Base):
    __tablename__ = 'discordguardianstoken'

    discordsnowflake = Column(BigInteger, primary_key=True)
    destinyid = Column(BigInteger)
    signupdate = Column(Date)
    serverid = Column(BigInteger)
    token = Column(Text)
    refresh_token = Column(Text)
    systemid = Column(Integer)
    token_expiry = Column(DateTime)
    refresh_token_expiry = Column(DateTime)
    steamjoinid = Column(BigInteger)
    activitieslastupdated = Column(DateTime)


t_instanceplayerperformance = Table(
    'instanceplayerperformance', metadata,
    Column('instanceid', BigInteger),
    Column('playerid', BigInteger),
    Column('characterid', BigInteger),
    Column('lightlevel', Integer),
    Column('displayname', Text),
    Column('deaths', Integer),
    Column('opponentsdefeated', Integer),
    Column('completed', Integer),
    UniqueConstraint('instanceid', 'characterid')
)


class Lfgmessage(Base):
    __tablename__ = 'lfgmessages'

    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger)
    channel_id = Column(BigInteger)
    message_id = Column(BigInteger)
    author_id = Column(BigInteger)
    activity = Column(Text)
    description = Column(Text)
    start_time = Column(DateTime(True))
    max_joined_members = Column(Integer)
    joined_members = Column(ARRAY(BigInteger()))
    alternate_members = Column(ARRAY(BigInteger()))
    creation_time = Column(DateTime(True))
    voice_channel_id = Column(BigInteger)


class Lfguser(Base):
    __tablename__ = 'lfgusers'

    user_id = Column(BigInteger, primary_key=True)
    blacklisted_members = Column(ARRAY(BigInteger()))


t_markovpairs = Table(
    'markovpairs', metadata,
    Column('word1', Text),
    Column('word2', Text)
)


t_messagedb = Table(
    'messagedb', metadata,
    Column('msg', Text),
    Column('userid', BigInteger),
    Column('channelid', BigInteger),
    Column('msgid', BigInteger),
    Column('msgdate', Date)
)


class OwnedEmblem(Base):
    __tablename__ = 'owned_emblems'

    destiny_id = Column(BigInteger, primary_key=True)
    emblem_hash = Column(BigInteger)


class Persistentmessage(Base):
    __tablename__ = 'persistentmessages'

    messagename = Column(Text, primary_key=True, nullable=False)
    guildid = Column(BigInteger, primary_key=True, nullable=False)
    channelid = Column(BigInteger)
    messageid = Column(BigInteger)
    reactionsidlist = Column(ARRAY(BigInteger()))


class Pgcractivity(Base):
    __tablename__ = 'pgcractivities'

    instanceid = Column(BigInteger, primary_key=True)
    referenceid = Column(BigInteger)
    directoractivityhash = Column(BigInteger)
    period = Column(DateTime)
    startingphaseindex = Column(SmallInteger)
    mode = Column(SmallInteger)
    modes = Column(ARRAY(SmallInteger()))
    isprivate = Column(Boolean)
    membershiptype = Column(SmallInteger)


class Pgcractivitiesfailtoget(Base):
    __tablename__ = 'pgcractivitiesfailtoget'

    instanceid = Column(BigInteger, primary_key=True)
    period = Column(DateTime)


class Pgcractivitiesusersstat(Base):
    __tablename__ = 'pgcractivitiesusersstats'

    instanceid = Column(BigInteger, primary_key=True, nullable=False)
    membershipid = Column(BigInteger, primary_key=True, nullable=False)
    characterid = Column(BigInteger, primary_key=True, nullable=False)
    characterclass = Column(Text)
    characterlevel = Column(SmallInteger)
    membershiptype = Column(SmallInteger)
    lightlevel = Column(Integer)
    emblemhash = Column(BigInteger)
    standing = Column(SmallInteger)
    assists = Column(Integer)
    completed = Column(SmallInteger)
    deaths = Column(Integer)
    kills = Column(Integer)
    opponentsdefeated = Column(Integer)
    efficiency = Column(Numeric)
    killsdeathsratio = Column(Numeric)
    killsdeathsassists = Column(Numeric)
    score = Column(Integer)
    activitydurationseconds = Column(Integer)
    completionreason = Column(SmallInteger)
    startseconds = Column(Integer)
    timeplayedseconds = Column(Integer)
    playercount = Column(SmallInteger)
    teamscore = Column(Integer)
    precisionkills = Column(Integer)
    weaponkillsgrenade = Column(Integer)
    weaponkillsmelee = Column(Integer)
    weaponkillssuper = Column(Integer)
    weaponkillsability = Column(Integer)


class Pgcractivitiesusersstatsweapon(Base):
    __tablename__ = 'pgcractivitiesusersstatsweapons'

    instanceid = Column(BigInteger, primary_key=True, nullable=False)
    characterid = Column(BigInteger, primary_key=True, nullable=False)
    membershipid = Column(BigInteger, primary_key=True, nullable=False)
    weaponid = Column(BigInteger, primary_key=True, nullable=False)
    uniqueweaponkills = Column(Integer)
    uniqueweaponprecisionkills = Column(Integer)


class Poll(Base):
    __tablename__ = 'polls'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    description = Column(Text)
    data = Column(JSON)
    author_id = Column(BigInteger)
    guild_id = Column(BigInteger)
    channel_id = Column(BigInteger)
    message_id = Column(BigInteger)


class Rssfeeditem(Base):
    __tablename__ = 'rssfeeditems'

    id = Column(Text, primary_key=True)


class Version(Base):
    __tablename__ = 'versions'

    name = Column(Text, primary_key=True)
    version = Column(Text)


# create all tables
async def create_tables(connection: AsyncConnection):
    await connection.run_sync(Base.metadata.drop_all)
