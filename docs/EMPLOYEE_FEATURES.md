# Employee Features

This document describes the Employee role features in HireSense.

## Overview

Employees have access to view their project assignments, manage their skills and resume, compare with target roles, and generate learning paths for career growth.

## Access

- Login at `/auth/login` with an employee account
- All employee routes are prefixed with `/employee/`
- Employee accounts must be approved by an admin before access is granted

## Features

### Dashboard (`/employee/`)

The employee dashboard provides:
- Active project assignments
- Current skills summary
- Resume status
- Active learning path

### Project Assignments (REQ-12)

| Route | Description |
|-------|-------------|
| `/employee/assignments` | List all project assignments |
| `/employee/assignments/<id>` | View assignment details |

Each assignment shows:
- Project title and description
- Manager name
- Role in project
- Project status
- Required skills vs. your skills

### Profile

| Route | Description |
|-------|-------------|
| `/employee/profile` | View own profile |

### Resume Management (REQ-13)

| Route | Description |
|-------|-------------|
| `/employee/resume` | View resume |
| `/employee/resume/upload` | Upload/update resume |
| `/employee/resume/download` | Download resume |
| `/employee/resume/delete` | Delete resume |

Supported formats: PDF, DOC, DOCX

### Skill Management (REQ-13)

| Route | Description |
|-------|-------------|
| `/employee/skills` | View and manage skills |
| `/employee/skills/add` | Add a skill |
| `/employee/skills/update` | Update skill proficiency |
| `/employee/skills/remove` | Remove a skill |

Skills have:
- Proficiency level (1-5 scale)
- Verification status (manager-verified)
- Category (technical, soft, domain)

### Role Comparison (REQ-14)

| Route | Description |
|-------|-------------|
| `/employee/compare` | Compare with target roles |

Compare your current profile with target roles like:
- Senior Developer
- Tech Lead
- DevOps Engineer
- Data Scientist
- QA Engineer
- Security Analyst

The comparison shows:
- Readiness score (percentage)
- Required skills met vs. missing
- Recommended skills
- Estimated time to readiness

### Learning Paths (REQ-14)

| Route | Description |
|-------|-------------|
| `/employee/learning-paths` | View learning paths |
| `/employee/learning-paths/generate` | Generate new learning path |
| `/employee/learning-paths/<id>` | View path details |
| `/employee/learning-paths/<id>/complete` | Mark as completed |
| `/employee/learning-paths/<id>/archive` | Archive path |

Learning paths provide:
- Readiness score
- Skill recommendations (prioritized)
- Learning resources
- Target role requirements

## RBAC Boundaries

Per SRS Section 5.3.1:
- Employees can view only their own data
- Employees can compare skills against advanced roles
- Employees can upgrade their own skills/resumes
- Employees CANNOT view other employees' data
- Employees CANNOT access manager routes (`/manager/`)
- Employees CANNOT access admin routes (`/admin/`)

## Testing

Run employee-specific tests:
```bash
pytest testing/integration/test_employee_flows.py -v
```
