"""Placement entity model."""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Placement:
    offer_id: int
    actual_joining_date: date
    final_package_lpa: float
    placement_status: str = "JOINING_PENDING"
    remarks: Optional[str] = None
    placement_id: Optional[int] = None
