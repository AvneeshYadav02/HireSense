from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from . import db, login_manager


class Department(db.Model):
    """Organizational department for users."""
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    users = db.relationship("User", back_populates="department", lazy="dynamic")

    def __repr__(self):
        return f"<Department {self.name}>"


class Skill(db.Model):
    """Skills catalog for matching and gap analysis."""
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50))  # technical, soft, domain
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user_skills = db.relationship("UserSkill", back_populates="skill", lazy="dynamic", cascade="all, delete-orphan")
    project_skills = db.relationship("ProjectSkill", back_populates="skill", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Skill {self.name}>"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="employee")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # New fields for Manager/Employee features
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)
    job_title = db.Column(db.String(100), nullable=True)

    # Relationships
    department = db.relationship("Department", back_populates="users")
    notifications = db.relationship("Notification", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    resume = db.relationship("Resume", back_populates="user", uselist=False, cascade="all, delete-orphan")
    user_skills = db.relationship("UserSkill", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    learning_paths = db.relationship("LearningPath", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    managed_projects = db.relationship("Project", back_populates="manager", lazy="dynamic", foreign_keys="Project.manager_id")
    project_assignments = db.relationship("ProjectAssignment", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False, default="info")  # success, error, info
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Resume(db.Model):
    """Employee resume storage and parsed content."""
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=True)
    parsed_content = db.Column(db.Text, nullable=True)  # JSON string of parsed skills
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship
    user = db.relationship("User", back_populates="resume")

    def __repr__(self):
        return f"<Resume user_id={self.user_id}>"


class LearningPath(db.Model):
    """Career progression learning paths for users."""
    __tablename__ = "learning_paths"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_role = db.Column(db.String(100), nullable=False)
    generated_content = db.Column(db.Text, nullable=True)  # JSON with learning recommendations
    status = db.Column(db.String(20), default="active", nullable=False)  # active, completed, archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship
    user = db.relationship("User", back_populates="learning_paths")

    def __repr__(self):
        return f"<LearningPath user_id={self.user_id} target={self.target_role}>"


class Project(db.Model):
    """Projects managed by managers."""
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="planning", nullable=False)  # planning, active, completed, on_hold
    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    manager = db.relationship("User", back_populates="managed_projects", foreign_keys=[manager_id])
    required_skills = db.relationship("ProjectSkill", back_populates="project", lazy="dynamic", cascade="all, delete-orphan")
    assignments = db.relationship("ProjectAssignment", back_populates="project", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.title}>"


class ProjectSkill(db.Model):
    """Skill requirements for a project."""
    __tablename__ = "project_skills"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    is_mandatory = db.Column(db.Boolean, default=True, nullable=False)
    minimum_proficiency = db.Column(db.Integer, default=1, nullable=False)  # 1-5 scale

    # Unique constraint
    __table_args__ = (db.UniqueConstraint("project_id", "skill_id", name="uq_project_skill"),)

    # Relationships
    project = db.relationship("Project", back_populates="required_skills")
    skill = db.relationship("Skill", back_populates="project_skills")

    def __repr__(self):
        return f"<ProjectSkill project_id={self.project_id} skill_id={self.skill_id}>"


class ProjectAssignment(db.Model):
    """Employee assignments to projects."""
    __tablename__ = "project_assignments"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    allotted_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    role_in_project = db.Column(db.String(100), nullable=True)  # developer, lead, analyst, etc.
    status = db.Column(db.String(20), default="active", nullable=False)  # active, completed, removed

    # Unique constraint - one assignment per user per project
    __table_args__ = (db.UniqueConstraint("project_id", "user_id", name="uq_project_user"),)

    # Relationships
    project = db.relationship("Project", back_populates="assignments")
    user = db.relationship("User", back_populates="project_assignments")

    def __repr__(self):
        return f"<ProjectAssignment project_id={self.project_id} user_id={self.user_id}>"


class UserSkill(db.Model):
    """User skills with proficiency levels."""
    __tablename__ = "user_skills"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    proficiency_level = db.Column(db.Integer, default=1, nullable=False)  # 1-5 scale
    is_verified = db.Column(db.Boolean, default=False, nullable=False)  # Manager-verified
    acquired_date = db.Column(db.Date, nullable=True)
    last_used_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Unique constraint - one entry per user per skill
    __table_args__ = (db.UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),)

    # Relationships
    user = db.relationship("User", back_populates="user_skills")
    skill = db.relationship("Skill", back_populates="user_skills")

    def __repr__(self):
        return f"<UserSkill user_id={self.user_id} skill_id={self.skill_id} level={self.proficiency_level}>"


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))
