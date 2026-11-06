"""Read-only SQL queries for dashboard and management reports."""
from util.db_connection import get_connection


class ReportDAO:
    def get_dashboard_summary(self):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT
                    (SELECT COUNT(*) FROM candidates) AS total_candidates,
                    (SELECT COUNT(*) FROM candidates
                     WHERE candidate_status='ACTIVE') AS active_candidates,
                    (SELECT COUNT(*) FROM companies
                     WHERE company_status='ACTIVE') AS active_companies,
                    (SELECT COUNT(*) FROM jobs) AS total_jobs,
                    (SELECT COUNT(*) FROM jobs
                     WHERE job_status='OPEN') AS open_jobs,
                    (SELECT COUNT(*) FROM applications) AS total_applications,
                    (SELECT COUNT(*) FROM applications
                     WHERE application_status='SHORTLISTED') AS shortlisted_applications,
                    (SELECT COUNT(*) FROM applications
                     WHERE application_status='INTERVIEW') AS interview_applications,
                    (SELECT COUNT(*) FROM applications
                     WHERE application_status='SELECTED') AS selected_applications,
                    (SELECT COUNT(*) FROM offers) AS total_offers,
                    (SELECT COUNT(*) FROM offers
                     WHERE offer_status='ACCEPTED') AS accepted_offers,
                    (SELECT COUNT(*) FROM placements
                     WHERE placement_status='JOINED') AS total_placements,
                    (SELECT COUNT(*) FROM placements
                     WHERE placement_status='JOINING_PENDING') AS pending_joinings,
                    (SELECT COUNT(*) FROM placements
                     WHERE placement_status='NOT_JOINED') AS not_joined"""
            )
            return cursor.fetchone()
        finally:
            if connection.is_connected():
                connection.close()

    def get_application_funnel(self):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT application_status, COUNT(*) AS total
                   FROM applications
                   GROUP BY application_status
                   ORDER BY FIELD(application_status, 'APPLIED', 'SHORTLISTED',
                       'INTERVIEW', 'SELECTED', 'OFFERED', 'JOINED', 'REJECTED')"""
            )
            return cursor.fetchall()
        finally:
            if connection.is_connected():
                connection.close()

    def get_company_hiring_report(self):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT co.company_id, co.company_name,
                          COUNT(DISTINCT j.job_id) AS jobs_posted,
                          COUNT(DISTINCT a.application_id) AS applications_received,
                          COUNT(DISTINCT CASE
                              WHEN a.application_status IN ('SELECTED','OFFERED','JOINED')
                              THEN a.application_id END) AS selected_or_beyond,
                          COUNT(DISTINCT CASE
                              WHEN a.application_status='JOINED'
                              THEN a.application_id END) AS candidates_joined
                   FROM companies co
                   LEFT JOIN jobs j ON j.company_id=co.company_id
                   LEFT JOIN applications a ON a.job_id=j.job_id
                   GROUP BY co.company_id, co.company_name
                   ORDER BY candidates_joined DESC, applications_received DESC,
                            co.company_name"""
            )
            return cursor.fetchall()
        finally:
            if connection.is_connected():
                connection.close()

    def get_job_performance_report(self):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT j.job_id, j.job_title, co.company_name,
                          j.openings, j.job_status, j.package_lpa,
                          COUNT(a.application_id) AS applications_received,
                          SUM(CASE WHEN a.application_status='SHORTLISTED'
                              THEN 1 ELSE 0 END) AS shortlisted,
                          SUM(CASE WHEN a.application_status='INTERVIEW'
                              THEN 1 ELSE 0 END) AS in_interview,
                          SUM(CASE WHEN a.application_status IN ('SELECTED','OFFERED','JOINED')
                              THEN 1 ELSE 0 END) AS selected_or_beyond,
                          SUM(CASE WHEN a.application_status='JOINED'
                              THEN 1 ELSE 0 END) AS joined
                   FROM jobs j
                   JOIN companies co ON co.company_id=j.company_id
                   LEFT JOIN applications a ON a.job_id=j.job_id
                   GROUP BY j.job_id, j.job_title, co.company_name,
                            j.openings, j.job_status, j.package_lpa
                   ORDER BY applications_received DESC, j.job_id DESC"""
            )
            return cursor.fetchall()
        finally:
            if connection.is_connected():
                connection.close()

    def get_placement_package_report(self):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT COUNT(*) AS placement_records,
                          SUM(CASE WHEN placement_status='JOINED' THEN 1 ELSE 0 END)
                              AS joined_candidates,
                          SUM(CASE WHEN placement_status='JOINING_PENDING' THEN 1 ELSE 0 END)
                              AS pending_joinings,
                          SUM(CASE WHEN placement_status='NOT_JOINED' THEN 1 ELSE 0 END)
                              AS not_joined_candidates,
                          AVG(CASE WHEN placement_status='JOINED'
                              THEN final_package_lpa END) AS average_package_lpa,
                          MIN(CASE WHEN placement_status='JOINED'
                              THEN final_package_lpa END) AS minimum_package_lpa,
                          MAX(CASE WHEN placement_status='JOINED'
                              THEN final_package_lpa END) AS maximum_package_lpa
                   FROM placements"""
            )
            return cursor.fetchone()
        finally:
            if connection.is_connected():
                connection.close()

    def get_placements_by_company(self):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT co.company_name,
                          COUNT(p.placement_id) AS placement_records,
                          SUM(CASE WHEN p.placement_status='JOINED' THEN 1 ELSE 0 END)
                              AS joined_candidates,
                          AVG(CASE WHEN p.placement_status='JOINED'
                              THEN p.final_package_lpa END) AS average_package_lpa
                   FROM companies co
                   JOIN jobs j ON j.company_id=co.company_id
                   JOIN applications a ON a.job_id=j.job_id
                   JOIN offers o ON o.application_id=a.application_id
                   JOIN placements p ON p.offer_id=o.offer_id
                   GROUP BY co.company_id, co.company_name
                   ORDER BY joined_candidates DESC, co.company_name"""
            )
            return cursor.fetchall()
        finally:
            if connection.is_connected():
                connection.close()

    def get_placements_by_passing_year(self):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT c.passing_year,
                          COUNT(p.placement_id) AS placement_records,
                          SUM(CASE WHEN p.placement_status='JOINED' THEN 1 ELSE 0 END)
                              AS joined_candidates,
                          AVG(CASE WHEN p.placement_status='JOINED'
                              THEN p.final_package_lpa END) AS average_package_lpa
                   FROM candidates c
                   JOIN applications a ON a.candidate_id=c.candidate_id
                   JOIN offers o ON o.application_id=a.application_id
                   JOIN placements p ON p.offer_id=o.offer_id
                   GROUP BY c.passing_year
                   ORDER BY c.passing_year DESC"""
            )
            return cursor.fetchall()
        finally:
            if connection.is_connected():
                connection.close()
