"""Recruitment & Placement Management System entry point."""
from app.candidate_menu import CandidateMenu
from app.company_menu import CompanyMenu
from app.job_menu import JobMenu
from app.application_menu import ApplicationMenu
from app.interview_menu import InterviewMenu
from app.offer_menu import OfferMenu
from app.placement_menu import PlacementMenu
from app.report_menu import ReportMenu


def main():
    while True:
        print("\n" + "=" * 48)
        print("       RECRUITMENT & PLACEMENT SYSTEM")
        print("=" * 48)
        print("1. Candidates")
        print("2. Companies")
        print("3. Jobs")
        print("4. Eligibility & Applications")
        print("5. Interview Management")
        print("6. Offer Management")
        print("7. Placement Management")
        print("8. Reports & Dashboard")
        print("0. Exit")

        choice = input("Enter choice: ").strip()
        if choice == "1":
            CandidateMenu().run()
        elif choice == "2":
            CompanyMenu().run()
        elif choice == "3":
            JobMenu().run()
        elif choice == "4":
            ApplicationMenu().run()
        elif choice == "5":
            InterviewMenu().run()
        elif choice == "6":
            OfferMenu().run()
        elif choice == "7":
            PlacementMenu().run()
        elif choice == "0":
            print("Exiting Recruitment & Placement System.")
            break
        elif choice == "8":
            ReportMenu().run()
        else:
            print("Invalid choice. Select 0-8.")


if __name__ == "__main__":
    main()
