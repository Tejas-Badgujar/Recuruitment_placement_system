"""Business rules for offer creation and response tracking."""
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from dao.offer_dao import OfferDAO
from exception.custom_exceptions import ValidationError


class OfferService:
    def __init__(self):
        self.dao = OfferDAO()

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
    def _parse_date(value, label, optional=False):
        if optional and (value is None or str(value).strip() == ""):
            return None
        try:
            return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError(f"{label} must use YYYY-MM-DD format.")

    @staticmethod
    def _parse_package(value):
        try:
            package = Decimal(str(value).strip())
        except (InvalidOperation, AttributeError):
            raise ValidationError("Package must be a valid number in LPA.")
        if not package.is_finite() or package < 0 or package > Decimal("999999.99"):
            raise ValidationError("Package must be between 0 and 999999.99 LPA.")
        return package

    def create_offer(self, application_id, designation, package_lpa,
                     offer_date, expected_joining_date):
        application_id = self._positive_int(application_id, "Application ID")
        designation = (designation or "").strip()
        if not designation:
            raise ValidationError("Designation is required.")
        if len(designation) > 150:
            raise ValidationError("Designation cannot exceed 150 characters.")
        package = self._parse_package(package_lpa)
        issued_on = self._parse_date(offer_date, "Offer date")
        joining_on = self._parse_date(
            expected_joining_date, "Expected joining date", optional=True
        )
        if issued_on > date.today():
            raise ValidationError("Offer date cannot be in the future.")
        if joining_on and joining_on < issued_on:
            raise ValidationError(
                "Expected joining date cannot be earlier than the offer date."
            )

        application = self.dao.get_application(application_id)
        if application["application_status"] != "SELECTED":
            raise ValidationError(
                "An offer can be created only for an application in SELECTED status."
            )
        return self.dao.create_offer(
            application_id, designation, package, issued_on, joining_on
        )

    def get_all_offers(self):
        return self.dao.get_all_offers()

    def get_offer(self, offer_id):
        offer_id = self._positive_int(offer_id, "Offer ID")
        return self.dao.get_offer(offer_id)

    def update_offer_status(self, offer_id, new_status):
        offer_id = self._positive_int(offer_id, "Offer ID")
        new_status = (new_status or "").strip().upper()
        if new_status not in {"ACCEPTED", "DECLINED", "EXPIRED"}:
            raise ValidationError("Status must be ACCEPTED, DECLINED or EXPIRED.")
        offer = self.dao.get_offer(offer_id)
        if offer["offer_status"] != "PENDING":
            raise ValidationError(
                f"Offer is already {offer['offer_status']} and cannot be changed."
            )
        self.dao.update_offer_status(
            offer_id, new_status, offer["application_id"]
        )
