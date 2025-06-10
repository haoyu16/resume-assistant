import openai
from dotenv import load_dotenv
import os
from typing import Optional, Tuple

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

from .llm_base import BaseAgent, ModelConfig

class ContentPolisher(BaseAgent):
    """Agent responsible for polishing and optimizing content."""
    
    _SYSTEM_CONTENT = """You are a professional resume writer specializing in content optimization. 
    Your goal is to make the content impactful, relevant, and professional."""
    
    _SUMMARY_FOCUS_POINTS = """
    1. Crafting a compelling narrative
    2. Highlighting key professional identity
    3. Emphasizing unique value proposition
    4. Maintaining concise and impactful language
    5. Ensuring relevance to career goals"""
    
    _SKILLS_FOCUS_POINTS = """
    1. Using industry-standard terminology
    2. Organizing skills by relevance/importance
    3. Including both technical and soft skills
    4. Using clear and consistent formatting
    5. Avoiding redundancy and outdated skills"""
    
    _EXPERIENCE_FOCUS_POINTS = """
    1. Using strong action verbs
    2. Quantifying achievements where possible
    3. Making each point impactful
    4. Highlighting relevant responsibilities
    5. Being concise and specific"""
    
    _JOB_SPECIFIC_SUMMARY_POINTS = """
    1. Aligning with job requirements
    2. Emphasizing relevant expertise
    3. Using industry-specific language
    4. Highlighting key qualifications
    5. Maintaining professional tone"""
    
    _JOB_SPECIFIC_SKILLS_POINTS = """
    1. Prioritizing required skills
    2. Including job-specific keywords
    3. Matching terminology from posting
    4. Emphasizing relevant technologies
    5. Balancing technical and soft skills"""
    
    _JOB_SPECIFIC_EXPERIENCE_POINTS = """
    1. Using strong action verbs
    2. Quantifying achievements where possible
    3. Highlighting relevant accomplishments
    4. Using job-specific terminology
    5. Being concise and impactful"""
    
    def __init__(self, model_config: Optional[ModelConfig] = None):
        """Initialize with optional model configuration."""
        # Use higher temperature for more creative optimization
        default_config = ModelConfig(temperature=0.8)
        super().__init__(model_config or default_config)
    
    def _get_focus_points(self, content_type: str, has_job_desc: bool) -> str:
        """Get appropriate focus points based on content type and context."""
        if has_job_desc:
            if content_type == "summary":
                return self._JOB_SPECIFIC_SUMMARY_POINTS
            elif content_type == "skills":
                return self._JOB_SPECIFIC_SKILLS_POINTS
            else:  # experience or projects
                return self._JOB_SPECIFIC_EXPERIENCE_POINTS
        else:
            if content_type == "summary":
                return self._SUMMARY_FOCUS_POINTS
            elif content_type == "skills":
                return self._SKILLS_FOCUS_POINTS
            else:  # experience or projects
                return self._EXPERIENCE_FOCUS_POINTS
    
    def _get_prompt_template(self, has_job_desc: bool, has_feedback: bool) -> str:
        """Get the appropriate prompt template based on available inputs."""
        base_template = """As a professional resume content optimizer, enhance the following {content_type}{context}.
        
        {job_desc_section}
        Content to Optimize:
        {content}
        {feedback_section}
        Focus on:{focus_points}"""
        
        context = ""
        if has_feedback:
            context = " based on the critic's feedback"
            if has_job_desc:
                context += " while maintaining alignment with job requirements"
                
        return base_template
    
    def polish_content(self, content: str, content_type: str = "experience", job_description: Optional[str] = None, critic_feedback: Optional[str] = None) -> str:
        """
        Polish the content based on job description and critic's feedback if provided.
        
        Args:
            content (str): Content to optimize
            content_type (str): Type of content ("summary", "skills", "experience", or "projects")
            job_description (Optional[str]): Job requirements
            critic_feedback (Optional[str]): Previous feedback from critic
        """
        template = self._get_prompt_template(bool(job_description), bool(critic_feedback))
        focus_points = self._get_focus_points(content_type, bool(job_description))
        
        # Prepare sections
        job_desc_section = f"Job Requirements:\n{job_description}\n\n" if job_description else ""
        feedback_section = f"\nCritic's Feedback:\n{critic_feedback}\n" if critic_feedback else ""
        
        prompt = self._create_prompt(
            template,
            content_type=content_type,
            context="" if not (job_description or critic_feedback) else " based on the provided context",
            job_desc_section=job_desc_section,
            content=content,
            feedback_section=feedback_section,
            focus_points=focus_points
        )
        
        return self._call_openai(prompt, self._SYSTEM_CONTENT)

