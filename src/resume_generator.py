import os
import subprocess
from datetime import datetime
from typing import Dict, Optional, Tuple, NamedTuple

from llm_agents import ModelConfig, ResumeQualityChecker, QualityCheckResult, ContentOptimizer
from latex_formatter import (
    format_experience,
    format_project,
    format_education,
    format_publications,
    format_contact_links,
    escape_latex,
    format_skills,
    format_certifications
)

class CompilationResult(NamedTuple):
    """Result of resume compilation."""
    success: bool
    pdf_path: Optional[str]
    error_message: Optional[str]

class ResumeGenerator:
    def __init__(
        self,
        template_path: str = 'resume_template.tex',
        quality_checker_config: Optional[ModelConfig] = None,
        polisher_config: Optional[ModelConfig] = None,
        critic_config: Optional[ModelConfig] = None,
        max_optimization_rounds: int = 3
    ):
        """
        Initialize ResumeGenerator.
        
        Args:
            template_path (str): Path to LaTeX template file
            quality_checker_config (Optional[ModelConfig]): Configuration for quality checker
            polisher_config (Optional[ModelConfig]): Configuration for content polisher
            critic_config (Optional[ModelConfig]): Configuration for content critic
            max_optimization_rounds (int): Maximum rounds for content optimization
        """
        self.template_path = template_path
        self.quality_checker = ResumeQualityChecker(quality_checker_config)
        self.optimizer = ContentOptimizer(
            max_rounds=max_optimization_rounds,
            polisher_config=polisher_config,
            critic_config=critic_config
        )
        
    def _read_template(self) -> str:
        """Read the LaTeX template file."""
        with open(self.template_path, 'r') as file:
            return file.read()
            
    def generate_latex(self, data: Dict, job_description: Optional[str] = None, optimize_content: bool = True) -> Tuple[str, QualityCheckResult]:
        """
        Generate LaTeX resume from template and data.
        
        Args:
            data (Dict): Resume data
            job_description (str, optional): Job description for content optimization
            optimize_content (bool): Whether to optimize content using LLM
            
        Returns:
            Tuple[str, QualityCheckResult]: Generated LaTeX content and quality check results
        """
        template = self._read_template()
        
        # Format contact information
        additional_links = format_contact_links(data.get('github'), data.get('portfolio'))
        
        # Optimize summary and skills if enabled
        summary = (
            self.optimizer.optimize_content(data['summary'], job_description, content_type="summary")
            if optimize_content and job_description
            else data['summary']
        )
        summary = escape_latex(summary)
        
        skills_text = (
            self.optimizer.optimize_content(data['skills'], job_description, content_type="skills")
            if optimize_content and job_description
            else data['skills']
        )
        skills = format_skills(skills_text)
        
        # Format and optimize experiences
        experiences = []
        for exp in data['experience']:
            experiences.append(format_experience(
                exp['company'],
                exp['role'],
                exp['dates'],
                exp['location'],
                exp.get('projects', [])
            ))
        
        # Format and optimize projects (optional)
        projects_section = ""
        if data.get('projects'):
            projects = []
            for proj in data['projects']:
                # Optimize the description
                description = (
                    self.optimizer.optimize_content(proj['description'], job_description, content_type="projects")
                    if optimize_content and job_description
                    else proj['description']
                )
                projects.append(format_project(
                    proj['name'],
                    proj['technologies'],
                    proj['dates'],
                    description
                ))
            projects_section = "\n\\section{Projects}\n\\resumeSubHeadingListStart\n" + \
                             '\n'.join(projects) + \
                             "\n\\resumeSubHeadingListEnd"
        
        # Format education
        education = []
        for edu in data['education']:
            education.append(format_education(
                edu['school'],
                edu['degree'],
                edu['dates'],
                edu['location'],
                edu.get('gpa')
            ))
        
        # Format certifications
        certifications_section = format_certifications(data.get('certifications', []))
        
        # Format publications
        publications_section = format_publications([
            escape_latex(pub) for pub in data.get('publications', [])
        ])
        
        # Ensure linkedin URL starts with https://
        linkedin_url = data['linkedin']
        if linkedin_url and not linkedin_url.startswith(('http://', 'https://')):
            linkedin_url = 'https://' + linkedin_url.lstrip('/ ')

        # Replace placeholders in template
        resume = template.format(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            location=data['location'],
            linkedin=linkedin_url,  # Use the fixed URL
            additional_links=additional_links,
            summary=escape_latex(summary),
            skills=skills,
            experience='\n'.join(experiences),
            projects=projects_section,
            education='\n'.join(education),
            certifications_section=certifications_section,
            publications_section=publications_section
        )
        
        # Perform quality check on the entire resume
        quality_result = None
        if optimize_content:
            quality_result = self.quality_checker.check_resume(resume)
        
        return resume, quality_result
        
    def save_and_compile(self, latex_content: str, base_filepath: str) -> CompilationResult:
        """
        Save LaTeX content to file and compile to PDF.
        
        Args:
            latex_content (str): LaTeX content to compile
            base_filepath (str): The base path for the output files (e.g., 'output/folder/resume')
            
        Returns:
            CompilationResult: Result of the compilation process
        """
        tex_file = f"{base_filepath}.tex"
        pdf_file = f"{base_filepath}.pdf"
        output_dir = os.path.dirname(base_filepath)

        # Save LaTeX content
        with open(tex_file, 'w') as f:
            f.write(latex_content)
        
        # Compile LaTeX to PDF
        try:
            # Use -interaction=nonstopmode to prevent hanging on errors
            process = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', output_dir, tex_file],
                check=True,
                capture_output=True,
                text=True
            )
            return CompilationResult(
                success=True,
                pdf_path=pdf_file,
                error_message=None
            )
        except subprocess.CalledProcessError as e:
            # Provide detailed error log from LaTeX
            log_output = e.stdout + e.stderr
            return CompilationResult(
                success=False,
                pdf_path=None,
                error_message=f"Error compiling LaTeX. See log for details:\n\n{log_output}"
            ) 