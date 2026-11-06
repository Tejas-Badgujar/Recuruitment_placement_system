# Step 11 – System Integration Test Plan

## A. Preflight
1. Activate the project's `.venv`.
2. Install dependencies: `python -m pip install -r requirements.txt`.
3. Confirm `.env` points to `recruitment_placement_db`.
4. Run `python system_check.py`.
5. Do not continue while any preflight check is FAIL.

## B. End-to-end business workflow
Use separate test candidates/jobs for branches that end in JOINED and NOT_JOINED.

1. Create or select an ACTIVE candidate with matching qualification, branch,
   passing year, percentage, backlog count and required skills.
2. Create or select an ACTIVE company.
3. Create an OPEN job with a future deadline and matching eligibility criteria.
4. Run eligibility check; the candidate should be eligible.
5. Apply; application status should be APPLIED.
6. Try duplicate application; it must be blocked.
7. Move application APPLIED -> SHORTLISTED.
8. Schedule interview round 1 for a future date/time.
9. Confirm application status becomes INTERVIEW.
10. Reschedule the interview; verify the new date/time and RESCHEDULED status.
11. Mark interview COMPLETED and submit feedback.
12. Schedule another round if required; verify duplicate round is rejected.
13. Move application INTERVIEW -> SELECTED.
14. Create offer; verify offer PENDING and application OFFERED.
15. Accept offer.
16. Create placement with JOINING_PENDING.
17. On/after joining date, mark placement JOINED.
18. Verify application status becomes JOINED.
19. Use a separate selected candidate/application for declined or expired offer.
20. Verify DECLINED/EXPIRED offer moves application to REJECTED.

## C. Negative tests
- Inactive candidate cannot apply.
- Closed job cannot accept application.
- Candidate missing one required skill is ineligible.
- Duplicate application is rejected.
- Interview cannot be scheduled for APPLIED or REJECTED application.
- Duplicate interview round is rejected.
- Feedback cannot be submitted before interview is COMPLETED.
- Duplicate feedback is rejected.
- Invalid application status jump is rejected.
- Offer cannot be created before application reaches SELECTED.
- Duplicate offer is rejected.
- Placement cannot be created from PENDING/DECLINED/EXPIRED offer.
- Duplicate placement is rejected.
- Finalised placement cannot be edited or finalised again.

## D. Reports
Run all eight options under Reports & Dashboard. Compare tabular counts with
`sql/integration_verification.sql`. Export each tabular report and open the CSV.

## E. Evidence to record
For each test, record: test case, input IDs, expected result, actual result,
PASS/FAIL, and screenshot or SQL output. Never use production records for
destructive tests. Do not manually edit status fields to fake a successful flow.
