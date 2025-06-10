from typing import List, Optional
from dataclasses import dataclass
from .llm_base import BaseAgent, ModelConfig
import re

@dataclass
class QualityCheckResult:
    """Result of resume quality check."""
    is_approved: bool
    feedback: str
    suggested_changes: List[str]
    estimated_pages: float

class ResumeQualityChecker(BaseAgent):
    """Agent responsible for final quality checks of the resume."""
    
    _SYSTEM_CONTENT = """You are a professional resume quality control specialist.
    Your goal is to ensure the resume meets professional standards, is properly formatted,
    and fits within acceptable length limits."""
    
    def __init__(self, model_config: Optional[ModelConfig] = None):
        """Initialize with optional model configuration."""
        # Use low temperature for consistent quality checks
        default_config = ModelConfig(temperature=0.3)
        super().__init__(model_config or default_config)
    
    def check_resume(self, latex_content: str) -> QualityCheckResult:
        """
        Check the overall quality of the resume.
        
        Args:
            latex_content (str): The LaTeX content to check
            
        Returns:
            QualityCheckResult: Results of the quality check
        """
        template = """Review the following LaTeX resume content for quality and provide detailed feedback.

Content to Review:
{content}

Analyze the following aspects:
1. Length Estimation:
   - Estimate the number of pages based on content volume
   - Suggest specific content to trim if exceeds 2 pages
   - Consider LaTeX formatting and spacing

2. Formatting and Structure:
   - Check for LaTeX syntax errors or typos
   - Verify proper use of sections and environments
   - Check for consistent formatting

3. Professional Standards:
   - Identify any unprofessional content or phrasing
   - Check for appropriate tone and language
   - Verify consistent tense usage

4. Content Organization:
   - Evaluate section ordering and hierarchy
   - Check for redundant information
   - Verify proper use of bullet points

Provide your response in the following format:
ESTIMATED_PAGES: [number]
APPROVED: [YES/NO]
FEEDBACK: [general feedback]
SUGGESTED_CHANGES:
- [change 1]
- [change 2]
...etc"""

        prompt = self._create_prompt(template, content=latex_content)
        response = self._call_openai(prompt, self._SYSTEM_CONTENT)
        
        # Parse response
        lines = response.split('\n')
        pages_str = next(line for line in lines if line.startswith('ESTIMATED_PAGES:')).split(':')[1].strip()
        match = re.search(r'\d+(\.\d+)?', pages_str)
        if match:
            estimated_pages = float(match.group(0))
        else:
            estimated_pages = 1.0  # default if not found
        is_approved = 'YES' in next(line for line in lines if line.startswith('APPROVED:')).split(':')[1].strip()
        
        feedback_start = response.find('FEEDBACK:') + 9
        changes_start = response.find('SUGGESTED_CHANGES:')
        feedback = response[feedback_start:changes_start].strip()
        
        changes_section = response[changes_start:].split('\n')[1:]  # Skip the "SUGGESTED_CHANGES:" line
        suggested_changes = [change.strip('- ').strip() for change in changes_section if change.strip().startswith('-')]
        
        return QualityCheckResult(
            is_approved=is_approved,
            feedback=feedback,
            suggested_changes=suggested_changes,
            estimated_pages=estimated_pages
        )