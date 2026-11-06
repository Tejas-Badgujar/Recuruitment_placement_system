"""DAO for candidate eligibility data and job applications."""
from mysql.connector import IntegrityError
from util.db_connection import get_connection
from exception.custom_exceptions import (
    CandidateNotFoundError,
    JobNotFoundError,
    DuplicateApplicationError,
)


class ApplicationDAO:
    def get_candidate_profile(self, candidate_id):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT candidate_id, qualification, branch, passing_year,
                          percentage, active_backlogs, candidate_status
                   FROM candidates WHERE candidate_id=%s""",
                (candidate_id,),
            )
            candidate = cursor.fetchone()
            if candidate is None:
                raise CandidateNotFoundError(
                    f"Candidate ID {candidate_id} does not exist."
                )
            cursor.execute(
                "SELECT skill_name FROM candidate_skills WHERE candidate_id=%s",
                (candidate_id,),
            )
            candidate["skills"] = [row["skill_name"] for row in cursor.fetchall()]
            return candidate
        finally:
            if connection.is_connected():
                connection.close()

    def get_job_profile(self, job_id):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT j.job_id, j.company_id, j.qualification_required,
                          j.branch_required, j.passing_year, j.minimum_percentage,
                          j.maximum_backlogs, j.application_deadline, j.job_status,
                          c.company_status
                   FROM jobs j
                   JOIN companies c ON c.company_id=j.company_id
                   WHERE j.job_id=%s""",
                (job_id,),
            )
            job = cursor.fetchone()
            if job is None:
                raise JobNotFoundError(f"Job ID {job_id} does not exist.")
            cursor.execute(
                "SELECT skill_name FROM job_required_skills WHERE job_id=%s",
                (job_id,),
            )
            job["required_skills"] = [
                row["skill_name"] for row in cursor.fetchall()
            ]
            return job
        finally:
            if connection.is_connected():
                connection.close()

    def has_applied(self, candidate_id, job_id):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """SELECT application_id FROM applications
                   WHERE candidate_id=%s AND job_id=%s""",
                (candidate_id, job_id),
            )
            return cursor.fetchone() is not None
        finally:
            if connection.is_connected():
                connection.close()

    def create_application(self, candidate_id, job_id, eligibility_remarks):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """INSERT INTO applications
                   (candidate_id, job_id, application_status,
                    eligibility_checked, eligibility_remarks)
                   VALUES (%s, %s, 'APPLIED', TRUE, %s)""",
                (candidate_id, job_id, eligibility_remarks),
            )
            connection.commit()
            return cursor.lastrowid
        except IntegrityError as error:
            connection.rollback()
            # Unique(candidate_id, job_id) is the final protection against races.
            if getattr(error, "errno", None) == 1062:
                raise DuplicateApplicationError(
                    "This candidate has already applied for this job."
                ) from error
            raise
        except Exception:
            connection.rollback()
            raise
        finally:
            if connection.is_connected():
                connection.close()

    def get_all_applications(self):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT a.application_id, a.candidate_id,
                          CONCAT(c.first_name, ' ', c.last_name) AS candidate_name,
                          a.job_id, j.job_title, co.company_name,
                          a.applied_at, a.application_status,
                          a.eligibility_remarks
                   FROM applications a
                   JOIN candidates c ON c.candidate_id=a.candidate_id
                   JOIN jobs j ON j.job_id=a.job_id
                   JOIN companies co ON co.company_id=j.company_id
                   ORDER BY a.application_id DESC"""
            )
            return cursor.fetchall()
        finally:
            if connection.is_connected():
                connection.close()

    def get_applications_by_candidate(self, candidate_id):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT a.application_id, a.candidate_id, a.job_id,
                          j.job_title, co.company_name, a.applied_at,
                          a.application_status, a.eligibility_remarks
                   FROM applications a
                   JOIN jobs j ON j.job_id=a.job_id
                   JOIN companies co ON co.company_id=j.company_id
                   WHERE a.candidate_id=%s
                   ORDER BY a.application_id DESC""",
                (candidate_id,),
            )
            return cursor.fetchall()
        finally:
            if connection.is_connected():
                connection.close()
