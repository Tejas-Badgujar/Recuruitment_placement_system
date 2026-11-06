"""Candidate entity model."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Candidate:
    first_name: str
    last_name: str
    email: str
    mobile: str
    qualification: str
    passing_year: int
    percentage: float
    active_backlogs: int = 0
    gender: str = "NOT_SPECIFIED"
    date_of_birth: Optional[str] = None
    branch: Optional[str] = None
    address: Optional[str] = None
    resume_path: Optional[str] = None
    candidate_id: Optional[int] = None
    candidate_status: str = "ACTIVE"
