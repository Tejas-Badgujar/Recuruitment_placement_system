"""Eligibility engine for matching candidates to job requirements."""
from datetime import date
from exception.custom_exceptions import (
    CandidateNotEligibleError,
    ValidationError,
)
from dao.application_dao import ApplicationDAO


class EligibilityService:
    def __init__(self):
        self.dao = ApplicationDAO()

    @staticmethod
    def _normalized(value):
        return (value or "").strip().casefold()

    def check_eligibility(self, candidate_id, job_id):
        try:
            candidate_id = int(candidate_id)
            job_id = int(job_id)
        except (TypeError, ValueError):
            raise ValidationError("Candidate ID and Job ID must be integers.")

        if candidate_id <= 0 or job_id <= 0:
            raise ValidationError("Candidate ID and Job ID must be positive.")

        candidate = self.dao.get_candidate_profile(candidate_id)
        job = self.dao.get_job_profile(job_id)

        reasons = []

        if candidate["candidate_status"] != "ACTIVE":
            reasons.append("Candidate is not active.")

        if job["job_status"] != "OPEN":
            reasons.append("Job is not open.")

        # A company can be deactivated after a job is posted.
        if job["company_status"] != "ACTIVE":
            reasons.append("Recruiting company is inactive.")

        deadline = job["application_deadline"]
        if hasattr(deadline, "date"):
            deadline = deadline.date()
        if isinstance(deadline, str):
            deadline = date.fromisoformat(deadline)
        if deadline < date.today():
            reasons.append("Application deadline has passed.")

        if self._normalized(candidate["qualification"]) != self._normalized(
            job["qualification_required"]
        ):
            reasons.append(
                f"Qualification mismatch: required {job['qualification_required']}."
            )

        required_branch = self._normalized(job["branch_required"])
        candidate_branch = self._normalized(candidate["branch"])
        if required_branch and required_branch != candidate_branch:
            reasons.append(f"Branch mismatch: required {job['branch_required']}.")

        if float(candidate["percentage"]) < float(job["minimum_percentage"]):
            reasons.append(
                f"Percentage below minimum: required {job['minimum_percentage']}%."
            )

        if int(candidate["passing_year"]) != int(job["passing_year"]):
            reasons.append(
                f"Passing year mismatch: required {job['passing_year']}."
            )

        if int(candidate["active_backlogs"]) > int(job["maximum_backlogs"]):
            reasons.append(
                f"Backlogs exceed maximum allowed: {job['maximum_backlogs']}."
            )

        candidate_skills = {
            self._normalized(skill) for skill in candidate["skills"]
        }
        missing_skills = [
            skill for skill in job["required_skills"]
            if self._normalized(skill) not in candidate_skills
        ]
        if missing_skills:
            reasons.append(
                "Missing required skills: " + ", ".join(missing_skills) + "."
            )

        return {
            "eligible": not reasons,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "reasons": reasons if reasons else ["All eligibility criteria satisfied."],
            "missing_skills": missing_skills,
        }
