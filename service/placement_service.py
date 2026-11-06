"""Business rules for placement tracking."""
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from dao.placement_dao import PlacementDAO
from exception.custom_exceptions import ValidationError


class PlacementService:
    def __init__(self):
        self.dao = PlacementDAO()

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
    def _parse_date(value, label):
        try:
            return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            raise ValidationError(f"{label} must use YYYY-MM-DD format.")

    @staticmethod
    def _parse_package(value):
        try:
            amount = Decimal(str(value).strip())
        except (InvalidOperation, AttributeError):
            raise ValidationError("Final package must be a valid number in LPA.")
        if not amount.is_finite() or amount < 0 or amount > Decimal("999999.99"):
            raise ValidationError("Final package must be between 0 and 999999.99 LPA.")
        return amount

    @staticmethod
    def _remarks(value):
        value = value.strip() if value else None
        if value and len(value) > 500:
            raise ValidationError("Remarks cannot exceed 500 characters.")
        return value

    def create_placement(self, offer_id, joining_date, final_package,
                         placement_status, remarks):
        offer_id = self._positive_int(offer_id, "Offer ID")
        joining_date = self._parse_date(joining_date, "Joining date")
        package = self._parse_package(final_package)
        status = (placement_status or "JOINING_PENDING").strip().upper()
        if status not in {"JOINING_PENDING", "JOINED", "NOT_JOINED"}:
            raise ValidationError(
                "Status must be JOINING_PENDING, JOINED or NOT_JOINED."
            )
        if status == "JOINED" and joining_date > date.today():
            raise ValidationError("A JOINED candidate cannot have a future joining date.")
        remarks = self._remarks(remarks)
        offer = self.dao.get_offer(offer_id)
        if offer["offer_status"] != "ACCEPTED":
            raise ValidationError(
                "Only an ACCEPTED offer can be converted into a placement."
            )
        return self.dao.create_placement(
            offer_id, joining_date, package, status, remarks
        )

    def get_all_placements(self):
        return self.dao.get_all_placements()

    def get_placement(self, placement_id):
        return self.dao.get_placement(
            self._positive_int(placement_id, "Placement ID")
        )

    def update_placement(self, placement_id, joining_date, final_package, remarks):
        placement_id = self._positive_int(placement_id, "Placement ID")
        joining_date = self._parse_date(joining_date, "Joining date")
        package = self._parse_package(final_package)
        remarks = self._remarks(remarks)
        self.dao.update_placement(
            placement_id, joining_date, package, remarks
        )

    def update_placement_status(self, placement_id, new_status):
        placement_id = self._positive_int(placement_id, "Placement ID")
        status = (new_status or "").strip().upper()
        if status not in {"JOINING_PENDING", "JOINED", "NOT_JOINED"}:
            raise ValidationError(
                "Status must be JOINING_PENDING, JOINED or NOT_JOINED."
            )
        placement = self.dao.get_placement(placement_id)
        current = placement["placement_status"]
        if current in {"JOINED", "NOT_JOINED"}:
            raise ValidationError("Finalised placement status cannot be changed.")
        if status == "JOINING_PENDING":
            raise ValidationError(
                "JOINING_PENDING is the initial status; choose JOINED or NOT_JOINED to finalise."
            )
        if status == "JOINED" and placement["actual_joining_date"] > date.today():
            raise ValidationError(
                "A candidate cannot be marked JOINED before the joining date."
            )
        self.dao.update_placement_status(placement_id, status)
