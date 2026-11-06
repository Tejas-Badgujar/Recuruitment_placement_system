"""Job entity model."""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Job:
    company_id: int
    job_title: str
    qualification_required: str
    passing_year: int
    application_deadline: str
    minimum_percentage: float = 0.0
    maximum_backlogs: int = 0
    openings: int = 1
    branch_required: Optional[str] = None
    technology: Optional[str] = None
    location: Optional[str] = None
    package_lpa: Optional[float] = None
    job_description: Optional[str] = None
    job_status: str = "OPEN"
    required_skills: Optional[List[str]] = None
    job_id: Optional[int] = None
