"""
Unit tests for service layer.
"""
import pytest
import os
import json
from io import BytesIO
from werkzeug.datastructures import FileStorage
from app.services.skill_service import SkillService
from app.services.project_service import ProjectService
from app.services.learning_path_service import LearningPathService
from app.services.resume_service import ResumeService
from app.models import UserSkill, ProjectSkill, ProjectAssignment, Resume


class TestSkillService:
    """Tests for SkillService."""

    def test_get_all_skills(self, db_session, skills):
        """Test retrieving all skills."""
        all_skills = SkillService.get_all_skills()
        assert len(all_skills) >= len(skills)

    def test_get_user_skills(self, db_session, employee_with_skills):
        """Test retrieving user skills."""
        user_skills = SkillService.get_user_skills(employee_with_skills.id)
        assert len(user_skills) == 2
        assert any(s["skill_name"] == "Python" for s in user_skills)

    def test_add_user_skill(self, db_session, employee_user, skills):
        """Test adding a skill to a user."""
        skill = SkillService.add_user_skill(employee_user.id, skills[0].id, 3)
        assert skill.proficiency_level == 3
        assert skill.is_verified is False

    def test_add_user_skill_invalid_proficiency(self, db_session, employee_user, skills):
        """Test adding skill with invalid proficiency."""
        with pytest.raises(ValueError, match="Proficiency level must be between 1 and 5"):
            SkillService.add_user_skill(employee_user.id, skills[0].id, 6)

    def test_add_duplicate_skill(self, db_session, employee_with_skills, skills):
        """Test adding a skill user already has."""
        with pytest.raises(ValueError, match="already has this skill"):
            SkillService.add_user_skill(employee_with_skills.id, skills[0].id, 2)

    def test_update_user_skill(self, db_session, employee_with_skills, skills):
        """Test updating skill proficiency."""
        updated = SkillService.update_user_skill(employee_with_skills.id, skills[0].id, 5)
        assert updated.proficiency_level == 5

    def test_remove_user_skill(self, db_session, employee_with_skills, skills):
        """Test removing a user skill."""
        result = SkillService.remove_user_skill(employee_with_skills.id, skills[0].id)
        assert result is True
        # Verify it's gone
        user_skills = SkillService.get_user_skills(employee_with_skills.id)
        assert not any(s["skill_name"] == "Python" for s in user_skills)

    def test_get_project_skill_requirements(self, db_session, project_with_skills):
        """Test getting project skill requirements."""
        requirements = SkillService.get_project_skill_requirements(project_with_skills.id)
        assert len(requirements) == 2
        python_req = next(r for r in requirements if r["skill_name"] == "Python")
        assert python_req["is_mandatory"] is True

    def test_match_employees_to_project(self, db_session, project_with_skills, employee_with_skills):
        """Test matching employees to project."""
        matches = SkillService.match_employees_to_project(project_with_skills.id)
        assert len(matches) > 0
        # Employee with Python skill should be in matches
        employee_match = next((m for m in matches if m["user_id"] == employee_with_skills.id), None)
        assert employee_match is not None
        assert employee_match["mandatory_met"] is True

    def test_calculate_skill_gap(self, db_session, employee_with_skills):
        """Test calculating skill gaps."""
        gaps = SkillService.calculate_skill_gap(employee_with_skills.id)
        # Should identify gaps for skills not at level 3+
        assert len(gaps) > 0


