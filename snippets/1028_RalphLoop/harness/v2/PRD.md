# Educational Portal – PRD v2 (vague UI/UX hint)

This is a variant of PRD.md for a follow-up Ralph loop run. The feature set is
identical to PRD.md. The only difference is one added line under UI/UX below.
The first run (see ../README.md and ../snippet/index.md) said nothing about
UI/UX and produced a working but poorly structured single-page dashboard with
no navigation and no cross-component data sync. This run tests whether a
short, non-specific hint is enough to change that outcome, without listing
the concrete issues (routing, live sync, etc.) found in the first run.

## Stack
- Frontend: React + Vite + TypeScript
- Backend: Node.js + Express
- Database: SQLite with better-sqlite3
- Auth: JWT tokens

## General guidance

Pay attention to UI/UX in every task below: the result should be genuinely pleasant and easy to use, not just functionally correct. This is not a separate checklist item, keep it in mind while implementing each feature.

Write appropriate tests for each implemented feature. This is not a separate checklist item either, tests should accompany each feature as it is built.

## Mandatory Features

- [x] User authentication (login/logout, JWT)
- [x] Role system: Student, Teacher, Administrator, Super-administrator
- [x] Class management (start date + identifier, e.g. 2009/C)
- [x] Subject management (description, required books, lessons)
- [x] Assign subjects to classes per year, including which teacher holds it
- [x] Grade entry for students by teacher
- [x] Year-end grade entry by teacher
- [x] README with setup instructions

## Optional Features

- [x] Semester grade entry
- [x] Weighted grade average calculation and display
- [x] Class average statistics for teachers
- [x] Event creation by admin, visible to all
- [x] Timetable management
- [x] Dark/light mode

## Rules
- Implement one task at a time
- Commit after each completed feature
- Update progress.txt after each commit
- If all tasks are done, output <promise>COMPLETE</promise>
