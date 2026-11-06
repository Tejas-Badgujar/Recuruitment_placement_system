-- Recruitment & Placement Management System
-- Optional sample data. Run after database.sql.
USE recruitment_placement_db;

INSERT INTO candidates
(first_name, last_name, email, mobile, qualification, branch, passing_year,
 percentage, active_backlogs, address)
VALUES
('Aarav', 'Patil', 'aarav.patil@example.com', '9000000001',
 'B.E.', 'Computer Engineering', 2026, 78.50, 0, 'Nashik'),
('Diya', 'Sharma', 'diya.sharma@example.com', '9000000002',
 'B.E.', 'Information Technology', 2026, 68.00, 1, 'Pune'),
('Rohan', 'Deshmukh', 'rohan.d@example.com', '9000000003',
 'Diploma', 'Computer Technology', 2026, 58.00, 2, 'Nashik');

INSERT INTO companies
(company_name, industry, website, contact_person, contact_email, company_status)
VALUES
('TechNova Solutions', 'Information Technology', 'https://example.com',
 'HR Manager', 'hr@technova.example', 'ACTIVE'),
('DataBridge Systems', 'Software Services', 'https://example.org',
 'Recruitment Team', 'careers@databridge.example', 'ACTIVE');

INSERT INTO candidate_skills (candidate_id, skill_name, proficiency)
VALUES
(1, 'Python', 'ADVANCED'),
(1, 'MySQL', 'INTERMEDIATE'),
(1, 'HTML', 'INTERMEDIATE'),
(2, 'Python', 'INTERMEDIATE'),
(2, 'Java', 'INTERMEDIATE'),
(3, 'HTML', 'BEGINNER');

INSERT INTO jobs
(company_id, job_title, qualification_required, branch_required, technology,
 openings, location, package_lpa, minimum_percentage, passing_year,
 maximum_backlogs, application_deadline, job_status)
VALUES
(1, 'Python Developer Trainee', 'B.E.', 'Computer Engineering',
 'Python', 5, 'Pune', 3.50, 60.00, 2026, 1, '2026-12-31', 'OPEN'),
(2, 'Software Engineer Trainee', 'B.E.', NULL,
 'Java', 3, 'Mumbai', 4.00, 65.00, 2026, 0, '2026-12-15', 'OPEN');

INSERT INTO job_required_skills (job_id, skill_name)
VALUES
(1, 'Python'),
(1, 'MySQL'),
(2, 'Java'),
(2, 'SQL');

-- Expected example: candidate 1 can satisfy the basic criteria for job 1.
-- Applications are intentionally not inserted here; the Python eligibility
-- service will validate eligibility before creating an application.
