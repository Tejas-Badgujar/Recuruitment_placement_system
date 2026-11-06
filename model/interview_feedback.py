"""Interview feedback entity model."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class InterviewFeedback:
    interview_id: int
    result: str
    technical_rating: Optional[float] = None
    communication_rating: Optional[float] = None
    remarks: Optional[str] = None
