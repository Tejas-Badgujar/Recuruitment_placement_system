"""Business rules and validation for company operations."""
import re
from model.company import Company
from dao.company_dao import CompanyDAO
from exception.custom_exceptions import ValidationError, CompanyNotFoundError


class CompanyService:
    def __init__(self):
        self.dao = CompanyDAO()

    @staticmethod
    def _optional(data, key):
        value = data.get(key)
        return value.strip() if isinstance(value, str) and value.strip() else None

    def _build_company(self, data):
        name = data.get("company_name")
        if not name or not name.strip():
            raise ValidationError("Company name is required.")

        email = self._optional(data, "contact_email")
        if email and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise ValidationError("Enter a valid company contact email.")

        mobile = self._optional(data, "contact_mobile")
        if mobile and not re.fullmatch(r"[0-9+() -]{7,20}", mobile):
            raise ValidationError("Contact mobile must contain 7-20 valid phone characters.")

        website = self._optional(data, "website")
        if website and not re.match(r"^https?://", website, flags=re.IGNORECASE):
            raise ValidationError("Website must start with http:// or https://.")

        return Company(
            company_name=name.strip(),
            industry=self._optional(data, "industry"),
            website=website,
            contact_person=self._optional(data, "contact_person"),
            contact_email=email.lower() if email else None,
            contact_mobile=mobile,
            company_address=self._optional(data, "company_address"),
        )

    def add_company(self, data):
        return self.dao.add(self._build_company(data))

    def update_company(self, company_id, data):
        if not self.dao.get_by_id(company_id):
            raise CompanyNotFoundError("Company ID does not exist.")
        return self.dao.update(company_id, self._build_company(data))

    def get_company(self, company_id):
        company = self.dao.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundError("Company not found.")
        return company

    def get_all_companies(self):
        return self.dao.get_all()

    def search_companies(self, keyword):
        if not keyword or not keyword.strip():
            raise ValidationError("Enter a company ID, name, industry or contact email.")
        return self.dao.search(keyword.strip())

    def deactivate_company(self, company_id):
        return self.dao.deactivate(company_id)
