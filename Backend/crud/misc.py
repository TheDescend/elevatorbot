from Backend.crud.base import CRUDBase
from Backend.database.models import D2SteamPlayer, RssFeedItem


rss_feed_items = CRUDBase(RssFeedItem)
d2_steam_players = CRUDBase(D2SteamPlayer)
