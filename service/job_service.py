"""Business rules and validation for job operations."""
from datetime import date
from model.job import Job
from dao.job_dao import JobDAO
from exception.custom_exceptions import ValidationError, JobNotFoundError


class JobService:
    ALLOWED_STATUSES = {"OPEN", "CLOSED", "ON_HOLD"}

    def __init__(self):
        self.dao = JobDAO()

    @staticmethod
    def _required(data, key, label):
        value = data.get(key)
        if value is None or str(value).strip() == "":
            raise ValidationError(f"{label} is required.")
        return str(value).strip()

    @staticmethod
    def _optional(data, key):
        value = data.get(key)
        return str(value).strip() if value is not None and str(value).strip() else None

    @staticmethod
    def _skills(value):
        if value is None:
            return []
        if isinstance(value, str):
            values = value.split(",")
        else:
            values = value
        result = []
        seen = set()
        for item in values:
            skill = str(item).strip()
            if skill and skill.casefold() not in seen:
                result.append(skill)
                seen.add(skill.casefold())
        return result

    def _build_job(self, data):
        try:
            company_id = int(self._required(data, "company_id", "Company ID"))
            openings = int(data.get("openings", 1))
            passing_year = int(self._required(data, "passing_year", "Passing year"))
            minimum_percentage = float(data.get("minimum_percentage", 0))
            maximum_backlogs = int(data.get("maximum_backlogs", 0))
            package_value = self._optional(data, "package_lpa")
            package_lpa = float(package_value) if package_value else None
        except (TypeError, ValueError):
            raise ValidationError(
                "Company ID, openings, passing year, percentage, backlogs and package must be numeric."
            )

        if company_id <= 0:
            raise ValidationError("Company ID must be a positive number.")
        if openings <= 0:
            raise ValidationError("Openings must be greater than zero.")
        if not 1901 <= passing_year <= 2155:
            raise ValidationError("Passing year must be between 1901 and 2155.")
        if not 0 <= minimum_percentage <= 100:
            raise ValidationError("Minimum percentage must be between 0 and 100.")
        if maximum_backlogs < 0:
            raise ValidationError("Maximum backlogs cannot be negative.")
        if package_lpa is not None and package_lpa < 0:
            raise ValidationError("Package cannot be negative.")

        deadline_text = self._required(
            data, "application_deadline", "Application deadline"
        )
        try:
            deadline = date.fromisoformat(deadline_text)
        except ValueError:
            raise ValidationError("Deadline must use YYYY-MM-DD format.")
        if deadline < date.today():
            raise ValidationError("Application deadline cannot be in the past.")

        title = self._required(data, "job_title", "Job title")
        qualification = self._required(
            data, "qualification_required", "Required qualification"
        )

        return Job(
            company_id=company_id,
            job_title=title,
            qualification_required=qualification,
            passing_year=passing_year,
            application_deadline=deadline.isoformat(),
            minimum_percentage=minimum_percentage,
            maximum_backlogs=maximum_backlogs,
            openings=openings,
            branch_required=self._optional(data, "branch_required"),
            technology=self._optional(data, "technology"),
            location=self._optional(data, "location"),
            package_lpa=package_lpa,
            job_description=self._optional(data, "job_description"),
            required_skills=self._skills(data.get("required_skills")),
        )

    def create_job(self, data):
        return self.dao.add(self._build_job(data))

    def update_job(self, job_id, data):
        if not self.dao.get_by_id(job_id):
            raise JobNotFoundError("Job ID does not exist.")
        return self.dao.update(job_id, self._build_job(data))

    def get_job(self, job_id):
        job = self.dao.get_by_id(job_id)
        if not job:
            raise JobNotFoundError("Job not found.")
        return job

    def get_open_jobs(self):
        return self.dao.get_open_jobs()

    def search_jobs(self, keyword):
        if not keyword or not keyword.strip():
            raise ValidationError("Enter a job title, company, technology or location.")
        return self.dao.search(keyword.strip())

    def close_job(self, job_id):
        return self.dao.close(job_id)
