"""Data Access Object for company database operations."""
from mysql.connector import IntegrityError
from util.db_connection import get_connection
from exception.custom_exceptions import CompanyNotFoundError


class CompanyDAO:
    def add(self, company):
        sql = """
            INSERT INTO companies
            (company_name, industry, website, contact_person,
             contact_email, contact_mobile, company_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            company.company_name, company.industry, company.website,
            company.contact_person, company.contact_email,
            company.contact_mobile, company.company_address,
        )
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(sql, values)
            connection.commit()
            return cursor.lastrowid
        finally:
            if connection.is_connected():
                connection.close()

    def update(self, company_id, company):
        sql = """
            UPDATE companies
            SET company_name=%s, industry=%s, website=%s,
                contact_person=%s, contact_email=%s,
                contact_mobile=%s, company_address=%s
            WHERE company_id=%s AND company_status='ACTIVE'
        """
        values = (
            company.company_name, company.industry, company.website,
            company.contact_person, company.contact_email,
            company.contact_mobile, company.company_address, company_id,
        )
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(sql, values)
            if cursor.rowcount == 0:
                cursor.execute(
                    """SELECT company_id FROM companies
                       WHERE company_id=%s AND company_status='ACTIVE'""",
                    (company_id,),
                )
                if cursor.fetchone() is None:
                    connection.rollback()
                    raise CompanyNotFoundError(
                        "Company does not exist or is inactive."
                    )
            connection.commit()
            return True
        finally:
            if connection.is_connected():
                connection.close()

    def get_by_id(self, company_id):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM companies WHERE company_id=%s",
                (company_id,),
            )
            return cursor.fetchone()
        finally:
            if connection.is_connected():
                connection.close()

    def get_all(self):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM companies ORDER BY company_id DESC"
            )
            return cursor.fetchall()
        finally:
            if connection.is_connected():
                connection.close()

    def search(self, keyword):
        pattern = f"%{keyword}%"
        sql = """
            SELECT * FROM companies
            WHERE CAST(company_id AS CHAR) LIKE %s
               OR company_name LIKE %s
               OR industry LIKE %s
               OR contact_person LIKE %s
               OR contact_email LIKE %s
            ORDER BY company_id DESC
        """
        values = (pattern, pattern, pattern, pattern, pattern)
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql, values)
            return cursor.fetchall()
        finally:
            if connection.is_connected():
                connection.close()

    def deactivate(self, company_id):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """UPDATE companies SET company_status='INACTIVE'
                   WHERE company_id=%s AND company_status='ACTIVE'""",
                (company_id,),
            )
            if cursor.rowcount == 0:
                connection.rollback()
                raise CompanyNotFoundError(
                    "Active company not found with that ID."
                )
            connection.commit()
            return True
        finally:
            if connection.is_connected():
                connection.close()
