-- Recruitment & Placement Management System
-- Step 1: Database schema
-- Target: MySQL 8.0+ / compatible MariaDB
-- Run this file in MySQL Workbench or phpMyAdmin.

CREATE DATABASE IF NOT EXISTS recruitment_placement_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE recruitment_placement_db;

-- 1. Candidates
CREATE TABLE IF NOT EXISTS candidates (
    candidate_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(60) NOT NULL,
    last_name VARCHAR(60) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    mobile VARCHAR(20) NOT NULL UNIQUE,
    gender ENUM('MALE', 'FEMALE', 'OTHER', 'NOT_SPECIFIED') DEFAULT 'NOT_SPECIFIED',
    date_of_birth DATE NULL,
    qualification VARCHAR(100) NOT NULL,
    branch VARCHAR(100) NULL,
    passing_year YEAR NOT NULL,
    percentage DECIMAL(5,2) NOT NULL,
    active_backlogs INT NOT NULL DEFAULT 0,
    address VARCHAR(255) NULL,
    resume_path VARCHAR(255) NULL,
    candidate_status ENUM('ACTIVE', 'INACTIVE', 'PLACED') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_candidate_percentage CHECK (percentage BETWEEN 0 AND 100),
    CONSTRAINT chk_candidate_backlogs CHECK (active_backlogs >= 0),
    INDEX idx_candidate_name (last_name, first_name),
    INDEX idx_candidate_passing_year (passing_year),
    INDEX idx_candidate_status (candidate_status)
) ENGINE=InnoDB;

-- 2. Companies
CREATE TABLE IF NOT EXISTS companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    industry VARCHAR(100) NULL,
    website VARCHAR(255) NULL,
    contact_person VARCHAR(120) NULL,
    contact_email VARCHAR(150) NULL,
    contact_mobile VARCHAR(20) NULL,
    company_address VARCHAR(255) NULL,
    company_status ENUM('ACTIVE', 'INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_company_name (company_name),
    INDEX idx_company_status (company_status)
) ENGINE=InnoDB;

-- 3. Candidate skills
CREATE TABLE IF NOT EXISTS candidate_skills (
    candidate_skill_id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    proficiency ENUM('BEGINNER', 'INTERMEDIATE', 'ADVANCED') DEFAULT 'BEGINNER',
    CONSTRAINT fk_candidate_skills_candidate
        FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_candidate_skill UNIQUE (candidate_id, skill_name),
    INDEX idx_candidate_skill_name (skill_name)
) ENGINE=InnoDB;

-- 4. Jobs
CREATE TABLE IF NOT EXISTS jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    job_title VARCHAR(150) NOT NULL,
    job_description TEXT NULL,
    qualification_required VARCHAR(100) NOT NULL,
    branch_required VARCHAR(100) NULL,
    technology VARCHAR(150) NULL,
    openings INT NOT NULL DEFAULT 1,
    location VARCHAR(150) NULL,
    package_lpa DECIMAL(8,2) NULL,
    minimum_percentage DECIMAL(5,2) NOT NULL DEFAULT 0,
    passing_year YEAR NOT NULL,
    maximum_backlogs INT NOT NULL DEFAULT 0,
    application_deadline DATE NOT NULL,
    job_status ENUM('OPEN', 'CLOSED', 'ON_HOLD') NOT NULL DEFAULT 'OPEN',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_jobs_company
        FOREIGN KEY (company_id) REFERENCES companies(company_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_job_openings CHECK (openings > 0),
    CONSTRAINT chk_job_percentage CHECK (minimum_percentage BETWEEN 0 AND 100),
    CONSTRAINT chk_job_backlogs CHECK (maximum_backlogs >= 0),
    CONSTRAINT chk_job_package CHECK (package_lpa IS NULL OR package_lpa >= 0),
    INDEX idx_jobs_company (company_id),
    INDEX idx_jobs_status_deadline (job_status, application_deadline),
    INDEX idx_jobs_passing_year (passing_year)
) ENGINE=InnoDB;

