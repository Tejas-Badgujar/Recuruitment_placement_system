"""Console interface for Candidate Management."""
from datetime import date
from service.candidate_service import CandidateService
from exception.custom_exceptions import RPMSException


class CandidateMenu:
    def __init__(self):
        self.service = CandidateService()

    @staticmethod
    def _read_candidate_data(existing=None):
        existing = existing or {}

        def ask(label, key, required=True):
            old_value = existing.get(key)
            prompt = f"{label}"
            if old_value not in (None, ""):
                prompt += f" [{old_value}]"
            value = input(prompt + ": ").strip()
            if value:
                return value
            if old_value not in (None, ""):
                return str(old_value)
            if required:
                return input(f"{label} (required): ").strip()
            return ""

        return {
            "first_name": ask("First name", "first_name"),
            "last_name": ask("Last name", "last_name"),
            "email": ask("Email", "email"),
            "mobile": ask("Mobile", "mobile"),
            "gender": ask("Gender (MALE/FEMALE/OTHER/NOT_SPECIFIED)", "gender", False)
                      or "NOT_SPECIFIED",
            "date_of_birth": ask("Date of birth YYYY-MM-DD", "date_of_birth", False),
            "qualification": ask("Qualification", "qualification"),
            "branch": ask("Branch", "branch", False),
            "passing_year": ask("Passing year", "passing_year"),
            "percentage": ask("Percentage", "percentage"),
            "active_backlogs": ask("Active backlogs", "active_backlogs")
                               or "0",
            "address": ask("Address", "address", False),
            "resume_path": ask("Resume path (optional)", "resume_path", False),
        }

    @staticmethod
    def _display(candidates):
        if not candidates:
            print("\nNo candidate records found.")
            return
        print("\n" + "-" * 125)
        print(f"{'ID':<5} {'NAME':<24} {'EMAIL':<30} {'MOBILE':<16} "
              f"{'YEAR':<7} {'PERCENT':<9} {'BACKLOGS':<9} {'STATUS':<10}")
        print("-" * 125)
        for c in candidates:
            name = f"{c['first_name']} {c['last_name']}"
            print(f"{c['candidate_id']:<5} {name[:23]:<24} "
                  f"{c['email'][:29]:<30} {c['mobile'][:15]:<16} "
                  f"{str(c['passing_year']):<7} {str(c['percentage']):<9} "
                  f"{c['active_backlogs']:<9} {c['candidate_status']:<10}")
        print("-" * 125)

    def add_candidate(self):
        data = self._read_candidate_data()
        candidate_id = self.service.add_candidate(data)
        print(f"Candidate created successfully. Candidate ID: {candidate_id}")

    def update_candidate(self):
        candidate_id = int(input("Enter candidate ID to update: "))
        existing = self.service.get_candidate(candidate_id)
        if existing["candidate_status"] == "INACTIVE":
            print("Inactive candidates cannot be updated.")
            return
        data = self._read_candidate_data(existing)
        self.service.update_candidate(candidate_id, data)
        print("Candidate updated successfully.")

    def search_candidate(self):
        keyword = input("Enter candidate ID, name, email or mobile: ")
        self._display(self.service.search_candidates(keyword))

    def view_all_candidates(self):
        self._display(self.service.get_all_candidates())

    def deactivate_candidate(self):
        candidate_id = int(input("Enter candidate ID to deactivate: "))
        confirm = input("Deactivate this candidate? (y/n): ").strip().lower()
        if confirm == "y":
            self.service.deactivate_candidate(candidate_id)
            print("Candidate deactivated. Record was not deleted.")
        else:
            print("Operation cancelled.")

    def run(self):
        while True:
            print("\n========== CANDIDATE MANAGEMENT ==========")
            print("1. Add Candidate")
            print("2. Update Candidate")
            print("3. Search Candidate")
            print("4. View All Candidates")
            print("5. Deactivate Candidate")
            print("0. Back to Main Menu")
            choice = input("Enter choice: ").strip()

            actions = {
                "1": self.add_candidate,
                "2": self.update_candidate,
                "3": self.search_candidate,
                "4": self.view_all_candidates,
                "5": self.deactivate_candidate,
            }
            if choice == "0":
                break
            action = actions.get(choice)
            if action is None:
                print("Invalid choice. Select 0-5.")
                continue
            try:
                action()
            except ValueError:
                print("Invalid numeric input. Please check the value and try again.")
            except RPMSException as error:
                print(f"Operation failed: {error}")
            except Exception as error:
                print(f"Unexpected error: {error}")
