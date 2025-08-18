"""
PDF Generation Service
Generates professional PDF resumes using RenderCV.
"""

import json
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

try:
    pass

    RENDERCV_AVAILABLE = True
except ImportError:
    RENDERCV_AVAILABLE = False

from app.data.resume_models import Resume
from app.logger import logger


class PDFGenerationService:
    """Service for generating PDF resumes using RenderCV."""

    def __init__(self, output_dir: Optional[str] = None):
        if not RENDERCV_AVAILABLE:
            raise ImportError("RenderCV not installed. Run: pip install rendercv")

        self.output_dir = (
            Path(output_dir) if output_dir else Path.cwd() / "generated_resumes"
        )
        self.output_dir.mkdir(exist_ok=True)

        # Template directory for custom RenderCV themes
        self.templates_dir = Path(__file__).parent.parent / "templates" / "rendercv"
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    async def generate_pdf_resume(
        self,
        resume: Resume,
        template_name: str = "moderncv",
        theme_options: Optional[Dict[str, Any]] = None,
        output_filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a PDF resume using RenderCV."""
        try:
            # Convert resume to RenderCV format
            rendercv_data = self._convert_to_rendercv_format(resume)

            # Apply theme options
            if theme_options:
                rendercv_data.update(theme_options)

            # Create temporary files
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Write YAML file
                yaml_file = temp_path / "resume.yaml"
                with open(yaml_file, "w", encoding="utf-8") as f:
                    yaml.dump(
                        rendercv_data, f, default_flow_style=False, allow_unicode=True
                    )

                # Generate output filename
                if not output_filename:
                    safe_name = "".join(
                        c
                        for c in resume.contact_info.full_name
                        if c.isalnum() or c in (" ", "-", "_")
                    ).rstrip()
                    safe_name = safe_name.replace(" ", "_")
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_filename = f"{safe_name}_{timestamp}.pdf"

                output_path = self.output_dir / output_filename

                # Generate PDF using RenderCV
                success = await self._run_rendercv(
                    yaml_file=yaml_file,
                    output_path=output_path,
                    template_name=template_name,
                )

                if success and output_path.exists():
                    # Get file info
                    file_size = output_path.stat().st_size

                    result = {
                        "success": True,
                        "pdf_path": str(output_path),
                        "filename": output_filename,
                        "file_size": file_size,
                        "template": template_name,
                        "generated_at": datetime.now().isoformat(),
                    }

                    logger.info(f"Successfully generated PDF resume: {output_filename}")
                    return result
                else:
                    raise Exception("PDF generation failed")

        except Exception as e:
            logger.error(f"Error generating PDF resume: {e}")
            return {
                "success": False,
                "error": str(e),
                "generated_at": datetime.now().isoformat(),
            }

    async def _run_rendercv(
        self, yaml_file: Path, output_path: Path, template_name: str
    ) -> bool:
        """Run RenderCV command to generate PDF."""
        try:
            # Import RenderCV modules
            from rendercv.cli.commands import render_command
            from rendercv.data_models import CurriculumVitae

            # Load the YAML file
            with open(yaml_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Create CV object
            cv = CurriculumVitae(**data)

            # Set output directory
            output_dir = output_path.parent

            # Render the CV
            render_command.render_cv(
                cv=cv,
                output_directory=output_dir,
                theme=template_name,
                dont_generate_png=True,  # Only generate PDF
                dont_generate_html=True,  # Only generate PDF
                dont_generate_markdown=True,  # Only generate PDF
                latex_path=None,
                pdf_path=output_path,
            )

            return output_path.exists()

        except Exception as e:
            logger.error(f"Error running RenderCV: {e}")
            return False

    def _convert_to_rendercv_format(self, resume: Resume) -> Dict[str, Any]:
        """Convert JobPilot Resume to RenderCV format."""

        # Basic CV structure for RenderCV
        cv_data = {
            "cv": {
                "name": resume.contact_info.full_name,
                "location": resume.contact_info.location or "",
                "email": resume.contact_info.email,
                "phone": resume.contact_info.phone or "",
                "website": resume.contact_info.website_url or "",
                "social_networks": [],
            },
            "design": {
                "theme": "moderncv",
                "color": "blue",
                "disable_page_numbering": False,
                "page_numbering_style": "NAME - Page PAGE_NUMBER of TOTAL_PAGES",
                "disable_last_updated_date": False,
                "last_updated_date_style": "Last updated in TODAY",
                "header_separator_between_connections": "",
            },
        }

        # Add social networks
        social_networks = []
        if resume.contact_info.linkedin_url:
            social_networks.append(
                {
                    "network": "LinkedIn",
                    "username": self._extract_username_from_url(
                        resume.contact_info.linkedin_url, "linkedin"
                    ),
                }
            )
        if resume.contact_info.github_url:
            social_networks.append(
                {
                    "network": "GitHub",
                    "username": self._extract_username_from_url(
                        resume.contact_info.github_url, "github"
                    ),
                }
            )
        cv_data["cv"]["social_networks"] = social_networks

        # Add summary
        if resume.summary:
            cv_data["cv"]["summary"] = resume.summary

        # Add work experience
        if resume.work_experience:
            cv_data["cv"]["experience"] = []
            for exp in resume.work_experience:
                exp_data = {
                    "company": exp.company,
                    "position": exp.position,
                    "location": exp.location or "",
                    "start_date": (
                        exp.start_date.strftime("%Y-%m") if exp.start_date else ""
                    ),
                    "end_date": (
                        exp.end_date.strftime("%Y-%m") if exp.end_date else "present"
                    ),
                    "highlights": exp.achievements or [],
                }
                cv_data["cv"]["experience"].append(exp_data)

        # Add education
        if resume.education:
            cv_data["cv"]["education"] = []
            for edu in resume.education:
                edu_data = {
                    "institution": edu.institution,
                    "area": edu.field_of_study or edu.degree,
                    "degree": edu.degree,
                    "location": edu.location or "",
                    "start_date": (
                        edu.start_date.strftime("%Y-%m") if edu.start_date else ""
                    ),
                    "end_date": edu.end_date.strftime("%Y-%m") if edu.end_date else "",
                    "highlights": edu.honors or [],
                }
                if edu.gpa:
                    edu_data["gpa"] = f"{edu.gpa:.2f}"
                cv_data["cv"]["education"].append(edu_data)

        # Add skills
        if resume.skills:
            # Group skills by category
            skill_categories = {}
            for skill in resume.skills:
                category = skill.category or "Technical Skills"
                if category not in skill_categories:
                    skill_categories[category] = []
                skill_categories[category].append(skill.name)

            cv_data["cv"]["technologies"] = []
            for category, skills in skill_categories.items():
                cv_data["cv"]["technologies"].append(
                    {"label": category, "details": ", ".join(skills)}
                )

        # Add projects
        if resume.projects:
            cv_data["cv"]["projects"] = []
            for project in resume.projects:
                proj_data = {
                    "name": project.name,
                    "date": (
                        project.end_date.strftime("%Y-%m") if project.end_date else ""
                    ),
                    "highlights": project.achievements or [project.description],
                    "url": project.url or project.github_url or "",
                }
                cv_data["cv"]["projects"].append(proj_data)

        # Add certifications
        if resume.certifications:
            cv_data["cv"]["certificates"] = []
            for cert in resume.certifications:
                cert_data = {
                    "name": cert.name,
                    "date": (
                        cert.issue_date.strftime("%Y-%m") if cert.issue_date else ""
                    ),
                    "url": cert.url or "",
                }
                cv_data["cv"]["certificates"].append(cert_data)

        return cv_data

    def _extract_username_from_url(self, url: str, platform: str) -> str:
        """Extract username from social media URL."""
        try:
            if platform == "linkedin":
                # Extract from LinkedIn URL
                if "/in/" in url:
                    return url.split("/in/")[1].split("/")[0]
                elif "/pub/" in url:
                    return url.split("/pub/")[1].split("/")[0]
            elif platform == "github":
                # Extract from GitHub URL
                if "github.com/" in url:
                    return url.split("github.com/")[1].split("/")[0]

            # Fallback: return the URL as-is
            return url

        except Exception:
            return url

    def get_available_templates(self) -> List[Dict[str, str]]:
        """Get list of available RenderCV templates."""
        try:
            # Default RenderCV themes
            default_themes = [
                {"name": "moderncv", "description": "Modern and clean design"},
                {"name": "classic", "description": "Classic professional layout"},
                {"name": "academic", "description": "Academic-style template"},
                {"name": "engineering", "description": "Engineering-focused template"},
                {"name": "sb2nov", "description": "Compact single-page design"},
            ]

            # Check for custom themes in templates directory
            custom_themes = []
            if self.templates_dir.exists():
                for theme_dir in self.templates_dir.iterdir():
                    if theme_dir.is_dir() and (theme_dir / "template.py").exists():
                        custom_themes.append(
                            {
                                "name": theme_dir.name,
                                "description": f"Custom theme: {theme_dir.name}",
                                "custom": True,
                            }
                        )

            return default_themes + custom_themes

        except Exception as e:
            logger.error(f"Error getting available templates: {e}")
            return [{"name": "moderncv", "description": "Default template"}]

    async def generate_preview_image(
        self,
        resume: Resume,
        template_name: str = "moderncv",
        output_filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a preview image of the resume."""
        try:
            # This would generate a PNG preview using RenderCV
            # For now, we'll return a placeholder response

            if not output_filename:
                safe_name = "".join(
                    c
                    for c in resume.contact_info.full_name
                    if c.isalnum() or c in (" ", "-", "_")
                ).rstrip()
                safe_name = safe_name.replace(" ", "_")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{safe_name}_preview_{timestamp}.png"

            preview_path = self.output_dir / output_filename

            # TODO: Implement actual preview generation
            # For now, return a mock result
            result = {
                "success": True,
                "preview_path": str(preview_path),
                "filename": output_filename,
                "template": template_name,
                "generated_at": datetime.now().isoformat(),
                "note": "Preview generation not yet implemented",
            }

            return result

        except Exception as e:
            logger.error(f"Error generating preview image: {e}")
            return {
                "success": False,
                "error": str(e),
                "generated_at": datetime.now().isoformat(),
            }

    def cleanup_old_files(self, days_old: int = 7) -> int:
        """Clean up old generated files."""
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            deleted_count = 0

            for file_path in self.output_dir.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1

            logger.info(f"Cleaned up {deleted_count} old files")
            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")
            return 0


class ResumeExportService:
    """Service for exporting resumes in various formats."""

    def __init__(self, pdf_service: PDFGenerationService):
        self.pdf_service = pdf_service

    async def export_resume(
        self,
        resume: Resume,
        export_format: str,
        template_name: str = "moderncv",
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Export resume in the specified format."""

        export_format = export_format.lower()
        options = options or {}

        try:
            if export_format == "pdf":
                return await self.pdf_service.generate_pdf_resume(
                    resume=resume,
                    template_name=template_name,
                    theme_options=options.get("theme_options"),
                    output_filename=options.get("filename"),
                )

            elif export_format == "json":
                return await self._export_json(resume, options)

            elif export_format == "yaml":
                return await self._export_yaml(resume, options)

            elif export_format == "txt":
                return await self._export_text(resume, options)

            else:
                raise ValueError(f"Unsupported export format: {export_format}")

        except Exception as e:
            logger.error(f"Error exporting resume in {export_format} format: {e}")
            return {"success": False, "error": str(e), "format": export_format}

    async def _export_json(
        self, resume: Resume, options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Export resume as JSON."""
        try:
            output_filename = (
                options.get("filename")
                or f"{resume.contact_info.full_name.replace(' ', '_')}_resume.json"
            )
            output_path = self.pdf_service.output_dir / output_filename

            # Convert resume to dict and handle dates
            resume_dict = resume.dict()

            # Convert dates to strings for JSON serialization
            def convert_dates(obj):
                if isinstance(obj, dict):
                    return {k: convert_dates(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_dates(item) for item in obj]
                elif isinstance(obj, (date, datetime)):
                    return obj.isoformat()
                else:
                    return obj

            resume_dict = convert_dates(resume_dict)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(resume_dict, f, indent=2, ensure_ascii=False)

            return {
                "success": True,
                "file_path": str(output_path),
                "filename": output_filename,
                "format": "json",
                "file_size": output_path.stat().st_size,
            }

        except Exception as e:
            raise Exception(f"JSON export failed: {e}")

    async def _export_yaml(
        self, resume: Resume, options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Export resume as YAML (RenderCV format)."""
        try:
            output_filename = (
                options.get("filename")
                or f"{resume.contact_info.full_name.replace(' ', '_')}_resume.yaml"
            )
            output_path = self.pdf_service.output_dir / output_filename

            # Convert to RenderCV format
            rendercv_data = self.pdf_service._convert_to_rendercv_format(resume)

            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    rendercv_data, f, default_flow_style=False, allow_unicode=True
                )

            return {
                "success": True,
                "file_path": str(output_path),
                "filename": output_filename,
                "format": "yaml",
                "file_size": output_path.stat().st_size,
            }

        except Exception as e:
            raise Exception(f"YAML export failed: {e}")

    async def _export_text(
        self, resume: Resume, options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Export resume as plain text."""
        try:
            output_filename = (
                options.get("filename")
                or f"{resume.contact_info.full_name.replace(' ', '_')}_resume.txt"
            )
            output_path = self.pdf_service.output_dir / output_filename

            # Generate plain text resume
            text_content = self._generate_text_resume(resume)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text_content)

            return {
                "success": True,
                "file_path": str(output_path),
                "filename": output_filename,
                "format": "txt",
                "file_size": output_path.stat().st_size,
            }

        except Exception as e:
            raise Exception(f"Text export failed: {e}")

    def _generate_text_resume(self, resume: Resume) -> str:
        """Generate a plain text version of the resume."""
        lines = []

        # Header
        lines.append(resume.contact_info.full_name.upper())
        lines.append("=" * len(resume.contact_info.full_name))
        lines.append("")

        # Contact info
        lines.append(f"Email: {resume.contact_info.email}")
        if resume.contact_info.phone:
            lines.append(f"Phone: {resume.contact_info.phone}")
        if resume.contact_info.location:
            lines.append(f"Location: {resume.contact_info.location}")
        if resume.contact_info.linkedin_url:
            lines.append(f"LinkedIn: {resume.contact_info.linkedin_url}")
        if resume.contact_info.github_url:
            lines.append(f"GitHub: {resume.contact_info.github_url}")
        lines.append("")

        # Summary
        if resume.summary:
            lines.append("PROFESSIONAL SUMMARY")
            lines.append("-" * 20)
            lines.append(resume.summary)
            lines.append("")

        # Experience
        if resume.work_experience:
            lines.append("WORK EXPERIENCE")
            lines.append("-" * 15)
            for exp in resume.work_experience:
                lines.append(f"{exp.position} at {exp.company}")
                if exp.location:
                    lines.append(f"Location: {exp.location}")
                date_range = f"{exp.start_date.strftime('%Y-%m') if exp.start_date else 'Unknown'} - "
                date_range += (
                    f"{exp.end_date.strftime('%Y-%m') if exp.end_date else 'Present'}"
                )
                lines.append(f"Duration: {date_range}")
                if exp.description:
                    lines.append(f"Description: {exp.description}")
                if exp.achievements:
                    lines.append("Achievements:")
                    for achievement in exp.achievements:
                        lines.append(f"  • {achievement}")
                lines.append("")

        # Education
        if resume.education:
            lines.append("EDUCATION")
            lines.append("-" * 9)
            for edu in resume.education:
                lines.append(f"{edu.degree} in {edu.field_of_study or 'N/A'}")
                lines.append(f"Institution: {edu.institution}")
                if edu.location:
                    lines.append(f"Location: {edu.location}")
                if edu.gpa:
                    lines.append(f"GPA: {edu.gpa:.2f}")
                lines.append("")

        # Skills
        if resume.skills:
            lines.append("SKILLS")
            lines.append("-" * 6)
            skill_categories = {}
            for skill in resume.skills:
                category = skill.category or "Technical Skills"
                if category not in skill_categories:
                    skill_categories[category] = []
                skill_categories[category].append(skill.name)

            for category, skills in skill_categories.items():
                lines.append(f"{category}: {', '.join(skills)}")
            lines.append("")

        # Projects
        if resume.projects:
            lines.append("PROJECTS")
            lines.append("-" * 8)
            for project in resume.projects:
                lines.append(f"{project.name}")
                lines.append(f"Description: {project.description}")
                if project.technologies:
                    lines.append(f"Technologies: {', '.join(project.technologies)}")
                if project.url:
                    lines.append(f"URL: {project.url}")
                lines.append("")

        # Certifications
        if resume.certifications:
            lines.append("CERTIFICATIONS")
            lines.append("-" * 14)
            for cert in resume.certifications:
                lines.append(f"{cert.name} - {cert.issuer}")
                if cert.issue_date:
                    lines.append(f"Issued: {cert.issue_date.strftime('%Y-%m')}")
                if cert.credential_id:
                    lines.append(f"Credential ID: {cert.credential_id}")
                lines.append("")

        return "\n".join(lines)


# Factory functions
def create_pdf_service(output_dir: Optional[str] = None) -> PDFGenerationService:
    """Create a PDF generation service."""
    return PDFGenerationService(output_dir=output_dir)


def create_export_service(output_dir: Optional[str] = None) -> ResumeExportService:
    """Create a resume export service."""
    pdf_service = create_pdf_service(output_dir)
    return ResumeExportService(pdf_service)
