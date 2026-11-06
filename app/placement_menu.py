"""Console menu for placement management."""
from service.placement_service import PlacementService
from exception.custom_exceptions import RPMSException


class PlacementMenu:
    def __init__(self):
        self.service = PlacementService()

    @staticmethod
    def _show_rows(rows):
        if not rows:
            print("\nNo placement records found.")
            return
        print("\n" + "-" * 150)
        print(f"{'ID':<6} {'OFFER':<7} {'CANDIDATE':<22} {'COMPANY':<22} "
              f"{'JOB':<20} {'PACKAGE':<11} {'JOINING DATE':<13} {'STATUS':<16}")
        print("-" * 150)
        for row in rows:
            print(f"{row['placement_id']:<6} {row['offer_id']:<7} "
                  f"{row['candidate_name'][:21]:<22} {row['company_name'][:21]:<22} "
                  f"{row['job_title'][:19]:<20} {str(row['final_package_lpa']):<11} "
                  f"{str(row['actual_joining_date']):<13} "
                  f"{row['placement_status']:<16}")
        print("-" * 150)

    def create(self):
        offer_id = input("Accepted Offer ID: ").strip()
        joining_date = input(
            "Planned/actual joining date (YYYY-MM-DD): "
        ).strip()
        package = input("Final package (LPA): ").strip()
        status = input(
            "Initial status (JOINING_PENDING/JOINED/NOT_JOINED): "
        ).strip() or "JOINING_PENDING"
        remarks = input("Remarks (optional): ").strip()
        placement_id = self.service.create_placement(
            offer_id, joining_date, package, status, remarks
        )
        print(f"Placement record created. Placement ID: {placement_id}")

    def view_all(self):
        self._show_rows(self.service.get_all_placements())

    def view_one(self):
        placement_id = input("Placement ID: ").strip()
        row = self.service.get_placement(placement_id)
        for key, value in row.items():
            print(f"{key.replace('_', ' ').title()}: {value}")

    def update_details(self):
        placement_id = input("Placement ID: ").strip()
        joining_date = input("Updated joining date (YYYY-MM-DD): ").strip()
        package = input("Final package (LPA): ").strip()
        remarks = input("Remarks (optional): ").strip()
        self.service.update_placement(
            placement_id, joining_date, package, remarks
        )
        print("Placement details updated.")

    def update_status(self):
        placement_id = input("Placement ID: ").strip()
        status = input("New status (JOINED/NOT_JOINED): ").strip()
        self.service.update_placement_status(placement_id, status)
        print(f"Placement status updated to {status.upper()}.")
        if status.upper() == "JOINED":
            print("Related application status is now JOINED.")
        elif status.upper() == "NOT_JOINED":
            print("Related application status is now REJECTED.")

    def run(self):
        actions = {
            "1": self.create,
            "2": self.view_all,
            "3": self.view_one,
            "4": self.update_details,
            "5": self.update_status,
        }
        while True:
            print("\n========== PLACEMENT MANAGEMENT ==========")
            print("1. Create Placement Record")
            print("2. View All Placements")
            print("3. View Placement Details")
            print("4. Update Placement Details")
            print("5. Update Placement Status")
            print("0. Back to Main Menu")
            choice = input("Enter choice: ").strip()
            if choice == "0":
                break
            action = actions.get(choice)
            if action is None:
                print("Invalid choice. Select 0-5.")
                continue
            try:
                action()
            except ValueError:
                print("Invalid input. Check the IDs, date and numeric values.")
            except RPMSException as error:
                print(f"Operation failed: {error}")
            except Exception as error:
                print(f"Unexpected error: {error}")
