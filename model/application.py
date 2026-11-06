"""Job application entity model."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Application:
    candidate_id: int
    job_id: int
    application_id: Optional[int] = None
    application_status: str = "APPLIED"
    eligibility_remarks: Optional[str] = None
