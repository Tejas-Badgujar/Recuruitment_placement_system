"""Console menu for interview scheduling and feedback."""
from service.interview_service import InterviewService
from exception.custom_exceptions import RPMSException


class InterviewMenu:
    def __init__(self):
        self.service = InterviewService()

    @staticmethod
    def _show_interviews(rows):
        if not rows:
            print("\nNo interviews found.")
            return
        print("\n" + "-" * 132)
        print(f"{'ID':<6} {'APP':<6} {'ROUND':<7} {'CANDIDATE':<22} "
              f"{'JOB':<22} {'DATE':<19} {'MODE':<9} {'STATUS':<13}")
        print("-" * 132)
        for row in rows:
            print(f"{row['interview_id']:<6} {row['application_id']:<6} "
                  f"{row['round_number']:<7} {row['candidate_name'][:21]:<22} "
                  f"{row['job_title'][:21]:<22} "
                  f"{str(row['interview_date'])[:16]:<19} "
                  f"{row['interview_mode']:<9} {row['interview_status']:<13}")
        print("-" * 132)

    def schedule(self):
        app_id = input("Application ID: ").strip()
        round_no = input("Round number (1, 2, 3...): ").strip()
        date_time = input("Interview date/time (YYYY-MM-DD HH:MM): ").strip()
        mode = input("Mode (ONLINE/OFFLINE): ").strip()
        interviewer = input("Interviewer name (optional): ").strip()
        venue = input("Meeting link / venue: ").strip()
        interview_id = self.service.schedule_interview(
            app_id, round_no, date_time, mode, interviewer, venue
        )
        print(f"Interview scheduled. Interview ID: {interview_id}")

    def view_all(self):
        self._show_interviews(self.service.get_all_interviews())

    def view_by_application(self):
        app_id = input("Application ID: ").strip()
        rows = self.service.get_interviews_by_application(app_id)
        self._show_interviews(rows)
        for row in rows:
            if row.get("result"):
                print(f"Interview {row['interview_id']} feedback: "
                      f"{row['result']} | Technical: {row['technical_rating']} | "
                      f"Communication: {row['communication_rating']}")

    def reschedule(self):
        interview_id = input("Interview ID: ").strip()
        date_time = input("New date/time (YYYY-MM-DD HH:MM): ").strip()
        mode = input("Mode (ONLINE/OFFLINE): ").strip()
        interviewer = input("Interviewer name (optional): ").strip()
        venue = input("Meeting link / venue: ").strip()
        self.service.reschedule_interview(
            interview_id, date_time, mode, interviewer, venue
        )
        print("Interview rescheduled successfully.")

    def finalise_interview(self):
        interview_id = input("Interview ID: ").strip()
        status = input("Enter COMPLETED or CANCELLED: ").strip()
        self.service.update_interview_status(interview_id, status)
        print(f"Interview marked as {status.upper()}.")

    def feedback(self):
        interview_id = input("Interview ID: ").strip()
        technical = input("Technical rating (0-10, blank if not rated): ").strip()
        communication = input(
            "Communication rating (0-10, blank if not rated): "
        ).strip()
        remarks = input("Remarks: ").strip()
        result = input("Result (PASS/FAIL/ON_HOLD): ").strip()
        feedback_id = self.service.submit_feedback(
            interview_id, technical, communication, remarks, result
        )
        print(f"Feedback submitted. Feedback ID: {feedback_id}")

    def change_application_status(self):
        app_id = input("Application ID: ").strip()
        status = input(
            "New status (SHORTLISTED/INTERVIEW/SELECTED/REJECTED/OFFERED/JOINED): "
        ).strip()
        self.service.update_application_status(app_id, status)
        print("Application status updated successfully.")

    def run(self):
        actions = {
            "1": self.schedule,
            "2": self.view_all,
            "3": self.view_by_application,
            "4": self.reschedule,
            "5": self.finalise_interview,
            "6": self.feedback,
            "7": self.change_application_status,
        }
        while True:
            print("\n========== INTERVIEW MANAGEMENT ==========")
            print("1. Schedule Interview")
            print("2. View All Interviews")
            print("3. View Interviews by Application")
            print("4. Reschedule Interview")
            print("5. Mark Interview Completed / Cancelled")
            print("6. Submit Interview Feedback")
            print("7. Update Application Workflow Status")
            print("0. Back to Main Menu")
            choice = input("Enter choice: ").strip()
            if choice == "0":
                break
            action = actions.get(choice)
            if action is None:
                print("Invalid choice. Select 0-7.")
                continue
            try:
                action()
            except ValueError:
                print("Invalid input. Check the ID, date and numeric values.")
            except RPMSException as error:
                print(f"Operation failed: {error}")
            except Exception as error:
                print(f"Unexpected error: {error}")
