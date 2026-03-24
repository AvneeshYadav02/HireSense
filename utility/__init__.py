"""
HireSense Utility Package

This package contains utility scripts and CLI commands for managing the
HireSense application, including database seeding, maintenance tasks,
and development helpers.

Available commands:
    - seed-users: Generate fake users for testing
    - seed-data: Seed departments, skills, and projects
"""

from .seed_users import seed_users, seed_data

__all__ = ["seed_users", "seed_data"]
