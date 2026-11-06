"""Interview entity model."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Interview:
    application_id: int
    round_number: int
    interview_date: datetime
    interview_mode: str
    interviewer_name: Optional[str] = None
    meeting_or_venue: Optional[str] = None
    interview_id: Optional[int] = None
    interview_status: str = "SCHEDULED"
