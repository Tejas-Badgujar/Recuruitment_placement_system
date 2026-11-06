"""Data Access Object for candidate database operations."""
from mysql.connector import IntegrityError
from util.db_connection import get_connection
from exception.custom_exceptions import (
    CandidateNotFoundError,
    DuplicateCandidateError,
)


class CandidateDAO:
    def add(self, candidate):
        sql = """
            INSERT INTO candidates
            (first_name, last_name, email, mobile, gender, date_of_birth,
             qualification, branch, passing_year, percentage,
             active_backlogs, address, resume_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            candidate.first_name, candidate.last_name, candidate.email,
            candidate.mobile, candidate.gender, candidate.date_of_birth,
            candidate.qualification, candidate.branch, candidate.passing_year,
            candidate.percentage, candidate.active_backlogs,
            candidate.address, candidate.resume_path,
        )
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(sql, values)
            connection.commit()
            return cursor.lastrowid
        except IntegrityError as error:
            connection.rollback()
            message = str(error).lower()
            if "email" in message or "mobile" in message or "duplicate" in message:
                raise DuplicateCandidateError(
                    "Email address or mobile number already exists."
                ) from error
            raise
        finally:
            if connection.is_connected():
                connection.close()

    def update(self, candidate_id, candidate):
        sql = """
            UPDATE candidates
            SET first_name=%s, last_name=%s, email=%s, mobile=%s,
                gender=%s, date_of_birth=%s, qualification=%s, branch=%s,
                passing_year=%s, percentage=%s, active_backlogs=%s,
                address=%s, resume_path=%s
            WHERE candidate_id=%s AND candidate_status <> 'INACTIVE'
        """
        values = (
            candidate.first_name, candidate.last_name, candidate.email,
            candidate.mobile, candidate.gender, candidate.date_of_birth,
            candidate.qualification, candidate.branch, candidate.passing_year,
            candidate.percentage, candidate.active_backlogs,
            candidate.address, candidate.resume_path, candidate_id,
        )
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(sql, values)
            if cursor.rowcount == 0:
                # MySQL may report zero changed rows when the submitted values
                # are identical to the existing values. Check existence/status
                # before treating zero rowcount as a missing candidate.
                cursor.execute(
                    """SELECT candidate_id FROM candidates
                       WHERE candidate_id=%s AND candidate_status <> 'INACTIVE'""",
                    (candidate_id,),
                )
                if cursor.fetchone() is None:
                    connection.rollback()
                    raise CandidateNotFoundError(
                        "Candidate does not exist or is inactive."
                    )
            connection.commit()
            return True
        except IntegrityError as error:
            connection.rollback()
            raise DuplicateCandidateError(
                "Email address or mobile number already belongs to another candidate."
            ) from error
        finally:
            if connection.is_connected():
                connection.close()

    def get_by_id(self, candidate_id):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM candidates WHERE candidate_id=%s",
                (candidate_id,),
            )
            return cursor.fetchone()
        finally:
            if connection.is_connected():
                connection.close()

    def get_all(self):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM candidates ORDER BY candidate_id DESC"
            )
            return cursor.fetchall()
        finally:
            if connection.is_connected():
                connection.close()

    def search(self, keyword):
        sql = """
            SELECT * FROM candidates
            WHERE CAST(candidate_id AS CHAR) LIKE %s
               OR first_name LIKE %s
               OR last_name LIKE %s
               OR CONCAT(first_name, ' ', last_name) LIKE %s
               OR email LIKE %s
               OR mobile LIKE %s
            ORDER BY candidate_id DESC
        """
        pattern = f"%{keyword}%"
        values = (pattern, pattern, pattern, pattern, pattern, pattern)
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql, values)
            return cursor.fetchall()
        finally:
            if connection.is_connected():
                connection.close()

    def deactivate(self, candidate_id):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """UPDATE candidates SET candidate_status='INACTIVE'
                   WHERE candidate_id=%s AND candidate_status='ACTIVE'""",
                (candidate_id,),
            )
            if cursor.rowcount == 0:
                connection.rollback()
                raise CandidateNotFoundError(
                    "Active candidate not found with that ID."
                )
            connection.commit()
            return True
        finally:
            if connection.is_connected():
                connection.close()
