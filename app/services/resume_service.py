"""
Resume Service - Business logic for resume management.

Handles resume uploads, storage, and parsing placeholder.
"""

import os
import json
from typing import Dict, Optional, List
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from app import db
from app.models import Resume, UserSkill, Skill


class ResumeService:
    """Service class for resume-related operations."""

    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}
    UPLOAD_FOLDER = "uploads/resumes"

    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Check if file extension is allowed."""
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in ResumeService.ALLOWED_EXTENSIONS
        )

    @staticmethod
    def get_user_resume(user_id: int) -> Optional[Resume]:
        """Get resume for a user."""
        return Resume.query.filter_by(user_id=user_id).first()

    @staticmethod
    def upload_resume(user_id: int, file: FileStorage) -> Resume:
        """Upload and save a resume file."""
        if not file:
            raise ValueError("No file provided")
        if not file.filename:
            raise ValueError("No filename provided")

        if not ResumeService.allowed_file(file.filename):
            raise ValueError("Invalid file type. Allowed: PDF, DOC, DOCX")

        # Create upload directory if not exists
        import os
        from flask import current_app
        # Make the upload folder absolute based on the app root directory
        if current_app:
            base_dir = os.path.dirname(current_app.root_path)
            upload_folder = os.path.join(base_dir, ResumeService.UPLOAD_FOLDER)
        else:
            upload_folder = os.path.abspath(ResumeService.UPLOAD_FOLDER)
            
        os.makedirs(upload_folder, exist_ok=True)

        # Generate secure filename
        original_filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"{user_id}_{timestamp}_{original_filename}"
        filepath = os.path.join(upload_folder, filename)

        # Check if user already has a resume
        existing = Resume.query.filter_by(user_id=user_id).first()
        if existing:
            # Delete old file if exists
            if existing.file_path and os.path.exists(existing.file_path):
                try:
                    os.remove(existing.file_path)
                except OSError:
                    pass  # Ignore file deletion errors

            # Update existing record
            file.save(filepath)
            existing.file_path = filepath
            existing.original_filename = original_filename
            existing.parsed_content = None  # Reset parsed content
            existing.last_updated = datetime.utcnow()
            db.session.commit()
            return existing

        # Create new resume record
        file.save(filepath)
        resume = Resume(
            user_id=user_id,
            file_path=filepath,
            original_filename=original_filename,
        )
        db.session.add(resume)
        db.session.commit()
        return resume

    @staticmethod
    def delete_resume(user_id: int) -> bool:
        """Delete a user's resume."""
        resume = Resume.query.filter_by(user_id=user_id).first()
        if not resume:
            return False

        # Delete file
        if resume.file_path and os.path.exists(resume.file_path):
            try:
                os.remove(resume.file_path)
            except OSError:
                pass

        db.session.delete(resume)
        db.session.commit()
        return True

    @staticmethod
    def parse_resume_skills(resume_id: int) -> Dict:
        """
        Parse skills from resume content.

        This is a placeholder stub for actual NLP parsing logic.
        In production, this would use transformer models (BERT, spaCy)
        to extract skills from the resume text.
        """
        resume = db.session.get(Resume, resume_id)
        if not resume:
            raise ValueError("Resume not found")

        # Placeholder: In production, implement actual NLP parsing here
        # Example workflow:
        # 1. Read file content (PDF parsing with PyPDF2, python-docx for DOCX)
        # 2. Extract text content
        # 3. Use NLP model to identify skills
        # 4. Match against known skills database

        parsed_content = {
            "extracted_skills": [],
            "parsed_at": datetime.utcnow().isoformat(),
            "parser_version": "stub_v1",
            "status": "pending_implementation",
        }

        resume.parsed_content = json.dumps(parsed_content)
        db.session.commit()
        return parsed_content

    @staticmethod
    def sync_parsed_skills_to_profile(
        user_id: int, skill_names: List[str], default_proficiency: int = 2
    ) -> int:
        """
        Add parsed resume skills to user profile.
        Returns the count of newly added skills.
        """
        count = 0
        for skill_name in skill_names:
            # Find the skill in the database
            skill = Skill.query.filter_by(name=skill_name).first()
            if not skill:
                continue  # Skip unknown skills

            # Check if user already has this skill
            existing = UserSkill.query.filter_by(
                user_id=user_id, skill_id=skill.id
            ).first()
            if existing:
                continue

            # Add skill to user profile
            user_skill = UserSkill(
                user_id=user_id,
                skill_id=skill.id,
                proficiency_level=default_proficiency,
                is_verified=False,
            )
            db.session.add(user_skill)
            count += 1

        db.session.commit()
        return count

    @staticmethod
    def get_recent_resume_updates(limit: int = 20) -> List[Dict]:
        """Get recent resume updates across all employees."""
        recent_resumes = (
            Resume.query
            .join(Resume.user)
            .order_by(Resume.last_updated.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "user_id": r.user_id,
                "username": r.user.username,
                "original_filename": r.original_filename,
                "last_updated": r.last_updated,
            }
            for r in recent_resumes
        ]
