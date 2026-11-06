"""Console interface for Company Management."""
from service.company_service import CompanyService
from exception.custom_exceptions import RPMSException


class CompanyMenu:
    def __init__(self):
        self.service = CompanyService()

    @staticmethod
    def _read_company_data(existing=None):
        existing = existing or {}

        def ask(label, key, required=False):
            old = existing.get(key)
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
            "company_name": ask("Company name", "company_name", True),
            "industry": ask("Industry", "industry"),
            "website": ask("Website (include https://)", "website"),
            "contact_person": ask("Contact person", "contact_person"),
            "contact_email": ask("Contact email", "contact_email"),
            "contact_mobile": ask("Contact mobile", "contact_mobile"),
            "company_address": ask("Company address", "company_address"),
        }

    @staticmethod
    def _display(companies):
        if not companies:
            print("\nNo company records found.")
            return
        print("\n" + "-" * 115)
        print(f"{'ID':<5} {'COMPANY':<27} {'INDUSTRY':<22} "
              f"{'CONTACT PERSON':<20} {'EMAIL':<27} {'STATUS':<10}")
        print("-" * 115)
        for c in companies:
            print(f"{c['company_id']:<5} {c['company_name'][:26]:<27} "
                  f"{(c['industry'] or '-')[:21]:<22} "
                  f"{(c['contact_person'] or '-')[:19]:<20} "
                  f"{(c['contact_email'] or '-')[:26]:<27} "
                  f"{c['company_status']:<10}")
        print("-" * 115)

    def add_company(self):
        company_id = self.service.add_company(self._read_company_data())
        print(f"Company created successfully. Company ID: {company_id}")

    def update_company(self):
        company_id = int(input("Enter company ID to update: "))
        existing = self.service.get_company(company_id)
        if existing["company_status"] == "INACTIVE":
            print("Inactive companies cannot be updated.")
            return
        self.service.update_company(
            company_id, self._read_company_data(existing)
        )
        print("Company updated successfully.")

    def search_company(self):
        keyword = input("Enter company ID, name, industry or contact email: ")
        self._display(self.service.search_companies(keyword))

    def view_all_companies(self):
        self._display(self.service.get_all_companies())

    def deactivate_company(self):
        company_id = int(input("Enter company ID to deactivate: "))
        confirm = input("Deactivate this company? (y/n): ").strip().lower()
        if confirm == "y":
            self.service.deactivate_company(company_id)
            print("Company deactivated. Existing job/application history is retained.")
        else:
            print("Operation cancelled.")

    def run(self):
        while True:
            print("\n========== COMPANY MANAGEMENT ==========")
            print("1. Add Company")
            print("2. Update Company")
            print("3. Search Company")
            print("4. View All Companies")
            print("5. Deactivate Company")
            print("0. Back to Main Menu")
            choice = input("Enter choice: ").strip()

            actions = {
                "1": self.add_company,
                "2": self.update_company,
                "3": self.search_company,
                "4": self.view_all_companies,
                "5": self.deactivate_company,
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
                print("Invalid numeric input. Please enter a valid ID.")
            except RPMSException as error:
                print(f"Operation failed: {error}")
            except Exception as error:
                print(f"Unexpected error: {error}")
