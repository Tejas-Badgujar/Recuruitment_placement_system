"""Offer entity model."""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Offer:
    application_id: int
    designation: str
    package_lpa: float
    offer_date: date
    expected_joining_date: Optional[date] = None
    offer_status: str = "PENDING"
    offer_id: Optional[int] = None
