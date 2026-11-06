"""Database operations for interview scheduling and feedback."""
from mysql.connector import IntegrityError
from util.db_connection import get_connection
from exception.custom_exceptions import (
    ApplicationNotFoundError, InterviewNotFoundError,
    DuplicateInterviewFeedbackError, ValidationError,
)


class InterviewDAO:
    def get_application(self, application_id):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT a.application_id, a.application_status,
                          CONCAT(c.first_name, ' ', c.last_name) AS candidate_name,
                          j.job_title, co.company_name
                   FROM applications a
                   JOIN candidates c ON c.candidate_id=a.candidate_id
                   JOIN jobs j ON j.job_id=a.job_id
                   JOIN companies co ON co.company_id=j.company_id
                   WHERE a.application_id=%s""",
                (application_id,),
            )
            row = cursor.fetchone()
            if row is None:
                raise ApplicationNotFoundError(
                    f"Application ID {application_id} does not exist."
                )
            return row
        finally:
            if connection.is_connected():
                connection.close()

    def create_interview(self, application_id, round_number, interview_date,
                         interview_mode, interviewer_name, meeting_or_venue):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """INSERT INTO interviews
                   (application_id, round_number, interview_date, interview_mode,
                    interviewer_name, meeting_or_venue, interview_status)
                   VALUES (%s, %s, %s, %s, %s, %s, 'SCHEDULED')""",
                (application_id, round_number, interview_date, interview_mode,
                 interviewer_name, meeting_or_venue),
            )
            interview_id = cursor.lastrowid
            # The first scheduled interview moves a shortlisted application
            # into the interview stage. Existing INTERVIEW applications stay there.
            cursor.execute(
                """UPDATE applications SET application_status='INTERVIEW',
                          status_updated_at=CURRENT_TIMESTAMP
                   WHERE application_id=%s AND application_status='SHORTLISTED'""",
                (application_id,),
            )
            connection.commit()
            return interview_id
        except IntegrityError as error:
            connection.rollback()
            if getattr(error, "errno", None) == 1062:
                raise ValidationError(
                    "An interview already exists for this application and round."
                ) from error
            raise
        except Exception:
            connection.rollback()
            raise
        finally:
            if connection.is_connected():
                connection.close()

    def get_all_interviews(self):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT i.interview_id, i.application_id, i.round_number,
                          i.interview_date, i.interview_mode, i.interviewer_name,
                          i.meeting_or_venue, i.interview_status,
                          CONCAT(c.first_name, ' ', c.last_name) AS candidate_name,
                          j.job_title, a.application_status
                   FROM interviews i
                   JOIN applications a ON a.application_id=i.application_id
                   JOIN candidates c ON c.candidate_id=a.candidate_id
                   JOIN jobs j ON j.job_id=a.job_id
                   ORDER BY i.interview_date DESC, i.interview_id DESC"""
            )
            return cursor.fetchall()
        finally:
            if connection.is_connected():
                connection.close()

    def get_interviews_by_application(self, application_id):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT i.interview_id, i.application_id, i.round_number,
                          i.interview_date, i.interview_mode, i.interviewer_name,
                          i.meeting_or_venue, i.interview_status,
                          f.technical_rating, f.communication_rating,
                          f.remarks, f.result
                   FROM interviews i
                   LEFT JOIN interview_feedback f ON f.interview_id=i.interview_id
                   WHERE i.application_id=%s
                   ORDER BY i.round_number""",
                (application_id,),
            )
            return cursor.fetchall()
        finally:
            if connection.is_connected():
                connection.close()

    def get_interview(self, interview_id, cursor=None):
        owns_connection = cursor is None
        connection = get_connection() if owns_connection else None
        try:
            active_cursor = cursor or connection.cursor(dictionary=True)
            active_cursor.execute(
                """SELECT interview_id, application_id, interview_status
                   FROM interviews WHERE interview_id=%s""",
                (interview_id,),
            )
            row = active_cursor.fetchone()
            if row is None:
                raise InterviewNotFoundError(
                    f"Interview ID {interview_id} does not exist."
                )
            return row
        finally:
            if owns_connection and connection.is_connected():
                connection.close()

    def update_interview(self, interview_id, interview_date, interview_mode,
                         interviewer_name, meeting_or_venue, new_status=None):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            row = self.get_interview(interview_id, cursor)
            if row["interview_status"] in ("COMPLETED", "CANCELLED"):
                raise ValidationError(
                    "Completed or cancelled interviews cannot be edited."
                )
            status = new_status or "RESCHEDULED"
            cursor.execute(
                """UPDATE interviews
                   SET interview_date=%s, interview_mode=%s, interviewer_name=%s,
                       meeting_or_venue=%s, interview_status=%s
                   WHERE interview_id=%s""",
                (interview_date, interview_mode, interviewer_name,
                 meeting_or_venue, status, interview_id),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            if connection.is_connected():
                connection.close()

    def set_interview_status(self, interview_id, status):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT interview_status FROM interviews WHERE interview_id=%s",
                (interview_id,),
            )
            row = cursor.fetchone()
            if row is None:
                raise InterviewNotFoundError(
                    f"Interview ID {interview_id} does not exist."
                )
            cursor.execute(
                "UPDATE interviews SET interview_status=%s WHERE interview_id=%s",
                (status, interview_id),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            if connection.is_connected():
                connection.close()

    def add_feedback(self, interview_id, technical_rating,
                     communication_rating, remarks, result):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT interview_status FROM interviews WHERE interview_id=%s",
                (interview_id,),
            )
            interview = cursor.fetchone()
            if interview is None:
                raise InterviewNotFoundError(
                    f"Interview ID {interview_id} does not exist."
                )
            if interview["interview_status"] != "COMPLETED":
                raise ValidationError(
                    "Feedback can be submitted only after the interview is COMPLETED."
                )
            cursor.execute(
                """INSERT INTO interview_feedback
                   (interview_id, technical_rating, communication_rating,
                    remarks, result)
                   VALUES (%s, %s, %s, %s, %s)""",
                (interview_id, technical_rating, communication_rating,
                 remarks, result),
            )
            connection.commit()
            return cursor.lastrowid
        except IntegrityError as error:
            connection.rollback()
            if getattr(error, "errno", None) == 1062:
                raise DuplicateInterviewFeedbackError(
                    "Feedback has already been submitted for this interview."
                ) from error
            raise
        except Exception:
            connection.rollback()
            raise
        finally:
            if connection.is_connected():
                connection.close()

    def update_application_status(self, application_id, new_status):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """UPDATE applications
                   SET application_status=%s, status_updated_at=CURRENT_TIMESTAMP
                   WHERE application_id=%s""",
                (new_status, application_id),
            )
            if cursor.rowcount == 0:
                # The service already checked existence; rowcount may be zero only
                # if the status did not change between checks.
                cursor.execute(
                    "SELECT application_id FROM applications WHERE application_id=%s",
                    (application_id,),
                )
                if cursor.fetchone() is None:
                    raise ApplicationNotFoundError(
                        f"Application ID {application_id} does not exist."
                    )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            if connection.is_connected():
                connection.close()
