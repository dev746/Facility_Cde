from dataclasses import dataclass
from typing import Optional


@dataclass
class Asset:
    asset_id: str
    name: str
    type: Optional[str] = None
    location: Optional[str] = None
    line: Optional[str] = None
    zone: Optional[str] = None
    status: str = "active"


@dataclass
class Finding:
    finding_id: str
    asset_id: str
    object: Optional[str] = None
    condition: Optional[str] = None
    confidence: Optional[float] = None
    source: Optional[str] = None
    severity: str = "low"
    status: str = "open"
    timestamp: Optional[str] = None


@dataclass
class ExpertNote:
    note_id: str
    asset_id: str
    comment: str
    author: str
    timestamp: str


@dataclass
class User:
    phone: str
    name: str
    role: str
    shift: Optional[str] = None
    line: Optional[str] = None
    is_active: int = 1
