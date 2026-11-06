"""Custom exceptions used by RPMS."""


class RPMSException(Exception):
    """Base exception for application-level errors."""


class CandidateNotFoundError(RPMSException):
    pass


class DuplicateCandidateError(RPMSException):
    pass


class CompanyNotFoundError(RPMSException):
    pass


class JobNotFoundError(RPMSException):
    pass


class ApplicationNotFoundError(RPMSException):
    pass


class DuplicateApplicationError(RPMSException):
    pass


class CandidateNotEligibleError(RPMSException):
    def __init__(self, reasons):
        self.reasons = reasons if isinstance(reasons, list) else [str(reasons)]
        super().__init__("; ".join(self.reasons))


class ValidationError(RPMSException):
    pass



class InterviewNotFoundError(RPMSException):
    pass


class DuplicateInterviewFeedbackError(RPMSException):
    pass



class OfferNotFoundError(RPMSException):
    pass


class DuplicateOfferError(RPMSException):
    pass



class PlacementNotFoundError(RPMSException):
    pass


class DuplicatePlacementError(RPMSException):
    pass
