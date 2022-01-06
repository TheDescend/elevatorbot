import dataclasses
import datetime

from dateutil import parser


@dataclasses.dataclass(unsafe_hash=True)
class _Date:
    _start: datetime.datetime | str
    name: str
    start: datetime.datetime = dataclasses.field(init=False, default=None)

    def __post_init__(self):
        # convert to datetime
        # reset is always at 5pm UTC!
        self.start = parser.parse(f"{self._start} 17:00 UTC")


expansion_dates = [
    _Date("2017-09-06", "D2 Vanilla"),
    _Date("2018-09-04", "Forsaken"),
    _Date("2019-10-01", "Shadowkeep"),
    _Date("2020-11-10", "Beyond Light"),
    _Date("2022-02-22", "Witch Queen"),
]

season_dates = [
    _Date("2017-12-05", "Curse of Osiris"),
    _Date("2018-05-08", "Warmind"),
    _Date("2018-12-04", "Season of the Forge"),
    _Date("2019-03-05", "Season of the Drifter"),
    _Date("2019-06-04", "Season of Opulence"),
    _Date("2019-12-10", "Season of Dawn"),
    _Date("2020-03-10", "Season of the Worthy"),
    _Date("2020-06-09", "Season of Arrivals"),
    _Date("2021-02-09", "Season of the Chosen"),
    _Date("2021-05-11", "Season of the Splicer"),
    _Date("2021-08-24", "Season of the Lost"),
]

other_important_dates_part_1 = [
    _Date("2019-10-04", "GoS"),
    _Date("2019-10-29", "PoH"),
    _Date("2020-01-14", "Corridors of Time"),
    _Date("2020-06-06", "Almighty Live Event"),
    _Date("2020-08-11", "Solstice of Heroes"),
    _Date("2020-11-21", "DSC"),
    _Date("2021-04-20", "Guardian Games"),
    _Date("2020-07-06", "Solstice of Heroes"),
    _Date("2020-10-12", "Festival of the Lost"),
    _Date("2021-12-07", "30th Anniversary Pack"),
]

other_important_dates_part_2 = [
    _Date("2020-02-04", "Empyrean Foundation"),
    _Date("2020-04-21", "Guardian Games"),
    _Date("2020-07-07", "Moments of Triumph"),
    _Date("2021-05-22", "VoG"),
]

season_and_expansion_dates = sorted(expansion_dates + season_dates, key=lambda m: m.start)
other_important_dates = sorted(other_important_dates_part_1 + other_important_dates_part_2, key=lambda m: m.start)
