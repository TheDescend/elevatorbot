from Backend.crud.base import CRUDBase
from Backend.database.models import D2SteamPlayer, OwnedEmblem, RssFeedItem


rss_feed_items = CRUDBase(RssFeedItem)
owned_emblems = CRUDBase(OwnedEmblem)
d2_steam_players = CRUDBase(D2SteamPlayer)