class TestProjectService:
    """Tests for ProjectService."""

    def test_get_manager_projects(self, db_session, project, manager_user):
        """Test getting manager's projects."""
        projects = ProjectService.get_manager_projects(manager_user.id)
        assert len(projects) >= 1
        assert project in projects

    def test_create_project(self, db_session, manager_user):
        """Test creating a project."""
        proj = ProjectService.create_project(
            manager_id=manager_user.id,
            title="New Project",
            description="Test description",
        )
        assert proj.id is not None
        assert proj.title == "New Project"
        assert proj.status == "planning"

    def test_create_project_empty_title(self, db_session, manager_user):
        """Test creating project with empty title."""
        with pytest.raises(ValueError, match="title is required"):
            ProjectService.create_project(manager_user.id, "  ")

    def test_update_project(self, db_session, project):
        """Test updating a project."""
        updated = ProjectService.update_project(
            project_id=project.id,
            title="Updated Title",
            status="active",
        )
        assert updated.title == "Updated Title"
        assert updated.status == "active"

    def test_update_project_invalid_status(self, db_session, project):
        """Test updating project with invalid status."""
        with pytest.raises(ValueError, match="Invalid status"):
            ProjectService.update_project(project.id, status="invalid")

    def test_assign_employee_to_project(self, db_session, project, employee_user):
        """Test assigning employee to project."""
        assignment = ProjectService.assign_employee_to_project(
            project.id, employee_user.id, "Developer"
        )
        assert assignment.status == "active"
        assert assignment.role_in_project == "Developer"

    def test_assign_non_employee(self, db_session, project, manager_user):
        """Test assigning non-employee to project."""
        with pytest.raises(ValueError, match="Only employees"):
            ProjectService.assign_employee_to_project(project.id, manager_user.id)

    def test_get_employee_assignments(self, db_session, assignment, employee_user):
        """Test getting employee assignments."""
        assignments = ProjectService.get_employee_assignments(employee_user.id)
        assert len(assignments) >= 1

    def test_remove_employee_from_project(self, db_session, assignment):
        """Test removing employee from project."""
        result = ProjectService.remove_employee_from_project(
            assignment.project_id, assignment.user_id
        )
        assert result is True
        # Verify status changed
        db_session.refresh(assignment)
        assert assignment.status == "removed"

    def test_get_project_team(self, db_session, assignment, project):
        """Test getting project team."""
        team = ProjectService.get_project_team(project.id)
        assert len(team) >= 1
        assert any(m["role_in_project"] == "Developer" for m in team)

    def test_get_project_stats(self, db_session, project, manager_user):
        """Test getting project statistics."""
        stats = ProjectService.get_project_stats(manager_user.id)
        assert stats["total_projects"] >= 1
        assert "active" in stats["by_status"] or stats["by_status"].get("active", 0) >= 0


class TestLearningPathService:
    """Tests for LearningPathService."""

    def test_get_available_target_roles(self):
        """Test getting available target roles."""
        roles = LearningPathService.get_available_target_roles()
        assert len(roles) > 0
        assert any(r["id"] == "senior_developer" for r in roles)

    def test_generate_learning_path(self, db_session, employee_user):
        """Test generating a learning path."""
        path = LearningPathService.generate_learning_path(
            employee_user.id, "senior_developer"
        )
        assert path.id is not None
        assert path.status == "active"
        assert path.target_role == "senior_developer"

    def test_generate_learning_path_invalid_role(self, db_session, employee_user):
        """Test generating path with invalid role."""
        with pytest.raises(ValueError, match="Unknown target role"):
            LearningPathService.generate_learning_path(employee_user.id, "invalid_role")

    def test_get_user_learning_paths(self, db_session, learning_path, employee_user):
        """Test getting user's learning paths."""
        paths = LearningPathService.get_user_learning_paths(employee_user.id)
        assert len(paths) >= 1
        assert learning_path in paths

    def test_compare_roles(self, db_session, employee_with_skills):
        """Test comparing roles."""
        comparison = LearningPathService.compare_roles(
            employee_with_skills.id, "senior_developer"
        )
        assert "readiness_score" in comparison
        assert "required_skills" in comparison
        assert comparison["target_role_title"] == "Senior Developer"

    def test_compare_roles_invalid(self, db_session, employee_user):
        """Test comparing with invalid role."""
        with pytest.raises(ValueError, match="Unknown target role"):
            LearningPathService.compare_roles(employee_user.id, "invalid_role")

    def test_update_learning_path_status(self, db_session, learning_path):
        """Test updating learning path status."""
        updated = LearningPathService.update_learning_path_status(
            learning_path.id, "completed"
        )
        assert updated.status == "completed"

    def test_update_learning_path_invalid_status(self, db_session, learning_path):
        """Test updating with invalid status."""
        with pytest.raises(ValueError, match="Invalid status"):
            LearningPathService.update_learning_path_status(learning_path.id, "invalid")


