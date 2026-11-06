"""Company entity model."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Company:
    company_name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_mobile: Optional[str] = None
    company_address: Optional[str] = None
    company_id: Optional[int] = None
    company_status: str = "ACTIVE"
