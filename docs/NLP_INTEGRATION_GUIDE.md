# NLP Integration Guide for HireSense

This guide explains how to add Natural Language Processing (NLP) capabilities to HireSense for intelligent resume parsing, skill extraction, and learning path generation.

## Table of Contents

1. [Overview](#overview)
2. [Current Implementation](#current-implementation)
3. [Architecture for NLP Integration](#architecture-for-nlp-integration)
4. [Prerequisites](#prerequisites)
5. [Step-by-Step Integration](#step-by-step-integration)
6. [Testing Your NLP Features](#testing-your-nlp-features)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

HireSense currently uses placeholder stubs for NLP functionality. This guide helps you replace these stubs with real NLP implementations using:

- **spaCy**: For entity recognition, text processing, and skill extraction
- **BERT/Transformers**: For semantic similarity, resume analysis, and intelligent matching

### What NLP Can Do in HireSense

| Feature | Current State | With NLP |
|---------|---------------|----------|
| Resume Parsing | Stores raw text | Extracts skills, experience, education automatically |
| Skill Extraction | Manual entry | Automatic extraction from resume text |
| Learning Paths | Template-based | Personalized based on semantic analysis |
| Role Comparison | Simple gap analysis | Semantic similarity matching |
| Employee Matching | Exact skill matches | Fuzzy matching with synonyms |

---

## Current Implementation

The current codebase has placeholder stubs in three service files where NLP will be integrated:

### 1. Resume Service (`app/services/resume_service.py`)

**Current stub:**
```python
def _parse_resume_content(self, file_path: str) -> dict:
    """
    Placeholder for NLP-based resume parsing.
    TODO: Integrate spaCy or transformers for:
    - Skill extraction
    - Experience parsing
    - Education extraction
    """
    return {"skills": [], "experience": [], "education": []}
```

**Integration point:** Parse uploaded resume files and extract structured data.

### 2. Skill Service (`app/services/skill_service.py`)

**Current stub:**
```python
@staticmethod
def extract_skills_from_text(text: str) -> List[str]:
    """
    Placeholder for NLP-based skill extraction.
    TODO: Implement with spaCy NER or BERT-based classification.
    """
    return []
```

**Integration point:** Extract skills from free-form text (resumes, job descriptions).

### 3. Learning Path Service (`app/services/learning_path_service.py`)

**Current stub:**
```python
def _generate_ai_learning_path(self, user_skills: List[str], target_role: str) -> dict:
    """
    Placeholder for AI/NLP-based learning path generation.
    TODO: Integrate GPT/BERT for personalized recommendations.
    """
    return {"modules": [], "estimated_duration": "N/A"}
```

**Integration point:** Generate personalized learning recommendations using semantic analysis.

---

## Architecture for NLP Integration

### Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Flask Application                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Resume     │  │    Skill     │  │  Learning    │      │
│  │   Service    │  │   Service    │  │    Path      │      │
│  │              │  │              │  │   Service    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │               │
│         └─────────────────┼──────────────────┘               │
│                           │                                  │
├───────────────────────────┼──────────────────────────────────┤
│                           │                                  │
│                   ┌───────▼────────┐                         │
│                   │  NLP Manager   │                         │
│                   │   (Singleton)  │                         │
│                   └───────┬────────┘                         │
│                           │                                  │
│          ┌────────────────┼────────────────┐                │
│          │                │                │                │
│  ┌───────▼──────┐  ┌─────▼─────┐  ┌───────▼──────┐        │
│  │    spaCy     │  │   BERT    │  │  PDF/DOCX    │        │
│  │   Models     │  │  Models   │  │   Parsers    │        │
│  └──────────────┘  └───────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **NLP Manager** - Singleton class that loads and manages NLP models
2. **Document Parsers** - Extract text from PDF/DOCX files
3. **Entity Extractors** - Use spaCy NER for skill/experience extraction
4. **Semantic Analyzers** - Use BERT for similarity and matching
5. **Service Integration** - Replace stubs in existing services

---

## Prerequisites

### Python Packages

Add these to `requirements.txt`:

```txt
# NLP Core
spacy>=3.7.0
transformers>=4.35.0
torch>=2.1.0  # or tensorflow>=2.15.0

# Document Processing
python-docx>=1.0.0
PyPDF2>=3.0.0
pdfplumber>=0.10.0

# Additional NLP Tools
scikit-learn>=1.3.0
numpy>=1.24.0
sentence-transformers>=2.2.2  # For semantic similarity
```

### spaCy Models

Download required spaCy models:

```bash
# English language model with NER
python -m spacy download en_core_web_lg

# For better accuracy (larger model)
python -m spacy download en_core_web_trf
```

### BERT Models

The code will auto-download these from HuggingFace on first use:
- `bert-base-uncased` - General purpose BERT
- `sentence-transformers/all-MiniLM-L6-v2` - Fast semantic similarity

---

## Step-by-Step Integration

### Step 1: Create NLP Manager

Create `app/services/nlp_manager.py`:

```python
"""
NLP Manager - Centralized NLP model management.
Implements singleton pattern for efficient model loading.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict
import spacy
from transformers import AutoTokenizer, AutoModel
import torch
from sentence_transformers import SentenceTransformer


class NLPManager:
    """Singleton class to manage NLP models and avoid redundant loading."""

    _instance: Optional['NLPManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.spacy_model: Optional[spacy.Language] = None
        self.sentence_transformer: Optional[SentenceTransformer] = None
        self.bert_tokenizer = None
        self.bert_model = None
        self._initialized = True

    def load_spacy_model(self, model_name: str = "en_core_web_lg"):
        """Load spaCy model for NER and text processing."""
        if self.spacy_model is None:
            try:
                self.spacy_model = spacy.load(model_name)
                print(f"✓ Loaded spaCy model: {model_name}")
            except OSError:
                print(f"✗ Model '{model_name}' not found. Downloading...")
                os.system(f"python -m spacy download {model_name}")
                self.spacy_model = spacy.load(model_name)
        return self.spacy_model

    def load_sentence_transformer(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """Load sentence transformer for semantic similarity."""
        if self.sentence_transformer is None:
            self.sentence_transformer = SentenceTransformer(model_name)
            print(f"✓ Loaded sentence transformer: {model_name}")
        return self.sentence_transformer

    def load_bert_model(self, model_name: str = "bert-base-uncased"):
        """Load BERT model for advanced NLP tasks."""
        if self.bert_model is None:
            self.bert_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.bert_model = AutoModel.from_pretrained(model_name)
            print(f"✓ Loaded BERT model: {model_name}")
        return self.bert_tokenizer, self.bert_model

    def get_skill_synonyms(self) -> Dict[str, List[str]]:
        """
        Return a dictionary of skill synonyms for fuzzy matching.
        This is a simple approach - can be enhanced with word embeddings.
        """
        return {
            "python": ["python3", "py", "python programming"],
            "javascript": ["js", "node.js", "nodejs", "node"],
            "react": ["reactjs", "react.js"],
            "angular": ["angularjs", "angular.js"],
            "docker": ["containerization", "containers"],
            "kubernetes": ["k8s", "k8"],
            "machine learning": ["ml", "artificial intelligence", "ai"],
            "database": ["sql", "nosql", "postgres", "mongodb"],
            # Add more as needed
        }


# Create singleton instance
nlp_manager = NLPManager()
```

### Step 2: Create Document Parsers

Create `app/services/document_parser.py`:

```python
"""
Document parsers for extracting text from various file formats.
"""

from pathlib import Path
from typing import Optional
import PyPDF2
import pdfplumber
from docx import Document


class DocumentParser:
    """Parse text from PDF and DOCX files."""

    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """Extract text from PDF using pdfplumber (better than PyPDF2)."""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e2:
                print(f"Fallback also failed: {e2}")
                raise ValueError(f"Could not parse PDF: {e}")

        return text.strip()

    @staticmethod
    def parse_docx(file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise ValueError(f"Could not parse DOCX: {e}")

    @staticmethod
    def parse_doc(file_path: str) -> str:
        """
        Extract text from legacy DOC file.
        Note: This requires additional libraries like textract or antiword.
        For now, raise an error with helpful message.
        """
        raise NotImplementedError(
            "Legacy .doc format requires additional setup. "
            "Please use .docx or .pdf format, or install 'textract' library."
        )

    @classmethod
    def parse_file(cls, file_path: str) -> str:
        """Auto-detect file type and parse accordingly."""
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext == '.pdf':
            return cls.parse_pdf(file_path)
        elif ext == '.docx':
            return cls.parse_docx(file_path)
        elif ext == '.doc':
            return cls.parse_doc(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
```

### Step 3: Integrate Resume Parsing

Update `app/services/resume_service.py`:

```python
from app.services.nlp_manager import nlp_manager
from app.services.document_parser import DocumentParser

class ResumeService:
    # ... existing code ...

    @staticmethod
    def _parse_resume_content(file_path: str) -> dict:
        """
        Parse resume using NLP to extract structured information.

        Returns:
            dict with keys: skills, experience, education, contact, summary
        """
        # Step 1: Extract text from document
        try:
            text = DocumentParser.parse_file(file_path)
        except Exception as e:
            print(f"Document parsing failed: {e}")
            return {"skills": [], "experience": [], "education": []}

        if not text or len(text) < 50:
            return {"skills": [], "experience": [], "education": []}

        # Step 2: Load spaCy model
        nlp = nlp_manager.load_spacy_model()
        doc = nlp(text)

        # Step 3: Extract entities
        skills = ResumeService._extract_skills_from_doc(doc, text)
        experience = ResumeService._extract_experience(doc, text)
        education = ResumeService._extract_education(doc, text)
        contact = ResumeService._extract_contact_info(doc, text)

        return {
            "skills": skills,
            "experience": experience,
            "education": education,
            "contact": contact,
            "summary": text[:500]  # First 500 chars as summary
        }

    @staticmethod
    def _extract_skills_from_doc(doc, text: str) -> List[str]:
        """Extract skills using pattern matching and NER."""
        skills = set()

        # Common technical skills patterns
        skill_keywords = [
            "python", "java", "javascript", "react", "angular", "vue",
            "docker", "kubernetes", "aws", "azure", "gcp",
            "sql", "postgresql", "mongodb", "redis",
            "machine learning", "deep learning", "nlp",
            "git", "ci/cd", "agile", "scrum"
        ]

        text_lower = text.lower()
        for skill in skill_keywords:
            if skill in text_lower:
                skills.add(skill.title())

        # Use NER to find organizations/products (often skills)
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT"] and len(ent.text) > 2:
                skills.add(ent.text)

        return list(skills)

    @staticmethod
    def _extract_experience(doc, text: str) -> List[dict]:
        """Extract work experience sections."""
        experiences = []

        # Look for date patterns and job titles
        # This is a simplified version - enhance as needed
        lines = text.split('\n')
        for i, line in enumerate(lines):
            # Look for year patterns (e.g., "2020-2023", "Jan 2020")
            if any(str(year) in line for year in range(2000, 2030)):
                experiences.append({
                    "period": line.strip(),
                    "description": lines[i+1] if i+1 < len(lines) else ""
                })

        return experiences

    @staticmethod
    def _extract_education(doc, text: str) -> List[dict]:
        """Extract education information."""
        education = []

        # Look for degree keywords
        degree_keywords = ["bachelor", "master", "phd", "doctorate", "degree"]
        lines = text.split('\n')

        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in degree_keywords):
                education.append({
                    "degree": line.strip(),
                    "details": lines[i+1] if i+1 < len(lines) else ""
                })

        return education

    @staticmethod
    def _extract_contact_info(doc, text: str) -> dict:
        """Extract contact information using NER."""
        contact = {"email": None, "phone": None}

        # Extract email using regex
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact["email"] = emails[0]

        # Extract phone using NER or pattern
        for ent in doc.ents:
            if ent.label_ == "PHONE":
                contact["phone"] = ent.text
                break

        return contact
```

### Step 4: Integrate Skill Extraction

Update `app/services/skill_service.py`:

```python
from app.services.nlp_manager import nlp_manager

class SkillService:
    # ... existing code ...

    @staticmethod
    def extract_skills_from_text(text: str) -> List[str]:
        """
        Extract skills from free-form text using NLP.

        Args:
            text: Free-form text (resume, job description, etc.)

        Returns:
            List of extracted skill names
        """
        if not text or len(text.strip()) < 10:
            return []

        # Load spaCy model
        nlp = nlp_manager.load_spacy_model()
        doc = nlp(text.lower())

        extracted_skills = set()

        # Method 1: Match against known skills from database
        db_skills = Skill.query.all()
        db_skill_names = [s.name.lower() for s in db_skills]

        for skill_name in db_skill_names:
            if skill_name in text.lower():
                # Find the original capitalization from DB
                for s in db_skills:
                    if s.name.lower() == skill_name:
                        extracted_skills.add(s.name)
                        break

        # Method 2: Use spaCy NER for technical terms
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "GPE"]:
                # Check if it's a known technology/skill
                if ent.text.lower() in db_skill_names:
                    extracted_skills.add(ent.text.title())

        # Method 3: Check for synonyms
        synonyms = nlp_manager.get_skill_synonyms()
        for canonical, variants in synonyms.items():
            for variant in variants:
                if variant in text.lower():
                    extracted_skills.add(canonical.title())
                    break

        return list(extracted_skills)

    @staticmethod
    def compute_semantic_similarity(
        skills1: List[str],
        skills2: List[str]
    ) -> float:
        """
        Compute semantic similarity between two skill sets using BERT.

        Returns:
            Float between 0 and 1 indicating similarity
        """
        if not skills1 or not skills2:
            return 0.0

        # Load sentence transformer
        model = nlp_manager.load_sentence_transformer()

        # Encode skill sets
        text1 = ", ".join(skills1)
        text2 = ", ".join(skills2)

        embeddings = model.encode([text1, text2])

        # Compute cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

        return float(similarity)
```

### Step 5: Integrate Learning Path Generation

Update `app/services/learning_path_service.py`:

```python
from app.services.nlp_manager import nlp_manager

class LearningPathService:
    # ... existing code ...

    def _generate_ai_learning_path(
        self,
        user_skills: List[str],
        target_role: str
    ) -> dict:
        """
        Generate AI-powered learning path using semantic analysis.

        Args:
            user_skills: List of user's current skills
            target_role: Target role name

        Returns:
            Dict with modules, duration, and recommendations
        """
        # Get role template
        role_template = self.role_templates.get(target_role.lower())
        if not role_template:
            return {"modules": [], "estimated_duration": "N/A"}

        required_skills = role_template["skills"]

        # Load sentence transformer for semantic matching
        model = nlp_manager.load_sentence_transformer()

        # Encode skills
        user_skill_text = ", ".join(user_skills)
        required_skills_texts = required_skills

        all_texts = [user_skill_text] + required_skills_texts
        embeddings = model.encode(all_texts)

        user_embedding = embeddings[0]
        required_embeddings = embeddings[1:]

        # Compute similarity scores for each required skill
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(
            [user_embedding],
            required_embeddings
        )[0]

        # Generate modules based on similarity
        modules = []
        for i, skill in enumerate(required_skills):
            similarity_score = similarities[i]

            if similarity_score < 0.3:  # Low familiarity
                level = "Beginner"
                duration = "8-12 weeks"
            elif similarity_score < 0.6:  # Some familiarity
                level = "Intermediate"
                duration = "4-6 weeks"
            else:  # High familiarity
                level = "Advanced"
                duration = "2-3 weeks"

            modules.append({
                "skill": skill,
                "level": level,
                "duration": duration,
                "priority": "High" if similarity_score < 0.4 else "Medium",
                "similarity_score": round(similarity_score, 2)
            })

        # Sort by priority (lowest similarity first)
        modules.sort(key=lambda x: x["similarity_score"])

        # Calculate total duration
        total_weeks = len(modules) * 4  # Average estimate
        estimated_duration = f"{total_weeks} weeks"

        return {
            "modules": modules,
            "estimated_duration": estimated_duration,
            "personalized": True
        }
```

### Step 6: Update Requirements

Add NLP dependencies to `requirements.txt`:

```bash
cd /d/Git-Projects/HireSense
cat >> requirements.txt << EOL

# NLP Dependencies
spacy>=3.7.0
en-core-web-lg @ https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.7.0/en_core_web_lg-3.7.0-py3-none-any.whl
transformers>=4.35.0
torch>=2.1.0
python-docx>=1.0.0
PyPDF2>=3.0.0
pdfplumber>=0.10.0
scikit-learn>=1.3.0
sentence-transformers>=2.2.2
EOL
```

### Step 7: Environment Configuration

Update `.env` with NLP settings:

```env
# NLP Configuration
NLP_ENABLED=true
SPACY_MODEL=en_core_web_lg
BERT_MODEL=bert-base-uncased
SENTENCE_TRANSFORMER_MODEL=sentence-transformers/all-MiniLM-L6-v2
NLP_CACHE_DIR=./nlp_models
```

---

## Testing Your NLP Features

### Unit Tests

Create `testing/unit/test_nlp.py`:

```python
import pytest
from app.services.nlp_manager import nlp_manager, NLPManager
from app.services.document_parser import DocumentParser
from app.services.skill_service import SkillService


class TestNLPManager:
    def test_singleton_pattern(self):
        """Test that NLPManager is a singleton."""
        manager1 = NLPManager()
        manager2 = NLPManager()
        assert manager1 is manager2

    def test_load_spacy_model(self):
        """Test loading spaCy model."""
        nlp = nlp_manager.load_spacy_model()
        assert nlp is not None

        # Test NER
        doc = nlp("Python and Docker are required skills")
        assert len(doc) > 0


class TestDocumentParser:
    def test_parse_pdf(self, tmp_path):
        """Test PDF parsing (requires test PDF file)."""
        # You'll need to create test files
        pass

    def test_parse_docx(self, tmp_path):
        """Test DOCX parsing."""
        pass


class TestSkillExtraction:
    def test_extract_skills_from_text(self, app, db, skills):
        """Test skill extraction from text."""
        with app.app_context():
            text = """
            I am proficient in Python, JavaScript, and React.
            I have experience with Docker and Kubernetes.
            """
            extracted = SkillService.extract_skills_from_text(text)
            assert len(extracted) > 0
            assert any("python" in s.lower() for s in extracted)
```

### Integration Tests

Add to `testing/integration/test_employee_flows.py`:

```python
def test_resume_upload_with_nlp_parsing(client, employee, login_employee, skills):
    """Test resume upload triggers NLP parsing."""
    # Upload resume
    data = {
        'resume_file': (BytesIO(b'Resume content with Python and Docker'), 'test.pdf')
    }
    response = client.post('/employee/resume/upload', data=data)

    # Check that skills were extracted
    resume = Resume.query.filter_by(user_id=employee.id).first()
    assert resume is not None
    assert resume.parsed_content is not None
```

---

## Best Practices

### 1. Model Loading

**DO:**
```python
# Use singleton pattern for model loading
nlp = nlp_manager.load_spacy_model()
```

**DON'T:**
```python
# Don't load models repeatedly
nlp = spacy.load("en_core_web_lg")  # Every time!
```

### 2. Error Handling

Always handle NLP errors gracefully:

```python
try:
    skills = SkillService.extract_skills_from_text(text)
except Exception as e:
    logger.error(f"NLP extraction failed: {e}")
    skills = []  # Fallback to empty list
```

### 3. Caching

Cache NLP results to avoid reprocessing:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def extract_skills_cached(text: str) -> tuple:
    return tuple(SkillService.extract_skills_from_text(text))
```

### 4. Async Processing

For large documents, use background tasks:

```python
from celery import shared_task

@shared_task
def parse_resume_async(resume_id: int):
    """Parse resume in background."""
    resume = Resume.query.get(resume_id)
    content = ResumeService._parse_resume_content(resume.file_path)
    resume.parsed_content = json.dumps(content)
    db.session.commit()
```

### 5. Model Updates

Keep models updated:

```bash
# Update spaCy models
pip install -U spacy
python -m spacy download en_core_web_lg

# Update transformers
pip install -U transformers torch
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Models Not Loading

**Error:** `OSError: [E050] Can't find model 'en_core_web_lg'`

**Solution:**
```bash
python -m spacy download en_core_web_lg
```

#### Issue 2: CUDA Out of Memory

**Error:** `RuntimeError: CUDA out of memory`

**Solution:**
```python
# Use CPU instead of GPU
import torch
device = torch.device("cpu")
model.to(device)
```

Or use smaller models:
```python
nlp_manager.load_spacy_model("en_core_web_sm")  # Smaller model
```

#### Issue 3: Slow Performance

**Solution:**
- Use `en_core_web_md` instead of `en_core_web_lg`
- Implement caching
- Use batch processing
- Consider using GPU if available

#### Issue 4: PDF Parsing Fails

**Error:** `Could not parse PDF`

**Solution:**
```bash
# Install additional dependencies
pip install pdfplumber textract
```

#### Issue 5: Memory Issues in Docker

**Solution:**
Update `docker-compose.yml`:
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 4G  # Increase memory limit
```

---

## Advanced Topics

### 1. Custom Skill Ontology

Create a skill taxonomy:

```python
SKILL_ONTOLOGY = {
    "Programming Languages": {
        "Python": ["Django", "Flask", "FastAPI"],
        "JavaScript": ["React", "Vue", "Angular"],
    },
    "DevOps": {
        "Containerization": ["Docker", "Kubernetes"],
        "CI/CD": ["Jenkins", "GitLab CI", "GitHub Actions"],
    },
}
```

### 2. Fine-tuning BERT

Fine-tune BERT on job descriptions:

```python
from transformers import Trainer, TrainingArguments

# Prepare dataset
# Train model
# Save for inference
```

### 3. Multi-language Support

Add support for multiple languages:

```python
LANGUAGE_MODELS = {
    "en": "en_core_web_lg",
    "es": "es_core_news_lg",
    "fr": "fr_core_news_lg",
}
```

---

## Resources

### Documentation
- [spaCy Documentation](https://spacy.io/usage)
- [Transformers Documentation](https://huggingface.co/docs/transformers)
- [Sentence Transformers](https://www.sbert.net/)

### Tutorials
- [spaCy 101](https://spacy.io/usage/spacy-101)
- [BERT for Resume Parsing](https://towardsdatascience.com/bert-for-dummies-step-by-step-tutorial-fb90890ffe03)
- [NLP with Python](https://realpython.com/natural-language-processing-spacy-python/)

### Pre-trained Models
- [spaCy Models](https://spacy.io/models)
- [HuggingFace Model Hub](https://huggingface.co/models)

---

## Conclusion

This guide provides a complete roadmap for integrating NLP into HireSense. Start with basic spaCy integration for skill extraction, then gradually add BERT for semantic analysis and learning path personalization.

**Next Steps:**
1. Install dependencies
2. Create `nlp_manager.py` and `document_parser.py`
3. Update the three service stubs
4. Write tests
5. Deploy and monitor performance

For questions or issues, refer to the [HireSense GitHub Issues](https://github.com/your-repo/issues) or the resources listed above.

---

**Last Updated:** 2026-03-24
**Version:** 1.0
**Maintainer:** HireSense Development Team
