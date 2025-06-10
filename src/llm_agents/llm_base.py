import openai
from typing import Optional
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Configuration for OpenAI model."""
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

class BaseAgent:
    """Base class for LLM agents."""
    
    def __init__(self, model_config: Optional[ModelConfig] = None):
        """
        Initialize the agent with model configuration.
        
        Args:
            model_config (Optional[ModelConfig]): Configuration for the OpenAI model
        """
        self.model_config = model_config or ModelConfig()
    
    def _create_prompt(self, template: str, **kwargs) -> str:
        """Create a prompt by filling in the template with kwargs."""
        return template.format(**kwargs)
    
    def _call_openai(self, prompt: str, system_content: str) -> str:
        """Make an OpenAI API call with the given prompt and system content."""
        params = {
            "model": self.model_config.model,
            "temperature": self.model_config.temperature,
            "top_p": self.model_config.top_p,
            "frequency_penalty": self.model_config.frequency_penalty,
            "presence_penalty": self.model_config.presence_penalty,
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ]
        }
        
        if self.model_config.max_tokens:
            params["max_tokens"] = self.model_config.max_tokens
            
        response = openai.chat.completions.create(**params)
        return response.choices[0].message.content