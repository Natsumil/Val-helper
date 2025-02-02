from pydantic.dataclasses import dataclass
from typing import List, Optional, Any


@dataclass
class EntitlementsTokenResponse:
    accessToken: Optional[str] = None
    entitlements: Optional[List[Any]] = None
    issuer: Optional[str] = None
    subject: Optional[str] = None
    token: Optional[str] = None


@dataclass
class Friend:
    activePlatform: Optional[str] = None
    displayGroup: Optional[str] = None
    gamename: Optional[str] = None
    gametag: Optional[str] = None
    group: Optional[str] = None
    lastonlinets: Optional[int] = None
    name: Optional[str] = None
    note: Optional[str] = None
    pid: Optional[str] = None
    puuid: Optional[str] = None
    region: Optional[str] = None


@dataclass
class GetFriendsResponse:
    friends: Optional[List[Friend]] = None