"""Business rules for interview workflow and application status transitions."""
from datetime import datetime
from dao.interview_dao import InterviewDAO
from exception.custom_exceptions import ValidationError

# Deliberately strict: no skipping stages and no moving backwards.
ALLOWED_APPLICATION_TRANSITIONS = {
    "APPLIED": {"SHORTLISTED", "REJECTED"},
    "SHORTLISTED": {"INTERVIEW", "REJECTED"},
    "INTERVIEW": {"SELECTED", "REJECTED"},
    "SELECTED": {"OFFERED", "REJECTED"},
    "OFFERED": {"JOINED", "REJECTED"},
    "JOINED": set(),
    "REJECTED": set(),
}


class InterviewService:
    def __init__(self):
        self.dao = InterviewDAO()

    @staticmethod
    def _positive_int(value, label):
        try:
            number = int(value)
        except (TypeError, ValueError):
            raise ValidationError(f"{label} must be a whole number.")
        if number <= 0:
            raise ValidationError(f"{label} must be greater than zero.")
        return number

    @staticmethod
    def _parse_datetime(value):
        try:
            parsed = datetime.strptime(value.strip(), "%Y-%m-%d %H:%M")
        except (AttributeError, ValueError):
            raise ValidationError(
                "Date/time must use YYYY-MM-DD HH:MM format (24-hour time)."
            )
        if parsed <= datetime.now():
            raise ValidationError("Interview date and time must be in the future.")
        return parsed

    @staticmethod
    def _optional_text(value, label, max_length):
        value = value.strip() if value else None
        if value and len(value) > max_length:
            raise ValidationError(f"{label} cannot exceed {max_length} characters.")
        return value

    def schedule_interview(self, application_id, round_number, interview_date,
                           interview_mode, interviewer_name, meeting_or_venue):
        application_id = self._positive_int(application_id, "Application ID")
        round_number = self._positive_int(round_number, "Round number")
        parsed_date = self._parse_datetime(interview_date)
        mode = (interview_mode or "").strip().upper()
        if mode not in {"ONLINE", "OFFLINE"}:
            raise ValidationError("Interview mode must be ONLINE or OFFLINE.")

        application = self.dao.get_application(application_id)
        if application["application_status"] not in {"SHORTLISTED", "INTERVIEW"}:
            raise ValidationError(
                "Only SHORTLISTED or INTERVIEW applications can be scheduled."
            )

        interviewer_name = self._optional_text(
            interviewer_name, "Interviewer name", 120
        )
        meeting_or_venue = self._optional_text(
            meeting_or_venue, "Meeting link/venue", 255
        )
        if mode == "ONLINE" and not meeting_or_venue:
            raise ValidationError("Provide the online meeting link for ONLINE mode.")
        return self.dao.create_interview(
            application_id, round_number, parsed_date, mode,
            interviewer_name, meeting_or_venue
        )

    def get_all_interviews(self):
        return self.dao.get_all_interviews()

    def get_interviews_by_application(self, application_id):
        application_id = self._positive_int(application_id, "Application ID")
        self.dao.get_application(application_id)
        return self.dao.get_interviews_by_application(application_id)

    def reschedule_interview(self, interview_id, interview_date, interview_mode,
                             interviewer_name, meeting_or_venue):
        interview_id = self._positive_int(interview_id, "Interview ID")
        parsed_date = self._parse_datetime(interview_date)
        mode = (interview_mode or "").strip().upper()
        if mode not in {"ONLINE", "OFFLINE"}:
            raise ValidationError("Interview mode must be ONLINE or OFFLINE.")
        interviewer_name = self._optional_text(
            interviewer_name, "Interviewer name", 120
        )
        meeting_or_venue = self._optional_text(
            meeting_or_venue, "Meeting link/venue", 255
        )
        if mode == "ONLINE" and not meeting_or_venue:
            raise ValidationError("Provide the online meeting link for ONLINE mode.")
        self.dao.update_interview(
            interview_id, parsed_date, mode, interviewer_name,
            meeting_or_venue, "RESCHEDULED"
        )

    def update_interview_status(self, interview_id, status):
        interview_id = self._positive_int(interview_id, "Interview ID")
        status = (status or "").strip().upper()
        if status not in {"COMPLETED", "CANCELLED"}:
            raise ValidationError("Status must be COMPLETED or CANCELLED.")
        current = self.dao.get_interview(interview_id)
        if current["interview_status"] in {"COMPLETED", "CANCELLED"}:
            raise ValidationError("This interview is already finalised.")
        self.dao.set_interview_status(interview_id, status)

    def submit_feedback(self, interview_id, technical_rating,
                        communication_rating, remarks, result):
        interview_id = self._positive_int(interview_id, "Interview ID")
        result = (result or "").strip().upper()
        if result not in {"PASS", "FAIL", "ON_HOLD"}:
            raise ValidationError("Result must be PASS, FAIL or ON_HOLD.")

        def rating(value, label):
            if value is None or str(value).strip() == "":
                return None
            try:
                number = float(value)
            except (TypeError, ValueError):
                raise ValidationError(f"{label} must be a number from 0 to 10.")
            if not 0 <= number <= 10:
                raise ValidationError(f"{label} must be between 0 and 10.")
            return number

        technical_rating = rating(technical_rating, "Technical rating")
        communication_rating = rating(
            communication_rating, "Communication rating"
        )
        remarks = self._optional_text(remarks, "Remarks", 10000)
        return self.dao.add_feedback(
            interview_id, technical_rating, communication_rating, remarks, result
        )

    def update_application_status(self, application_id, new_status):
        application_id = self._positive_int(application_id, "Application ID")
        new_status = (new_status or "").strip().upper()
        valid = set(ALLOWED_APPLICATION_TRANSITIONS)
        if new_status not in valid:
            raise ValidationError(f"Status must be one of: {', '.join(sorted(valid))}.")
        application = self.dao.get_application(application_id)
        current = application["application_status"]
        if new_status not in ALLOWED_APPLICATION_TRANSITIONS[current]:
            allowed = ALLOWED_APPLICATION_TRANSITIONS[current]
            options = ", ".join(sorted(allowed)) if allowed else "no further status"
            raise ValidationError(
                f"Invalid application status transition: {current} -> {new_status}. "
                f"Allowed next status: {options}."
            )
        self.dao.update_application_status(application_id, new_status)