-- 5. Skills required for each job
CREATE TABLE IF NOT EXISTS job_required_skills (
    job_skill_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    CONSTRAINT fk_job_skills_job
        FOREIGN KEY (job_id) REFERENCES jobs(job_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_job_required_skill UNIQUE (job_id, skill_name),
    INDEX idx_job_skill_name (skill_name)
) ENGINE=InnoDB;

-- 6. Applications
CREATE TABLE IF NOT EXISTS applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    job_id INT NOT NULL,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    application_status ENUM(
        'APPLIED', 'SHORTLISTED', 'INTERVIEW',
        'SELECTED', 'OFFERED', 'JOINED', 'REJECTED'
    ) NOT NULL DEFAULT 'APPLIED',
    eligibility_checked BOOLEAN NOT NULL DEFAULT TRUE,
    eligibility_remarks VARCHAR(500) NULL,
    status_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_applications_candidate
        FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_applications_job
        FOREIGN KEY (job_id) REFERENCES jobs(job_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uq_candidate_job_application UNIQUE (candidate_id, job_id),
    INDEX idx_application_status (application_status),
    INDEX idx_application_job (job_id),
    INDEX idx_application_candidate (candidate_id)
) ENGINE=InnoDB;

-- 7. Interviews: one application can have multiple interview rounds
CREATE TABLE IF NOT EXISTS interviews (
    interview_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    round_number INT NOT NULL,
    interview_date DATETIME NOT NULL,
    interview_mode ENUM('ONLINE', 'OFFLINE') NOT NULL,
    interviewer_name VARCHAR(120) NULL,
    meeting_or_venue VARCHAR(255) NULL,
    interview_status ENUM('SCHEDULED', 'COMPLETED', 'CANCELLED', 'RESCHEDULED')
        NOT NULL DEFAULT 'SCHEDULED',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_interviews_application
        FOREIGN KEY (application_id) REFERENCES applications(application_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_application_round UNIQUE (application_id, round_number),
    CONSTRAINT chk_interview_round CHECK (round_number > 0),
    INDEX idx_interview_date (interview_date),
    INDEX idx_interview_status (interview_status)
) ENGINE=InnoDB;

-- 8. Interview feedback: one feedback record per interview
CREATE TABLE IF NOT EXISTS interview_feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL UNIQUE,
    technical_rating DECIMAL(3,1) NULL,
    communication_rating DECIMAL(3,1) NULL,
    remarks TEXT NULL,
    result ENUM('PASS', 'FAIL', 'ON_HOLD') NOT NULL,
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedback_interview
        FOREIGN KEY (interview_id) REFERENCES interviews(interview_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_technical_rating CHECK (
        technical_rating IS NULL OR technical_rating BETWEEN 0 AND 10
    ),
    CONSTRAINT chk_communication_rating CHECK (
        communication_rating IS NULL OR communication_rating BETWEEN 0 AND 10
    )
) ENGINE=InnoDB;

-- 9. Offers: at most one offer record per application
CREATE TABLE IF NOT EXISTS offers (
    offer_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL UNIQUE,
    designation VARCHAR(150) NOT NULL,
    package_lpa DECIMAL(8,2) NOT NULL,
    offer_date DATE NOT NULL,
    expected_joining_date DATE NULL,
    offer_status ENUM('PENDING', 'ACCEPTED', 'DECLINED', 'EXPIRED')
        NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_offers_application
        FOREIGN KEY (application_id) REFERENCES applications(application_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_offer_package CHECK (package_lpa >= 0),
    INDEX idx_offer_status (offer_status)
) ENGINE=InnoDB;

-- 10. Placements: at most one final placement per offer
CREATE TABLE IF NOT EXISTS placements (
    placement_id INT AUTO_INCREMENT PRIMARY KEY,
    offer_id INT NOT NULL UNIQUE,
    actual_joining_date DATE NOT NULL,
    final_package_lpa DECIMAL(8,2) NOT NULL,
    placement_status ENUM('JOINED', 'NOT_JOINED', 'JOINING_PENDING')
        NOT NULL DEFAULT 'JOINING_PENDING',
    remarks VARCHAR(500) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_placements_offer
        FOREIGN KEY (offer_id) REFERENCES offers(offer_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_placement_package CHECK (final_package_lpa >= 0),
    INDEX idx_placement_status (placement_status)
) ENGINE=InnoDB;

-- Verify that all 10 tables were created.
SHOW TABLES;
