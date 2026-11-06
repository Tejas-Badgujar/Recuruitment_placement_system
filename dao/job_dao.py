"""Data Access Object for job operations."""
from mysql.connector import IntegrityError
from util.db_connection import get_connection
from exception.custom_exceptions import JobNotFoundError, CompanyNotFoundError


class JobDAO:
    def _check_active_company(self, cursor, company_id):
        cursor.execute(
            "SELECT company_status FROM companies WHERE company_id=%s",
            (company_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise CompanyNotFoundError("Company ID does not exist.")
        if row[0] != "ACTIVE":
            raise CompanyNotFoundError(
                "Inactive companies cannot create or update job postings."
            )

    def add(self, job):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            self._check_active_company(cursor, job.company_id)

            cursor.execute(
                """INSERT INTO jobs
                   (company_id, job_title, job_description,
                    qualification_required, branch_required, technology,
                    openings, location, package_lpa, minimum_percentage,
                    passing_year, maximum_backlogs, application_deadline,
                    job_status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'OPEN')""",
                (
                    job.company_id, job.job_title, job.job_description,
                    job.qualification_required, job.branch_required,
                    job.technology, job.openings, job.location,
                    job.package_lpa, job.minimum_percentage,
                    job.passing_year, job.maximum_backlogs,
                    job.application_deadline,
                ),
            )
            job_id = cursor.lastrowid
            self._replace_skills(cursor, job_id, job.required_skills or [])
            connection.commit()
            return job_id
        except Exception:
            connection.rollback()
            raise
        finally:
            if connection.is_connected():
                connection.close()

    @staticmethod
    def _replace_skills(cursor, job_id, skills):
        cursor.execute("DELETE FROM job_required_skills WHERE job_id=%s", (job_id,))
        if skills:
            cursor.executemany(
                "INSERT INTO job_required_skills (job_id, skill_name) VALUES (%s, %s)",
                [(job_id, skill) for skill in skills],
            )

    def update(self, job_id, job):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT job_status FROM jobs WHERE job_id=%s",
                (job_id,),
            )
            current = cursor.fetchone()
            if current is None:
                raise JobNotFoundError("Job ID does not exist.")
            if current[0] == "CLOSED":
                raise JobNotFoundError("Closed jobs cannot be updated.")

            self._check_active_company(cursor, job.company_id)
            cursor.execute(
                """UPDATE jobs
                   SET company_id=%s, job_title=%s, job_description=%s,
                       qualification_required=%s, branch_required=%s,
                       technology=%s, openings=%s, location=%s,
                       package_lpa=%s, minimum_percentage=%s,
                       passing_year=%s, maximum_backlogs=%s,
                       application_deadline=%s
                   WHERE job_id=%s""",
                (
                    job.company_id, job.job_title, job.job_description,
                    job.qualification_required, job.branch_required,
                    job.technology, job.openings, job.location,
                    job.package_lpa, job.minimum_percentage,
                    job.passing_year, job.maximum_backlogs,
                    job.application_deadline, job_id,
                ),
            )
            self._replace_skills(cursor, job_id, job.required_skills or [])
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            if connection.is_connected():
                connection.close()

    def get_by_id(self, job_id):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT j.*, c.company_name
                   FROM jobs j
                   JOIN companies c ON c.company_id=j.company_id
                   WHERE j.job_id=%s""",
                (job_id,),
            )
            job = cursor.fetchone()
            if job:
                cursor.execute(
                    """SELECT skill_name FROM job_required_skills
                       WHERE job_id=%s ORDER BY skill_name""",
                    (job_id,),
                )
                job["required_skills"] = [row["skill_name"] for row in cursor.fetchall()]
            return job
        finally:
            if connection.is_connected():
                connection.close()

    def get_open_jobs(self):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT j.*, c.company_name
                   FROM jobs j
                   JOIN companies c ON c.company_id=j.company_id
                   WHERE j.job_status='OPEN'
                     AND j.application_deadline >= CURDATE()
                     AND c.company_status='ACTIVE'
                   ORDER BY j.created_at DESC"""
            )
            jobs = cursor.fetchall()
            for job in jobs:
                cursor.execute(
                    """SELECT skill_name FROM job_required_skills
                       WHERE job_id=%s ORDER BY skill_name""",
                    (job["job_id"],),
                )
                job["required_skills"] = [
                    row["skill_name"] for row in cursor.fetchall()
                ]
            return jobs
        finally:
            if connection.is_connected():
                connection.close()

    def search(self, keyword):
        pattern = f"%{keyword}%"
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT DISTINCT j.*, c.company_name
                   FROM jobs j
                   JOIN companies c ON c.company_id=j.company_id
                   LEFT JOIN job_required_skills s ON s.job_id=j.job_id
                   WHERE j.job_title LIKE %s
                      OR j.technology LIKE %s
                      OR j.location LIKE %s
                      OR c.company_name LIKE %s
                      OR s.skill_name LIKE %s
                   ORDER BY j.created_at DESC""",
                (pattern, pattern, pattern, pattern, pattern),
            )
            return cursor.fetchall()
        finally:
            if connection.is_connected():
                connection.close()

    def close(self, job_id):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """UPDATE jobs SET job_status='CLOSED'
                   WHERE job_id=%s AND job_status <> 'CLOSED'""",
                (job_id,),
            )
            if cursor.rowcount == 0:
                cursor.execute(
                    "SELECT job_id FROM jobs WHERE job_id=%s",
                    (job_id,),
                )
                if cursor.fetchone() is None:
                    raise JobNotFoundError("Job ID does not exist.")
                raise JobNotFoundError("Job is already closed.")
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            if connection.is_connected():
                connection.close()
