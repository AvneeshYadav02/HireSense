# Manager Features

This document describes the Manager role features in HireSense.

## Overview

Managers have access to project management, employee skill matching, team assignments, and self-service career development features.

## Access

- Login at `/auth/login` with a manager account
- All manager routes are prefixed with `/manager/`
- Manager accounts must be approved by an admin before access is granted

## Features

### Dashboard (`/manager/`)

The manager dashboard provides:
- Project statistics (total, active, planning, completed, on-hold)
- Total team members across all projects
- Recent projects (last 5)
- Recent skill updates from employees

### Project Management

| Route | Description |
|-------|-------------|
| `/manager/projects` | List all owned projects |
| `/manager/projects/create` | Create a new project |
| `/manager/projects/<id>` | View project details |
| `/manager/projects/<id>/edit` | Edit project |
| `/manager/projects/<id>/delete` | Delete project |

Projects have:
- Title and description
- Status: planning, active, completed, on_hold
- Start and end dates
- Skill requirements
- Team assignments

### Skill Dependencies (REQ-9)

| Route | Description |
|-------|-------------|
| `/manager/projects/<id>/skills` | Manage project skill requirements |
| `/manager/projects/<id>/skills/add` | Add skill requirement |
| `/manager/projects/<id>/skills/remove` | Remove skill requirement |

Each skill requirement specifies:
- The skill name
- Whether it's mandatory or optional
- Minimum proficiency level (1-5)

### Employee Skill Matching (REQ-10)

| Route | Description |
|-------|-------------|
| `/manager/projects/<id>/match` | Find employees matching project skills |
| `/manager/projects/<id>/assign` | Assign employee to project |
| `/manager/projects/<id>/team` | View project team |
| `/manager/projects/<id>/unassign/<user_id>` | Remove employee from project |

The matching algorithm:
1. Compares employee skills against project requirements
2. Calculates a match score based on mandatory/optional skills met
3. Ranks employees by match score
4. Shows green highlighting for employees meeting all mandatory skills

### Resume/Skill Updates (REQ-11)

| Route | Description |
|-------|-------------|
| `/manager/updates` | View recent skill/resume changes |
| `/manager/employees/<id>/skills` | View employee's skills |
| `/manager/employees/<id>/skills/verify` | Verify employee's skill |

Managers can:
- Monitor recent skill and resume updates
- View employee skill profiles (no PII like addresses/salary per SRS)
- Verify employee skills

### Self-Service Career Development

Managers retain self-service capabilities for their own career growth:

| Route | Description |
|-------|-------------|
| `/manager/profile` | View own profile |
| `/manager/skills` | Manage own skills |
| `/manager/learning-paths` | View learning paths |
| `/manager/learning-paths/generate` | Generate learning path |
| `/manager/compare` | Compare with target roles |

## RBAC Boundaries

Per SRS Section 5.3.1:
- Managers can view skill sets for projects
- Managers CANNOT view sensitive HR data (addresses, salary)
- Managers retain self-service capabilities for career development
- Managers CANNOT access admin routes (`/admin/`)
- Managers CANNOT access employee-specific routes (`/employee/`)

## Testing

Run manager-specific tests:
```bash
pytest testing/integration/test_manager_flows.py -v
```
