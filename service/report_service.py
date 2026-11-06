"""Reporting service: aggregate reports and CSV export."""
import csv
from pathlib import Path
from dao.report_dao import ReportDAO


class ReportService:
    def __init__(self):
        self.dao = ReportDAO()

    def get_dashboard(self):
        return self.dao.get_dashboard_summary()

    def get_application_funnel(self):
        rows = self.dao.get_application_funnel()
        total = sum(int(row["total"]) for row in rows)
        for row in rows:
            row["percentage"] = (
                round((int(row["total"]) / total) * 100, 2) if total else 0.0
            )
        return rows

    def get_company_report(self):
        return self.dao.get_company_hiring_report()

    def get_job_report(self):
        return self.dao.get_job_performance_report()

    def get_package_report(self):
        return self.dao.get_placement_package_report()

    def get_company_placements(self):
        return self.dao.get_placements_by_company()

    def get_year_report(self):
        return self.dao.get_placements_by_passing_year()

    @staticmethod
    def export_csv(report_name, rows):
        """Export a report result to a CSV file in the project reports folder."""
        if not rows:
            raise ValueError("There is no data to export for this report.")
        safe_name = "".join(
            char.lower() if char.isalnum() else "_" for char in report_name
        ).strip("_")
        reports_dir = Path(__file__).resolve().parents[1] / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        output = reports_dir / f"{safe_name}.csv"
        columns = list(rows[0].keys())
        with output.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
        return output
