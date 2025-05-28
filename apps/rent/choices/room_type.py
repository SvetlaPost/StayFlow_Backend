from enum import Enum

class RoomType(str, Enum):
    SINGLE_ROOM = "Single room (studio)"
    ONE_BEDROOM = "One room with a separate bedroom"
    TWO_BEDROOM = "Two rooms with shared bathroom"
    TWO_BEDROOM_ENSUITE = "Two rooms with private bathrooms"
    THREE_BEDROOM = "Three rooms"
    SUITE = "Suite / Apartment"
    SHARED_ROOM = "Shared room / bedspace"
    PRIVATE_ROOM_IN_SHARED = "Private room in a shared apartment"
    LOFT = "Loft / Attic"
    STUDIO = "Studio"


    @classmethod
    def faker_choices(cls):
        return [member.name for member in cls]