class TestResumeService:
    """Tests for ResumeService."""

    def test_get_user_resume(self, app, db_session, employee_user):
        """Test retrieving user's resume."""
        with app.app_context():
            resume = ResumeService.get_user_resume(employee_user.id)
            assert resume is None  # No resume yet

    def test_upload_resume_pdf(self, app, db_session, employee_user, tmp_path):
        """Test uploading a PDF resume."""
        with app.app_context():
            # Create a test PDF file
            test_file = tmp_path / "test_resume.pdf"
            test_file.write_bytes(b"%PDF-1.4\nTest resume content")

            with open(test_file, 'rb') as f:
                file_storage = FileStorage(
                    stream=f,
                    filename="test_resume.pdf",
                    content_type="application/pdf"
                )
                resume = ResumeService.upload_resume(employee_user.id, file_storage)

            assert resume is not None
            assert resume.original_filename == "test_resume.pdf"
            assert resume.user_id == employee_user.id
            assert os.path.exists(resume.file_path)

            # Cleanup
            if os.path.exists(resume.file_path):
                os.remove(resume.file_path)

    def test_upload_resume_docx(self, app, db_session, employee_user, tmp_path):
        """Test uploading a DOCX resume."""
        with app.app_context():
            test_file = tmp_path / "test_resume.docx"
            test_file.write_bytes(b"PK\x03\x04")  # DOCX magic bytes

            with open(test_file, 'rb') as f:
                file_storage = FileStorage(
                    stream=f,
                    filename="test_resume.docx",
                    content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                resume = ResumeService.upload_resume(employee_user.id, file_storage)

            assert resume is not None
            assert resume.original_filename == "test_resume.docx"

            # Cleanup
            if os.path.exists(resume.file_path):
                os.remove(resume.file_path)

    def test_upload_resume_invalid_extension(self, app, db_session, employee_user):
        """Test uploading file with invalid extension."""
        with app.app_context():
            file_storage = FileStorage(
                stream=BytesIO(b"test content"),
                filename="test.txt",
                content_type="text/plain"
            )

            with pytest.raises(ValueError, match="Invalid file type"):
                ResumeService.upload_resume(employee_user.id, file_storage)

    def test_upload_resume_no_filename(self, app, db_session, employee_user):
        """Test uploading file without filename."""
        with app.app_context():
            file_storage = FileStorage(
                stream=BytesIO(b"test content"),
                filename="",
                content_type="application/pdf"
            )

            with pytest.raises(ValueError, match="No file provided|No filename provided"):
                ResumeService.upload_resume(employee_user.id, file_storage)

    def test_upload_resume_replaces_existing(self, app, db_session, employee_user, tmp_path):
        """Test that uploading a new resume replaces the old one."""
        with app.app_context():
            # Upload first resume
            test_file1 = tmp_path / "resume1.pdf"
            test_file1.write_bytes(b"%PDF-1.4\nFirst resume")

            with open(test_file1, 'rb') as f:
                file_storage1 = FileStorage(
                    stream=f,
                    filename="resume1.pdf",
                    content_type="application/pdf"
                )
                resume1 = ResumeService.upload_resume(employee_user.id, file_storage1)
                old_path = resume1.file_path

            # Upload second resume
            test_file2 = tmp_path / "resume2.pdf"
            test_file2.write_bytes(b"%PDF-1.4\nSecond resume")

            with open(test_file2, 'rb') as f:
                file_storage2 = FileStorage(
                    stream=f,
                    filename="resume2.pdf",
                    content_type="application/pdf"
                )
                resume2 = ResumeService.upload_resume(employee_user.id, file_storage2)

            # Check only one resume exists
            assert resume2.original_filename == "resume2.pdf"
            assert not os.path.exists(old_path)  # Old file deleted

            # Cleanup
            if os.path.exists(resume2.file_path):
                os.remove(resume2.file_path)

    def test_delete_resume(self, app, db_session, employee_user, tmp_path):
        """Test deleting a resume."""
        with app.app_context():
            # Upload resume first
            test_file = tmp_path / "test.pdf"
            test_file.write_bytes(b"%PDF-1.4\nTest")

            with open(test_file, 'rb') as f:
                file_storage = FileStorage(
                    stream=f,
                    filename="test.pdf",
                    content_type="application/pdf"
                )
                resume = ResumeService.upload_resume(employee_user.id, file_storage)
                file_path = resume.file_path

            # Delete resume
            result = ResumeService.delete_resume(employee_user.id)
            assert result is True

            # Verify file and DB record deleted
            assert not os.path.exists(file_path)
            assert ResumeService.get_user_resume(employee_user.id) is None

    def test_delete_resume_nonexistent(self, app, db_session, employee_user):
        """Test deleting when no resume exists."""
        with app.app_context():
            result = ResumeService.delete_resume(employee_user.id)
            assert result is False



class TestProjectServiceAdvanced:
    """Additional tests for ProjectService edge cases."""

    def test_delete_project(self, app, db_session, project):
        """Test deleting a project."""
        with app.app_context():
            result = ProjectService.delete_project(project.id)
            assert result is True
            assert ProjectService.get_project_by_id(project.id) is None

    def test_delete_nonexistent_project(self, app, db_session):
        """Test deleting a project that doesn't exist."""
        with app.app_context():
            result = ProjectService.delete_project(99999)
            assert result is False

    def test_update_nonexistent_project(self, app, db_session):
        """Test updating a project that doesn't exist."""
        with app.app_context():
            with pytest.raises(ValueError, match="not found"):
                ProjectService.update_project(99999, title="New Title")

    def test_update_project_empty_title(self, app, db_session, project):
        """Test updating project with empty title."""
        with app.app_context():
            with pytest.raises(ValueError, match="cannot be empty"):
                ProjectService.update_project(project.id, title="  ")

    def test_add_project_skill(self, app, db_session, project, skills):
        """Test adding skill requirement to project."""
        with app.app_context():
            skill_req = ProjectService.add_project_skill(
                project.id,
                skills[0].id,
                is_mandatory=True,
                minimum_proficiency=3
            )
            assert skill_req.is_mandatory is True
            assert skill_req.minimum_proficiency == 3

    def test_add_project_skill_duplicate(self, app, db_session, project_with_skills, skills):
        """Test adding duplicate skill to project."""
        with app.app_context():
            with pytest.raises(ValueError, match="already added to this project"):
                ProjectService.add_project_skill(project_with_skills.id, skills[0].id)

    def test_remove_project_skill(self, app, db_session, project_with_skills, skills):
        """Test removing skill from project."""
        with app.app_context():
            result = ProjectService.remove_project_skill(project_with_skills.id, skills[0].id)
            assert result is True

    def test_remove_nonexistent_project_skill(self, app, db_session, project, skills):
        """Test removing skill that isn't in project."""
        with app.app_context():
            result = ProjectService.remove_project_skill(project.id, skills[0].id)
            assert result is False

    def test_get_project_skills(self, app, db_session, project_with_skills):
        """Test getting project skill requirements."""
        with app.app_context():
            skill_reqs = ProjectService.get_project_skills(project_with_skills.id)
            assert len(skill_reqs) == 2

    def test_assign_duplicate_employee(self, app, db_session, assignment):
        """Test assigning employee already on project."""
        with app.app_context():
            with pytest.raises(ValueError, match="already assigned"):
                ProjectService.assign_employee_to_project(
                    assignment.project_id,
                    assignment.user_id,
                    "Developer"
                )

    def test_remove_nonexistent_assignment(self, app, db_session, project, employee_user):
        """Test removing employee not on project."""
        with app.app_context():
            result = ProjectService.remove_employee_from_project(project.id, employee_user.id)
            assert result is False


class TestSkillServiceAdvanced:
    """Additional tests for SkillService edge cases."""

    def test_update_nonexistent_skill(self, app, db_session, employee_user, skills):
        """Test updating skill user doesn't have."""
        with app.app_context():
            with pytest.raises(ValueError, match="does not have this skill"):
                SkillService.update_user_skill(employee_user.id, skills[0].id, 4)

    def test_remove_nonexistent_skill(self, app, db_session, employee_user, skills):
        """Test removing skill user doesn't have."""
        with app.app_context():
            result = SkillService.remove_user_skill(employee_user.id, skills[0].id)
            assert result is False

