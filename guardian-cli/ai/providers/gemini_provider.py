"""
Gemini Provider Implementation
Google Gemini models via Google AI API
"""

import os
from typing import Optional, Dict, Any, List, Union

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from ai.providers.base_provider import BaseProvider


class GeminiProvider(BaseProvider):
    """Google Gemini API provider"""
    
    def __init__(self, config: Dict[str, Any], logger):
        super().__init__(config, logger)
        
        # Get Gemini-specific configuration
        ai_config = config.get("ai", {})
        gemini_config = ai_config.get("gemini", {})
        
        self.model_name = gemini_config.get("model", ai_config.get("model", "gemini-2.5-pro"))
        # Prefer config file over environment variable
        self.api_key = gemini_config.get("api_key") or os.environ.get("GOOGLE_API_KEY")
        self.temperature = ai_config.get("temperature", 0.2)
        
        self.backend = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Gemini backend"""
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError(
                "LangChain Google GenAI library not found. "
                "Install with: pip install langchain-google-genai"
            )
        
        if not self.api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY not found. "
                "Set environment variable or add to config. "
                "Get your API key from: https://aistudio.google.com/apikey"
            )
        
        try:
            self.backend = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=self.temperature,
                convert_system_message_to_human=True
            )
            self.logger.info(f"Initialized Gemini provider: {self.model_name}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini backend: {e}")
    
    def _format_context(self, context: Optional[List[Any]]) -> List[Union[HumanMessage, AIMessage]]:
        """Format context for LangChain"""
        if not context:
            return []
        
        messages = []
        for msg in context:
            # Handle LangChain message objects
            if hasattr(msg, "content"):
                messages.append(msg)
            # Handle dict format
            elif isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                else:
                    messages.append(AIMessage(content=content))
        
        return messages
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[list] = None
    ) -> str:
        """Generate response using Gemini"""
        await self._apply_rate_limit()
        
        try:
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            
            messages.extend(self._format_context(context))
            messages.append(HumanMessage(content=prompt))
            
            response = await self.backend.ainvoke(messages)
            return response.content
        except Exception as e:
            self.logger.error(f"Gemini generation failed: {e}")
            raise
    
    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[list] = None
    ) -> str:
        """Generate response synchronously"""
        self._apply_rate_limit_sync()
        
        try:
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            
            messages.extend(self._format_context(context))
            messages.append(HumanMessage(content=prompt))
            
            response = self.backend.invoke(messages)
            return response.content
        except Exception as e:
            self.logger.error(f"Gemini sync generation failed: {e}")
            raise
    
    def get_model_name(self) -> str:
        """Get current model name"""
        return self.model_name
    
    def is_available(self) -> bool:
        """Check if provider is available"""
        return LANGCHAIN_AVAILABLE and bool(self.api_key) and self.backend is not None
