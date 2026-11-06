"""Console menu for offer management."""
from service.offer_service import OfferService
from exception.custom_exceptions import RPMSException


class OfferMenu:
    def __init__(self):
        self.service = OfferService()

    @staticmethod
    def _show_offers(rows):
        if not rows:
            print("\nNo offers found.")
            return
        print("\n" + "-" * 145)
        print(f"{'ID':<6} {'APP':<6} {'CANDIDATE':<22} {'COMPANY':<22} "
              f"{'DESIGNATION':<19} {'PACKAGE':<11} {'OFFER DATE':<12} {'STATUS':<10}")
        print("-" * 145)
        for row in rows:
            print(f"{row['offer_id']:<6} {row['application_id']:<6} "
                  f"{row['candidate_name'][:21]:<22} {row['company_name'][:21]:<22} "
                  f"{row['designation'][:18]:<19} {str(row['package_lpa']):<11} "
                  f"{str(row['offer_date']):<12} {row['offer_status']:<10}")
        print("-" * 145)

    def create(self):
        application_id = input("Selected application ID: ").strip()
        designation = input("Offer designation: ").strip()
        package = input("Package (LPA): ").strip()
        offer_date = input("Offer date (YYYY-MM-DD): ").strip()
        joining_date = input(
            "Expected joining date (YYYY-MM-DD, optional): "
        ).strip()
        offer_id = self.service.create_offer(
            application_id, designation, package, offer_date, joining_date
        )
        print(f"Offer created successfully. Offer ID: {offer_id}")
        print("Application status has been moved from SELECTED to OFFERED.")

    def view_all(self):
        self._show_offers(self.service.get_all_offers())

    def view_one(self):
        offer_id = input("Offer ID: ").strip()
        offer = self.service.get_offer(offer_id)
        for key, value in offer.items():
            print(f"{key.replace('_', ' ').title()}: {value}")

    def update_status(self):
        offer_id = input("Offer ID: ").strip()
        status = input("New status (ACCEPTED/DECLINED/EXPIRED): ").strip()
        self.service.update_offer_status(offer_id, status)
        print(f"Offer status updated to {status.upper()}.")
        if status.upper() in {"DECLINED", "EXPIRED"}:
            print("Related application has been marked REJECTED.")

    def run(self):
        actions = {
            "1": self.create,
            "2": self.view_all,
            "3": self.view_one,
            "4": self.update_status,
        }
        while True:
            print("\n========== OFFER MANAGEMENT ==========")
            print("1. Create Offer")
            print("2. View All Offers")
            print("3. View Offer Details")
            print("4. Update Offer Status")
            print("0. Back to Main Menu")
            choice = input("Enter choice: ").strip()
            if choice == "0":
                break
            action = actions.get(choice)
            if action is None:
                print("Invalid choice. Select 0-4.")
                continue
            try:
                action()
            except ValueError:
                print("Invalid input. Check the entered values.")
            except RPMSException as error:
                print(f"Operation failed: {error}")
            except Exception as error:
                print(f"Unexpected error: {error}")
