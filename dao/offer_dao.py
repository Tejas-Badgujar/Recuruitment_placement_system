"""Database operations for job offers."""
from mysql.connector import IntegrityError
from util.db_connection import get_connection
from exception.custom_exceptions import (
    ApplicationNotFoundError, OfferNotFoundError, ValidationError,
    DuplicateOfferError,
)


class OfferDAO:
    def get_application(self, application_id):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT a.application_id, a.application_status,
                          CONCAT(c.first_name, ' ', c.last_name) AS candidate_name,
                          c.email, j.job_title, co.company_name
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

    def create_offer(self, application_id, designation, package_lpa,
                     offer_date, expected_joining_date):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """INSERT INTO offers
                   (application_id, designation, package_lpa, offer_date,
                    expected_joining_date, offer_status)
                   VALUES (%s, %s, %s, %s, %s, 'PENDING')""",
                (application_id, designation, package_lpa, offer_date,
                 expected_joining_date),
            )
            offer_id = cursor.lastrowid
            cursor.execute(
                """UPDATE applications
                   SET application_status='OFFERED',
                       status_updated_at=CURRENT_TIMESTAMP
                   WHERE application_id=%s AND application_status='SELECTED'""",
                (application_id,),
            )
            if cursor.rowcount != 1:
                raise ValidationError(
                    "Application status changed before offer creation. No offer was saved."
                )
            connection.commit()
            return offer_id
        except IntegrityError as error:
            connection.rollback()
            if getattr(error, "errno", None) == 1062:
                raise DuplicateOfferError(
                    "An offer already exists for this application."
                ) from error
            raise
        except Exception:
            connection.rollback()
            raise
        finally:
            if connection.is_connected():
                connection.close()

    def get_all_offers(self):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT o.offer_id, o.application_id, o.designation,
                          o.package_lpa, o.offer_date, o.expected_joining_date,
                          o.offer_status, a.application_status,
                          CONCAT(c.first_name, ' ', c.last_name) AS candidate_name,
                          j.job_title, co.company_name
                   FROM offers o
                   JOIN applications a ON a.application_id=o.application_id
                   JOIN candidates c ON c.candidate_id=a.candidate_id
                   JOIN jobs j ON j.job_id=a.job_id
                   JOIN companies co ON co.company_id=j.company_id
                   ORDER BY o.offer_date DESC, o.offer_id DESC"""
            )
            return cursor.fetchall()
        finally:
            if connection.is_connected():
                connection.close()

    def get_offer(self, offer_id):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT o.offer_id, o.application_id, o.designation,
                          o.package_lpa, o.offer_date, o.expected_joining_date,
                          o.offer_status, a.application_status
                   FROM offers o
                   JOIN applications a ON a.application_id=o.application_id
                   WHERE o.offer_id=%s""",
                (offer_id,),
            )
            row = cursor.fetchone()
            if row is None:
                raise OfferNotFoundError(f"Offer ID {offer_id} does not exist.")
            return row
        finally:
            if connection.is_connected():
                connection.close()

    def update_offer_status(self, offer_id, new_status, application_id):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT offer_status FROM offers WHERE offer_id=%s FOR UPDATE",
                (offer_id,),
            )
            offer = cursor.fetchone()
            if offer is None:
                raise OfferNotFoundError(f"Offer ID {offer_id} does not exist.")
            if offer["offer_status"] != "PENDING":
                raise ValidationError(
                    f"Offer is already {offer['offer_status']}; final offer statuses cannot be changed."
                )
            cursor.execute(
                "UPDATE offers SET offer_status=%s WHERE offer_id=%s",
                (new_status, offer_id),
            )
            if new_status in {"DECLINED", "EXPIRED"}:
                cursor.execute(
                    """UPDATE applications
                       SET application_status='REJECTED',
                           status_updated_at=CURRENT_TIMESTAMP
                       WHERE application_id=%s AND application_status='OFFERED'""",
                    (application_id,),
                )
                if cursor.rowcount != 1:
                    raise ValidationError(
                        "Offer status could not be synchronised with the application."
                    )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            if connection.is_connected():
                connection.close()
