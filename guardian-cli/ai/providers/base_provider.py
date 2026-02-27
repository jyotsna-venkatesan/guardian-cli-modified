"""
Base Provider Interface for AI Models
Defines the common interface that all AI providers must implement
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import time
import asyncio


class BaseProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, config: Dict[str, Any], logger):
        self.config = config
        self.logger = logger
        
        # Rate limiting
        ai_config = config.get("ai", {})
        self.rate_limit = ai_config.get("rate_limit", 60)
        self._min_request_interval = 60.0 / self.rate_limit if self.rate_limit > 0 else 0
        self._last_request_time = 0.0
    
    @abstractmethod
    def _initialize(self):
        """Initialize the provider backend"""
        pass
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[list] = None
    ) -> str:
        """Generate response asynchronously"""
        pass
    
    @abstractmethod
    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[list] = None
    ) -> str:
        """Generate response synchronously"""
        pass
    
    async def generate_with_reasoning(
        self,
        prompt: str,
        system_prompt: str,
        task_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate response with reasoning steps
        Default implementation - can be overridden by providers
        """
        full_prompt = f"{prompt}\n\nPlease think through this step-by-step and provide your reasoning."
        
        if task_context:
            full_prompt = f"Context: {task_context}\n\n{full_prompt}"
        
        response = await self.generate(full_prompt, system_prompt)
        
        return {
            "response": response,
            "reasoning": "Provider does not support explicit reasoning extraction"
        }
    
    async def _apply_rate_limit(self):
        """Apply rate limiting between API calls"""
        if self._min_request_interval > 0:
            elapsed = time.time() - self._last_request_time
            if elapsed < self._min_request_interval:
                wait_time = self._min_request_interval - elapsed
                await asyncio.sleep(wait_time)
        self._last_request_time = time.time()
    
    def _apply_rate_limit_sync(self):
        """Apply rate limiting between API calls (synchronous)"""
        if self._min_request_interval > 0:
            elapsed = time.time() - self._last_request_time
            if elapsed < self._min_request_interval:
                wait_time = self._min_request_interval - elapsed
                time.sleep(wait_time)
        self._last_request_time = time.time()
