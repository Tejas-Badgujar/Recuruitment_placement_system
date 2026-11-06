-- RPMS Step 11: read-only integration verification queries
USE recruitment_placement_db;

-- 1. Confirm all ten expected tables exist.
SHOW TABLES;

-- 2. Candidate and company counts.
SELECT candidate_status, COUNT(*) AS total
FROM candidates
GROUP BY candidate_status;

SELECT company_status, COUNT(*) AS total
FROM companies
GROUP BY company_status;

-- 3. Job counts.
SELECT job_status, COUNT(*) AS total
FROM jobs
GROUP BY job_status;

-- 4. Eligibility/application data integrity.
SELECT a.application_id, a.application_status,
       c.candidate_id, CONCAT(c.first_name, ' ', c.last_name) AS candidate_name,
       j.job_id, j.job_title
FROM applications a
JOIN candidates c ON c.candidate_id = a.candidate_id
JOIN jobs j ON j.job_id = a.job_id
ORDER BY a.application_id;

-- 5. Application status totals (compare with Reports > Application Funnel).
SELECT application_status, COUNT(*) AS total
FROM applications
GROUP BY application_status;

-- 6. Interview and feedback linkage.
SELECT i.interview_id, i.application_id, i.round_number,
       i.interview_status, f.result, f.technical_rating,
       f.communication_rating
FROM interviews i
LEFT JOIN interview_feedback f ON f.interview_id = i.interview_id
ORDER BY i.application_id, i.round_number;

-- 7. Offer/application status consistency.
SELECT o.offer_id, o.offer_status, a.application_id, a.application_status
FROM offers o
JOIN applications a ON a.application_id = o.application_id
ORDER BY o.offer_id;

-- 8. Placement/offer/application status consistency.
SELECT p.placement_id, p.placement_status, p.actual_joining_date,
       p.final_package_lpa, o.offer_status,
       a.application_id, a.application_status
FROM placements p
JOIN offers o ON o.offer_id = p.offer_id
JOIN applications a ON a.application_id = o.application_id
ORDER BY p.placement_id;

-- 9. Detect duplicate candidate/job applications (should return no rows).
SELECT candidate_id, job_id, COUNT(*) AS duplicate_count
FROM applications
GROUP BY candidate_id, job_id
HAVING COUNT(*) > 1;

-- 10. Detect duplicate interview rounds (should return no rows).
SELECT application_id, round_number, COUNT(*) AS duplicate_count
FROM interviews
GROUP BY application_id, round_number
HAVING COUNT(*) > 1;

-- 11. Detect duplicate offers per application (should return no rows).
SELECT application_id, COUNT(*) AS duplicate_count
FROM offers
GROUP BY application_id
HAVING COUNT(*) > 1;

-- 12. Detect duplicate placements per offer (should return no rows).
SELECT offer_id, COUNT(*) AS duplicate_count
FROM placements
GROUP BY offer_id
HAVING COUNT(*) > 1;

-- 13. Joined placement consistency: JOINED placement should have JOINED application.
SELECT p.placement_id, p.placement_status, a.application_status
FROM placements p
JOIN offers o ON o.offer_id = p.offer_id
JOIN applications a ON a.application_id = o.application_id
WHERE p.placement_status = 'JOINED'
  AND a.application_status <> 'JOINED';

-- 14. Declined/expired offers should not remain OFFERED.
SELECT o.offer_id, o.offer_status, a.application_status
FROM offers o
JOIN applications a ON a.application_id = o.application_id
WHERE o.offer_status IN ('DECLINED', 'EXPIRED')
  AND a.application_status = 'OFFERED';
