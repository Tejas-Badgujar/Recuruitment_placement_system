"""Console interface for Job Management."""
from service.job_service import JobService
from exception.custom_exceptions import RPMSException


class JobMenu:
    def __init__(self):
        self.service = JobService()

    @staticmethod
    def _read_job_data(existing=None):
        existing = existing or {}

        def ask(label, key, required=False, default=None):
            old = existing.get(key, default)
            if key == "required_skills" and isinstance(old, list):
                old = ", ".join(old)
            prompt = label
            if old not in (None, ""):
                prompt += f" [{old}]"
            value = input(prompt + ": ").strip()
            if value:
                return value
            if old not in (None, ""):
                return str(old)
            if required:
                return input(f"{label} (required): ").strip()
            return ""

        return {
            "company_id": ask("Company ID", "company_id", True),
            "job_title": ask("Job title", "job_title", True),
            "job_description": ask("Job description", "job_description"),
            "qualification_required": ask("Required qualification", "qualification_required", True),
            "branch_required": ask("Required branch (blank = any)", "branch_required"),
            "technology": ask("Primary technology", "technology"),
            "required_skills": ask("Required skills (comma separated)", "required_skills"),
            "openings": ask("Number of openings", "openings", default=1),
            "location": ask("Location", "location"),
            "package_lpa": ask("Package in LPA (optional)", "package_lpa"),
            "minimum_percentage": ask("Minimum percentage", "minimum_percentage", default=0),
            "passing_year": ask("Eligible passing year", "passing_year", True),
            "maximum_backlogs": ask("Maximum backlogs", "maximum_backlogs", default=0),
            "application_deadline": ask("Application deadline YYYY-MM-DD", "application_deadline", True),
        }

    @staticmethod
    def _display(jobs):
        if not jobs:
            print("\nNo jobs found.")
            return
        print("\n" + "-" * 135)
        print(f"{'ID':<5} {'JOB TITLE':<27} {'COMPANY':<24} {'TECHNOLOGY':<17} "
              f"{'YEAR':<7} {'MIN %':<8} {'OPENINGS':<9} {'DEADLINE':<12} {'STATUS':<9}")
        print("-" * 135)
        for job in jobs:
            print(f"{job['job_id']:<5} {job['job_title'][:26]:<27} "
                  f"{job['company_name'][:23]:<24} {(job['technology'] or '-')[:16]:<17} "
                  f"{str(job['passing_year']):<7} {str(job['minimum_percentage']):<8} "
                  f"{job['openings']:<9} {str(job['application_deadline']):<12} "
                  f"{job['job_status']:<9}")
            skills = job.get("required_skills")
            if skills:
                print("      Required skills: " + ", ".join(skills))
        print("-" * 135)

    def create_job(self):
        job_id = self.service.create_job(self._read_job_data())
        print(f"Job created successfully. Job ID: {job_id}")

    def update_job(self):
        job_id = int(input("Enter job ID to update: "))
        existing = self.service.get_job(job_id)
        if existing["job_status"] == "CLOSED":
            print("Closed jobs cannot be updated.")
            return
        self.service.update_job(job_id, self._read_job_data(existing))
        print("Job updated successfully.")

    def view_open_jobs(self):
        self._display(self.service.get_open_jobs())

    def search_jobs(self):
        keyword = input("Search by title, company, technology, skill or location: ")
        self._display(self.service.search_jobs(keyword))

    def close_job(self):
        job_id = int(input("Enter job ID to close: "))
        confirm = input("Close this job? (y/n): ").strip().lower()
        if confirm == "y":
            self.service.close_job(job_id)
            print("Job closed. Existing application records are retained.")
        else:
            print("Operation cancelled.")

    def run(self):
        while True:
            print("\n========== JOB MANAGEMENT ==========")
            print("1. Create Job")
            print("2. Update Job")
            print("3. View Open Jobs")
            print("4. Search Jobs")
            print("5. Close Job")
            print("0. Back to Main Menu")
            choice = input("Enter choice: ").strip()
            actions = {
                "1": self.create_job,
                "2": self.update_job,
                "3": self.view_open_jobs,
                "4": self.search_jobs,
                "5": self.close_job,
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
                print("Invalid numeric input. Check the ID or numeric fields.")
            except RPMSException as error:
                print(f"Operation failed: {error}")
            except Exception as error:
                print(f"Unexpected error: {error}")
