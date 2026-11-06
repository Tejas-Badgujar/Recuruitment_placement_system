"""Console dashboard and report menu."""
from service.report_service import ReportService
from exception.custom_exceptions import RPMSException


class ReportMenu:
    def __init__(self):
        self.service = ReportService()
        self.last_report_name = None
        self.last_report_rows = None

    @staticmethod
    def _value(value):
        return "-" if value is None else str(value)

    def dashboard(self):
        data = self.service.get_dashboard()
        print("\n========== MANAGEMENT DASHBOARD ==========")
        groups = [
            ("CANDIDATES", [
                ("Total candidates", "total_candidates"),
                ("Active candidates", "active_candidates"),
            ]),
            ("COMPANIES & JOBS", [
                ("Active companies", "active_companies"),
                ("Total jobs", "total_jobs"),
                ("Open jobs", "open_jobs"),
            ]),
            ("APPLICATIONS", [
                ("Total applications", "total_applications"),
                ("Shortlisted", "shortlisted_applications"),
                ("In interview", "interview_applications"),
                ("Selected", "selected_applications"),
            ]),
            ("OFFERS & PLACEMENTS", [
                ("Total offers", "total_offers"),
                ("Accepted offers", "accepted_offers"),
                ("Candidates joined", "total_placements"),
                ("Pending joinings", "pending_joinings"),
                ("Not joined", "not_joined"),
            ]),
        ]
        for heading, fields in groups:
            print(f"\n{heading}")
            print("-" * 42)
            for label, key in fields:
                print(f"{label:<28}: {self._value(data.get(key))}")

    def _print_table(self, title, rows, columns):
        print(f"\n========== {title.upper()} ==========")
        if not rows:
            print("No records available.")
            self.last_report_name = title
            self.last_report_rows = []
            return
        widths = {
            key: min(max(len(label), *(len(self._value(row.get(key))) for row in rows)), 28)
            for key, label in columns
        }
        header = " | ".join(label[:widths[key]].ljust(widths[key])
                            for key, label in columns)
        print(header)
        print("-" * len(header))
        for row in rows:
            print(" | ".join(self._value(row.get(key))[:widths[key]].ljust(widths[key])
                              for key, _ in columns))
        self.last_report_name = title
        self.last_report_rows = rows

    def application_funnel(self):
        rows = self.service.get_application_funnel()
        self._print_table(
            "Application Funnel", rows,
            [("application_status", "STATUS"), ("total", "COUNT"),
             ("percentage", "PERCENT %")]
        )

    def company_report(self):
        rows = self.service.get_company_report()
        self._print_table(
            "Company Hiring Report", rows,
            [("company_id", "COMPANY ID"), ("company_name", "COMPANY"),
             ("jobs_posted", "JOBS"), ("applications_received", "APPLICATIONS"),
             ("selected_or_beyond", "SELECTED+"), ("candidates_joined", "JOINED")]
        )

    def job_report(self):
        rows = self.service.get_job_report()
        self._print_table(
            "Job Performance Report", rows,
            [("job_id", "JOB ID"), ("job_title", "JOB"),
             ("company_name", "COMPANY"), ("openings", "OPENINGS"),
             ("job_status", "STATUS"), ("applications_received", "APPLICATIONS"),
             ("shortlisted", "SHORTLISTED"), ("in_interview", "INTERVIEW"),
             ("selected_or_beyond", "SELECTED+"), ("joined", "JOINED")]
        )

    def package_report(self):
        data = self.service.get_package_report()
        print("\n========== PLACEMENT PACKAGE ANALYSIS ==========")
        labels = [
            ("Placement records", "placement_records"),
            ("Joined candidates", "joined_candidates"),
            ("Pending joinings", "pending_joinings"),
            ("Not joined", "not_joined_candidates"),
            ("Average joined package (LPA)", "average_package_lpa"),
            ("Minimum joined package (LPA)", "minimum_package_lpa"),
            ("Maximum joined package (LPA)", "maximum_package_lpa"),
        ]
        for label, key in labels:
            value = data.get(key)
            if key.endswith("_lpa") and value is not None:
                value = f"{float(value):.2f}"
            print(f"{label:<34}: {self._value(value)}")

    def company_placements(self):
        rows = self.service.get_company_placements()
        self._print_table(
            "Placements By Company", rows,
            [("company_name", "COMPANY"), ("placement_records", "RECORDS"),
             ("joined_candidates", "JOINED"), ("average_package_lpa", "AVG LPA")]
        )

    def year_report(self):
        rows = self.service.get_year_report()
        self._print_table(
            "Placement By Passing Year", rows,
            [("passing_year", "PASSING YEAR"), ("placement_records", "RECORDS"),
             ("joined_candidates", "JOINED"), ("average_package_lpa", "AVG LPA")]
        )

    def export_last_report(self):
        if self.last_report_rows is None:
            print("Run a tabular report first. Dashboard and package summary are not CSV-exported.")
            return
        try:
            path = self.service.export_csv(
                self.last_report_name, self.last_report_rows
            )
            print(f"CSV exported successfully: {path}")
        except ValueError as error:
            print(error)

    def run(self):
        actions = {
            "1": self.dashboard,
            "2": self.application_funnel,
            "3": self.company_report,
            "4": self.job_report,
            "5": self.package_report,
            "6": self.company_placements,
            "7": self.year_report,
            "8": self.export_last_report,
        }
        while True:
            print("\n========== REPORTS & DASHBOARD ==========")
            print("1. Dashboard Summary")
            print("2. Application Status Funnel")
            print("3. Company Hiring Report")
            print("4. Job Performance Report")
            print("5. Placement Package Analysis")
            print("6. Placements by Company")
            print("7. Placements by Candidate Passing Year")
            print("8. Export Last Tabular Report to CSV")
            print("0. Back to Main Menu")
            choice = input("Enter choice: ").strip()
            if choice == "0":
                break
            action = actions.get(choice)
            if action is None:
                print("Invalid choice. Select 0-8.")
                continue
            try:
                action()
            except RPMSException as error:
                print(f"Report failed: {error}")
            except Exception as error:
                print(f"Unexpected report error: {error}")
