"""Console interface for Eligibility and Job Applications."""
from service.application_service import ApplicationService
from exception.custom_exceptions import RPMSException


class ApplicationMenu:
    def __init__(self):
        self.service = ApplicationService()

    @staticmethod
    def _print_eligibility(result):
        print("\n========== ELIGIBILITY RESULT ==========")
        print(f"Candidate ID: {result['candidate_id']}")
        print(f"Job ID: {result['job_id']}")
        print("Status:", "ELIGIBLE" if result["eligible"] else "NOT ELIGIBLE")
        for reason in result["reasons"]:
            print(" -", reason)

    @staticmethod
    def _display_applications(rows):
        if not rows:
            print("\nNo applications found.")
            return
        print("\n" + "-" * 125)
        print(f"{'APP ID':<8} {'CANDIDATE':<24} {'JOB TITLE':<27} "
              f"{'COMPANY':<23} {'APPLIED AT':<21} {'STATUS':<12}")
        print("-" * 125)
        for row in rows:
            applied_at = str(row["applied_at"])
            print(f"{row['application_id']:<8} "
                  f"{row['candidate_name'][:23]:<24} "
                  f"{row['job_title'][:26]:<27} "
                  f"{row['company_name'][:22]:<23} "
                  f"{applied_at[:20]:<21} "
                  f"{row['application_status']:<12}")
        print("-" * 125)

    def check_eligibility(self):
        candidate_id = input("Enter candidate ID: ").strip()
        job_id = input("Enter job ID: ").strip()
        result = self.service.check_eligibility(candidate_id, job_id)
        self._print_eligibility(result)

    def apply_for_job(self):
        candidate_id = input("Enter candidate ID: ").strip()
        job_id = input("Enter job ID: ").strip()
        result = self.service.check_eligibility(candidate_id, job_id)
        self._print_eligibility(result)
        if not result["eligible"]:
            print("Application was not created.")
            return
        confirm = input("Submit this application? (y/n): ").strip().lower()
        if confirm == "y":
            application_id = self.service.apply_for_job(candidate_id, job_id)
            print(f"Application submitted successfully. Application ID: {application_id}")
        else:
            print("Application cancelled.")

    def view_all_applications(self):
        self._display_applications(self.service.get_all_applications())

    def view_candidate_applications(self):
        candidate_id = input("Enter candidate ID: ").strip()
        self._display_applications(
            self.service.get_applications_by_candidate(candidate_id)
        )

    def run(self):
        while True:
            print("\n====== ELIGIBILITY & APPLICATION MANAGEMENT ======")
            print("1. Check Candidate Eligibility")
            print("2. Apply for Job")
            print("3. View All Applications")
            print("4. View Applications by Candidate")
            print("0. Back to Main Menu")
            choice = input("Enter choice: ").strip()

            actions = {
                "1": self.check_eligibility,
                "2": self.apply_for_job,
                "3": self.view_all_applications,
                "4": self.view_candidate_applications,
            }
            if choice == "0":
                break
            action = actions.get(choice)
            if action is None:
                print("Invalid choice. Select 0-4.")
                continue
            try:
                action()
            except ValueError:
                print("Invalid numeric input. Check candidate/job ID.")
            except RPMSException as error:
                print(f"Operation failed: {error}")
            except Exception as error:
                print(f"Unexpected error: {error}")
