"""Business rules and validation for candidate operations."""
import re
from datetime import date
from model.candidate import Candidate
from dao.candidate_dao import CandidateDAO
from exception.custom_exceptions import ValidationError, CandidateNotFoundError


class CandidateService:
    ALLOWED_GENDERS = {"MALE", "FEMALE", "OTHER", "NOT_SPECIFIED"}

    def __init__(self):
        self.dao = CandidateDAO()

    @staticmethod
    def _validate_text(value, field_name):
        if not value or not value.strip():
            raise ValidationError(f"{field_name} is required.")
        return value.strip()

    def _build_candidate(self, data):
        first_name = self._validate_text(data.get("first_name"), "First name")
        last_name = self._validate_text(data.get("last_name"), "Last name")
        qualification = self._validate_text(
            data.get("qualification"), "Qualification"
        )
        email = self._validate_text(data.get("email"), "Email").lower()
        mobile = self._validate_text(data.get("mobile"), "Mobile")

        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise ValidationError("Enter a valid email address.")
        if not re.fullmatch(r"[0-9+() -]{7,20}", mobile):
            raise ValidationError("Mobile must contain 7-20 valid phone characters.")

        try:
            passing_year = int(data.get("passing_year"))
            percentage = float(data.get("percentage"))
            backlogs = int(data.get("active_backlogs", 0))
        except (TypeError, ValueError):
            raise ValidationError(
                "Passing year, percentage and backlog count must be numeric."
            )

        if not 1901 <= passing_year <= 2155:
            raise ValidationError("Passing year must be between 1901 and 2155.")
        if not 0 <= percentage <= 100:
            raise ValidationError("Percentage must be between 0 and 100.")
        if backlogs < 0:
            raise ValidationError("Backlog count cannot be negative.")

        gender = (data.get("gender") or "NOT_SPECIFIED").upper().strip()
        if gender not in self.ALLOWED_GENDERS:
            raise ValidationError("Invalid gender value.")

        dob = data.get("date_of_birth") or None
        if dob:
            try:
                parsed_dob = date.fromisoformat(dob)
                if parsed_dob >= date.today():
                    raise ValidationError("Date of birth must be in the past.")
            except ValueError:
                raise ValidationError("Date of birth must use YYYY-MM-DD format.")

        return Candidate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile=mobile,
            qualification=qualification,
            passing_year=passing_year,
            percentage=percentage,
            active_backlogs=backlogs,
            gender=gender,
            date_of_birth=dob,
            branch=(data.get("branch") or "").strip() or None,
            address=(data.get("address") or "").strip() or None,
            resume_path=(data.get("resume_path") or "").strip() or None,
        )

    def add_candidate(self, data):
        candidate = self._build_candidate(data)
        return self.dao.add(candidate)

    def update_candidate(self, candidate_id, data):
        if not self.dao.get_by_id(candidate_id):
            raise CandidateNotFoundError("Candidate ID does not exist.")
        candidate = self._build_candidate(data)
        return self.dao.update(candidate_id, candidate)

    def get_candidate(self, candidate_id):
        candidate = self.dao.get_by_id(candidate_id)
        if not candidate:
            raise CandidateNotFoundError("Candidate not found.")
        return candidate

    def get_all_candidates(self):
        return self.dao.get_all()

    def search_candidates(self, keyword):
        if not keyword or not keyword.strip():
            raise ValidationError("Enter an ID, name, email or mobile to search.")
        return self.dao.search(keyword.strip())

    def deactivate_candidate(self, candidate_id):
        return self.dao.deactivate(candidate_id)
