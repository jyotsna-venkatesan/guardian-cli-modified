"""
AI Client for Guardian
Generic client that delegates to specific providers (Gemini, OpenAI, Claude, OpenRouter)
"""

from typing import Optional, Dict, Any
from ai.providers import get_provider
from utils.logger import get_logger


class AIClient:
    """
    Unified AI client that works with multiple providers
    Delegates all operations to the configured provider
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize AI client with specified provider
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = get_logger(config)
        
        # Load the appropriate provider based on config
        self.provider = get_provider(config)
        
        # Expose provider's model name
        self.model_name = self.provider.get_model_name()
        self.logger.info(f"AIClient initialized with {self.provider.__class__.__name__}: {self.model_name}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[list] = None
    ) -> str:
        """
        Generate AI response asynchronously
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instruction
            context: Optional conversation history
            
        Returns:
            Generated response text
        """
        return await self.provider.generate(prompt, system_prompt, context)
    
    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[list] = None
    ) -> str:
        """
        Generate AI response synchronously
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instruction
            context: Optional conversation history
            
        Returns:
            Generated response text
        """
        return self.provider.generate_sync(prompt, system_prompt, context)
    
    async def generate_with_reasoning(
        self,
        prompt: str,
        system_prompt: str,
        task_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate response with reasoning steps
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            task_context: Optional task context
            
        Returns:
            Dictionary with response and reasoning
        """
        return await self.provider.generate_with_reasoning(prompt, system_prompt, task_context)
    
    def get_model_name(self) -> str:
        """Get the current model name"""
        return self.model_name
    
    def is_available(self) -> bool:
        """Check if the provider is properly configured"""
        return self.provider.is_available()


# Backward compatibility alias
GeminiClient = AIClient