class ContentCritic(BaseAgent):
    """Agent responsible for critiquing and suggesting improvements."""
    
    _SYSTEM_CONTENT = """You are a highly critical resume reviewer. 
    Your goal is to ensure the content is perfect for the target job and meets high professional standards."""
    
    _SUMMARY_EVALUATION_POINTS = """
    1. Clarity of professional identity
    2. Impact and engagement
    3. Relevance to career goals
    4. Professional tone
    5. Conciseness and focus"""
    
    _SKILLS_EVALUATION_POINTS = """
    1. Relevance and currency of skills
    2. Organization and clarity
    3. Technical accuracy
    4. Breadth and depth balance
    5. Format consistency"""
    
    _EXPERIENCE_EVALUATION_POINTS = """
    1. Impact of achievements
    2. Use of action verbs
    3. Quantification of results
    4. Clarity and conciseness
    5. Professional tone"""
    
    _JOB_SPECIFIC_SUMMARY_POINTS = """
    1. Alignment with job requirements
    2. Emphasis on relevant expertise
    3. Use of industry terminology
    4. Professional tone
    5. Overall impact and relevance"""
    
    _JOB_SPECIFIC_SKILLS_POINTS = """
    1. Coverage of required skills
    2. Use of job-specific keywords
    3. Relevance to position
    4. Technical accuracy
    5. Organization and clarity"""
    
    _JOB_SPECIFIC_EXPERIENCE_POINTS = """
    1. Relevance to job requirements
    2. Impact of achievements
    3. Use of industry terminology
    4. Quantification of results
    5. Overall effectiveness"""
    
    def __init__(self, model_config: Optional[ModelConfig] = None):
        """Initialize with optional model configuration."""
        # Use lower temperature for more consistent criticism
        default_config = ModelConfig(temperature=0.3)
        super().__init__(model_config or default_config)
    
    def _get_evaluation_points(self, content_type: str, has_job_desc: bool) -> str:
        """Get appropriate evaluation points based on content type and context."""
        if has_job_desc:
            if content_type == "summary":
                return self._JOB_SPECIFIC_SUMMARY_POINTS
            elif content_type == "skills":
                return self._JOB_SPECIFIC_SKILLS_POINTS
            else:  # experience or projects
                return self._JOB_SPECIFIC_EXPERIENCE_POINTS
        else:
            if content_type == "summary":
                return self._SUMMARY_EVALUATION_POINTS
            elif content_type == "skills":
                return self._SKILLS_EVALUATION_POINTS
            else:  # experience or projects
                return self._EXPERIENCE_EVALUATION_POINTS
    
    def evaluate_content(self, original: str, optimized: str, content_type: str = "experience", job_description: Optional[str] = None) -> Tuple[bool, str]:
        """
        Evaluate the optimized content and provide feedback.
        
        Args:
            original (str): Original content
            optimized (str): Optimized content
            content_type (str): Type of content ("summary", "skills", "experience", or "projects")
            job_description (Optional[str]): Job description for context
            
        Returns:
            Tuple[bool, str]: (is_satisfied, feedback)
        """
        template = """As a critical resume reviewer, evaluate the optimized {content_type} against the original{job_context}.
        
        {job_desc_section}
        Original Content:
        {original}
        
        Optimized Content:
        {optimized}
        
        Evaluate based on:{evaluation_points}
        
        Provide specific, actionable feedback for improvement.
        Be clear about what needs to be changed and how.
        End your response with either SATISFIED or NEEDS_IMPROVEMENT on a new line."""
        
        evaluation_points = self._get_evaluation_points(content_type, bool(job_description))
        
        prompt = self._create_prompt(
            template,
            content_type=content_type,
            job_context=" and job requirements" if job_description else "",
            job_desc_section=f"Job Requirements:\n{job_description}\n\n" if job_description else "",
            original=original,
            optimized=optimized,
            evaluation_points=evaluation_points
        )
        
        feedback = self._call_openai(prompt, self._SYSTEM_CONTENT)
        is_satisfied = "SATISFIED" in feedback.split('\n')[-1]
        return is_satisfied, feedback

class ContentOptimizer:
    """Coordinates the optimization process between polisher and critic."""
    
    def __init__(
        self,
        max_rounds: int = 3,
        polisher_config: Optional[ModelConfig] = None,
        critic_config: Optional[ModelConfig] = None
    ):
        """
        Initialize the optimizer with configurable parameters.
        
        Args:
            max_rounds (int): Maximum number of optimization rounds
            polisher_config (Optional[ModelConfig]): Configuration for the polisher model
            critic_config (Optional[ModelConfig]): Configuration for the critic model
        """
        self.polisher = ContentPolisher(polisher_config)
        self.critic = ContentCritic(critic_config)
        self.max_rounds = max_rounds
    
    def optimize_content(self, content: str, content_type: str = "experience", job_description: Optional[str] = None) -> str:
        """
        Optimize content using a polisher and critic agent system.
        
        Args:
            content (str): The content to optimize
            content_type (str): Type of content ("summary", "skills", "experience", or "projects")
            job_description (Optional[str]): Job description to tailor content to
            
        Returns:
            str: Optimized content
        """
        current_round = 0
        optimized_content = content
        previous_feedback = None
        
        while current_round < self.max_rounds:
            # Polish the content, incorporating previous feedback if available
            optimized_content = self.polisher.polish_content(
                content if current_round == 0 else optimized_content,
                content_type=content_type,
                job_description=job_description,
                critic_feedback=previous_feedback
            )
            
            # Get critic's feedback
            is_satisfied, feedback = self.critic.evaluate_content(
                content,
                optimized_content,
                content_type=content_type,
                job_description=job_description
            )
            
            if is_satisfied:
                break
                
            previous_feedback = feedback
            current_round += 1
        
        return optimized_content

# Module-level function for backward compatibility
def optimize_content(
    content: str,
    content_type: str = "experience",
    job_description: Optional[str] = None,
    polisher_config: Optional[ModelConfig] = None,
    critic_config: Optional[ModelConfig] = None,
    max_rounds: int = 3
) -> str:
    """
    Backward-compatible function that uses ResumeOptimizer.
    
    Args:
        content (str): Content to optimize
        content_type (str): Type of content ("summary", "skills", "experience", or "projects")
        job_description (Optional[str]): Job description to tailor content to
        polisher_config (Optional[ModelConfig]): Configuration for the polisher model
        critic_config (Optional[ModelConfig]): Configuration for the critic model
        max_rounds (int): Maximum number of optimization rounds
        
    Returns:
        str: Optimized content
    """
    optimizer = ContentOptimizer(max_rounds, polisher_config, critic_config)
    return optimizer.optimize_content(content, content_type, job_description) 