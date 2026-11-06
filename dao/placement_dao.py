"""Database operations for placement records."""
from mysql.connector import IntegrityError
from util.db_connection import get_connection
from exception.custom_exceptions import (
    OfferNotFoundError, PlacementNotFoundError,
    DuplicatePlacementError, ValidationError,
)


class PlacementDAO:
    def get_offer(self, offer_id):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT o.offer_id, o.application_id, o.designation,
                          o.package_lpa, o.offer_status, o.expected_joining_date,
                          a.application_status,
                          CONCAT(c.first_name, ' ', c.last_name) AS candidate_name,
                          c.email, j.job_title, co.company_name
                   FROM offers o
                   JOIN applications a ON a.application_id=o.application_id
                   JOIN candidates c ON c.candidate_id=a.candidate_id
                   JOIN jobs j ON j.job_id=a.job_id
                   JOIN companies co ON co.company_id=j.company_id
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

    def create_placement(self, offer_id, joining_date, final_package,
                         placement_status, remarks):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT application_id, offer_status FROM offers WHERE offer_id=%s FOR UPDATE",
                (offer_id,),
            )
            offer = cursor.fetchone()
            if offer is None:
                raise OfferNotFoundError(f"Offer ID {offer_id} does not exist.")
            if offer["offer_status"] != "ACCEPTED":
                raise ValidationError(
                    "A placement can be recorded only for an ACCEPTED offer."
                )
            cursor.execute(
                """INSERT INTO placements
                   (offer_id, actual_joining_date, final_package_lpa,
                    placement_status, remarks)
                   VALUES (%s, %s, %s, %s, %s)""",
                (offer_id, joining_date, final_package, placement_status, remarks),
            )
            placement_id = cursor.lastrowid
            if placement_status == "JOINED":
                cursor.execute(
                    """UPDATE applications
                       SET application_status='JOINED',
                           status_updated_at=CURRENT_TIMESTAMP
                       WHERE application_id=%s AND application_status='OFFERED'""",
                    (offer["application_id"],),
                )
                if cursor.rowcount != 1:
                    raise ValidationError(
                        "Could not move application from OFFERED to JOINED."
                    )
            connection.commit()
            return placement_id
        except IntegrityError as error:
            connection.rollback()
            if getattr(error, "errno", None) == 1062:
                raise DuplicatePlacementError(
                    "A placement record already exists for this offer."
                ) from error
            raise
        except Exception:
            connection.rollback()
            raise
        finally:
            if connection.is_connected():
                connection.close()

    def get_all_placements(self):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT p.placement_id, p.offer_id, p.actual_joining_date,
                          p.final_package_lpa, p.placement_status, p.remarks,
                          o.application_id, o.designation, o.offer_status,
                          CONCAT(c.first_name, ' ', c.last_name) AS candidate_name,
                          c.email, j.job_title, co.company_name,
                          a.application_status
                   FROM placements p
                   JOIN offers o ON o.offer_id=p.offer_id
                   JOIN applications a ON a.application_id=o.application_id
                   JOIN candidates c ON c.candidate_id=a.candidate_id
                   JOIN jobs j ON j.job_id=a.job_id
                   JOIN companies co ON co.company_id=j.company_id
                   ORDER BY p.created_at DESC, p.placement_id DESC"""
            )
            return cursor.fetchall()
        finally:
            if connection.is_connected():
                connection.close()

    def get_placement(self, placement_id):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT p.placement_id, p.offer_id, p.actual_joining_date,
                          p.final_package_lpa, p.placement_status, p.remarks,
                          o.application_id, o.designation, o.offer_status,
                          a.application_status,
                          CONCAT(c.first_name, ' ', c.last_name) AS candidate_name,
                          c.email, j.job_title, co.company_name
                   FROM placements p
                   JOIN offers o ON o.offer_id=p.offer_id
                   JOIN applications a ON a.application_id=o.application_id
                   JOIN candidates c ON c.candidate_id=a.candidate_id
                   JOIN jobs j ON j.job_id=a.job_id
                   JOIN companies co ON co.company_id=j.company_id
                   WHERE p.placement_id=%s""",
                (placement_id,),
            )
            row = cursor.fetchone()
            if row is None:
                raise PlacementNotFoundError(
                    f"Placement ID {placement_id} does not exist."
                )
            return row
        finally:
            if connection.is_connected():
                connection.close()

    def update_placement(self, placement_id, joining_date, final_package, remarks):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT placement_status FROM placements WHERE placement_id=%s FOR UPDATE",
                (placement_id,),
            )
            row = cursor.fetchone()
            if row is None:
                raise PlacementNotFoundError(
                    f"Placement ID {placement_id} does not exist."
                )
            current_status = row[0]
            if current_status in ("JOINED", "NOT_JOINED"):
                raise ValidationError(
                    "Finalised placement records cannot be edited."
                )
            cursor.execute(
                """UPDATE placements
                   SET actual_joining_date=%s, final_package_lpa=%s, remarks=%s
                   WHERE placement_id=%s""",
                (joining_date, final_package, remarks, placement_id),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            if connection.is_connected():
                connection.close()

    def update_placement_status(self, placement_id, new_status):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT p.placement_status, o.application_id, a.application_status
                   FROM placements p
                   JOIN offers o ON o.offer_id=p.offer_id
                   JOIN applications a ON a.application_id=o.application_id
                   WHERE p.placement_id=%s FOR UPDATE""",
                (placement_id,),
            )
            row = cursor.fetchone()
            if row is None:
                raise PlacementNotFoundError(
                    f"Placement ID {placement_id} does not exist."
                )
            if row["placement_status"] in ("JOINED", "NOT_JOINED"):
                raise ValidationError(
                    f"Placement is already finalised as {row['placement_status']}."
                )
            if row["application_status"] != "OFFERED":
                raise ValidationError(
                    "Only an OFFERED application can be finalised as a placement."
                )
            cursor.execute(
                "UPDATE placements SET placement_status=%s WHERE placement_id=%s",
                (new_status, placement_id),
            )
            if new_status == "JOINED":
                cursor.execute(
                    """UPDATE applications
                       SET application_status='JOINED',
                           status_updated_at=CURRENT_TIMESTAMP
                       WHERE application_id=%s AND application_status='OFFERED'""",
                    (row["application_id"],),
                )
                if cursor.rowcount != 1:
                    raise ValidationError(
                        "Could not synchronize application status to JOINED."
                    )
            elif new_status == "NOT_JOINED":
                cursor.execute(
                    """UPDATE applications
                       SET application_status='REJECTED',
                           status_updated_at=CURRENT_TIMESTAMP
                       WHERE application_id=%s AND application_status='OFFERED'""",
                    (row["application_id"],),
                )
                if cursor.rowcount != 1:
                    raise ValidationError(
                        "Could not synchronize application status to REJECTED."
                    )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            if connection.is_connected():
                connection.close()
