"""RPMS integration preflight: dependencies, project files and MySQL schema."""
import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED_TABLES = {
    "candidates", "companies", "candidate_skills", "jobs",
    "job_required_skills", "applications", "interviews",
    "interview_feedback", "offers", "placements",
}
REQUIRED_FILES = [
    "main.py",
    "model/candidate.py", "model/company.py", "model/job.py",
    "model/application.py", "model/interview.py", "model/offer.py",
    "model/placement.py",
    "dao/candidate_dao.py", "dao/company_dao.py", "dao/job_dao.py",
    "dao/application_dao.py", "dao/interview_dao.py", "dao/offer_dao.py",
    "dao/placement_dao.py", "dao/report_dao.py",
    "service/candidate_service.py", "service/company_service.py",
    "service/job_service.py", "service/eligibility_service.py",
    "service/application_service.py", "service/interview_service.py",
    "service/offer_service.py", "service/placement_service.py",
    "service/report_service.py",
    "app/candidate_menu.py", "app/company_menu.py", "app/job_menu.py",
    "app/application_menu.py", "app/interview_menu.py", "app/offer_menu.py",
    "app/placement_menu.py", "app/report_menu.py",
    "sql/database.sql", "sql/sample_data.sql",
]
IMPORTS = [
    "app.candidate_menu", "app.company_menu", "app.job_menu",
    "app.application_menu", "app.interview_menu", "app.offer_menu",
    "app.placement_menu", "app.report_menu",
    "dao.candidate_dao", "dao.company_dao", "dao.job_dao",
    "dao.application_dao", "dao.interview_dao", "dao.offer_dao",
    "dao.placement_dao", "dao.report_dao",
    "service.candidate_service", "service.company_service",
    "service.job_service", "service.eligibility_service",
    "service.application_service", "service.interview_service",
    "service.offer_service", "service.placement_service",
    "service.report_service",
]


def result(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" +
          (f" — {detail}" if detail else ""))
    return ok


def main():
    print("=" * 66)
    print("RECRUITMENT & PLACEMENT SYSTEM - INTEGRATION PREFLIGHT")
    print("=" * 66)
    checks = []

    checks.append(result("Python version", sys.version_info >= (3, 9),
                         sys.version.split()[0] + " (requires 3.9+)"))

    missing_files = [item for item in REQUIRED_FILES if not (ROOT / item).is_file()]
    checks.append(result("Project files", not missing_files,
                         "All required files found" if not missing_files
                         else "Missing: " + ", ".join(missing_files)))

    missing_packages = [
        package for package in ("mysql", "dotenv")
        if importlib.util.find_spec(package) is None
    ]
    checks.append(result("Python dependencies", not missing_packages,
                         "mysql-connector-python and python-dotenv available"
                         if not missing_packages
                         else "Missing: " + ", ".join(missing_packages)
                         + " — run: python -m pip install -r requirements.txt"))

    env_file = ROOT / ".env"
    checks.append(result(".env configuration file", env_file.is_file(),
                         "Found (credentials are not displayed)"
                         if env_file.is_file()
                         else "Not found — copy .env.example to .env and configure it"))

    if missing_packages:
        print("\nDatabase and import checks skipped because dependencies are missing.")
        print(f"\nRESULT: {sum(checks)}/{len(checks)} preflight checks passed.")
        return 1

    # Imports are checked only after the external dependencies exist.
    import importlib
    import_errors = []
    for module in IMPORTS:
        try:
            importlib.import_module(module)
        except Exception as error:
            import_errors.append(f"{module}: {error}")
    checks.append(result("Application module imports", not import_errors,
                         f"{len(IMPORTS)} modules imported"
                         if not import_errors else "; ".join(import_errors)))

    try:
        from dotenv import load_dotenv
        import mysql.connector

        load_dotenv(ROOT / ".env")
        database_name = os.getenv("DB_NAME", "recruitment_placement_db")
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=database_name,
            connection_timeout=5,
        )
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE(), VERSION()")
            db_name, version = cursor.fetchone()
            cursor.execute("SHOW TABLES")
            existing_tables = {row[0] for row in cursor.fetchall()}
            missing_tables = sorted(REQUIRED_TABLES - existing_tables)
            checks.append(result("MySQL connection", True,
                                 f"Connected to {db_name}; server {version}"))
            checks.append(result("Required database tables", not missing_tables,
                                 "All 10 tables found" if not missing_tables
                                 else "Missing: " + ", ".join(missing_tables)))
        finally:
            connection.close()
    except Exception as error:
        checks.append(result("MySQL connection / schema", False, str(error)))

    print("\n" + "=" * 66)
    passed = sum(checks)
    print(f"RESULT: {passed}/{len(checks)} checks passed.")
    if passed == len(checks):
        print("Preflight passed. Proceed with the end-to-end test plan.")
        return 0
    print("Fix every FAIL before treating the project as integration-tested.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
