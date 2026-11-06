"""Application workflow service."""
from dao.application_dao import ApplicationDAO
from service.eligibility_service import EligibilityService
from exception.custom_exceptions import (
    CandidateNotEligibleError,
    DuplicateApplicationError,
    ValidationError,
)


class ApplicationService:
    def __init__(self):
        self.dao = ApplicationDAO()
        self.eligibility_service = EligibilityService()

    def check_eligibility(self, candidate_id, job_id):
        return self.eligibility_service.check_eligibility(candidate_id, job_id)

    def apply_for_job(self, candidate_id, job_id):
        result = self.check_eligibility(candidate_id, job_id)
        if not result["eligible"]:
            raise CandidateNotEligibleError(result["reasons"])

        if self.dao.has_applied(candidate_id, job_id):
            raise DuplicateApplicationError(
                "This candidate has already applied for this job."
            )

        remarks = "Eligible: all configured job criteria satisfied."
        application_id = self.dao.create_application(
            int(candidate_id), int(job_id), remarks
        )
        return application_id

    def get_all_applications(self):
        return self.dao.get_all_applications()

    def get_applications_by_candidate(self, candidate_id):
        try:
            candidate_id = int(candidate_id)
        except (TypeError, ValueError):
            raise ValidationError("Candidate ID must be an integer.")
        if candidate_id <= 0:
            raise ValidationError("Candidate ID must be positive.")
        return self.dao.get_applications_by_candidate(candidate_id)
