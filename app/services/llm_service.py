"""
LLM Service
Handles communication with various LLM providers for content generation.
"""

import asyncio
import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from app.logger import logger


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using the LLM provider."""


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed. Run: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")

        self.model = model
        self.client = openai.AsyncOpenAI(api_key=self.api_key)

    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using OpenAI GPT."""
        try:
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 2000)

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume writer and career coach. Always respond with valid JSON when requested.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            content = response.choices[0].message.content
            logger.info(f"Generated content using OpenAI {self.model}")
            return content

        except Exception as e:
            logger.error(f"Error generating content with OpenAI: {e}")
            raise


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"
    ):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic package not installed. Run: pip install anthropic"
            )

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")

        self.model = model
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)

    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using Anthropic Claude."""
        try:
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 2000)

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system="You are an expert resume writer and career coach. Always respond with valid JSON when requested.",
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text
            logger.info(f"Generated content using Anthropic {self.model}")
            return content

        except Exception as e:
            logger.error(f"Error generating content with Anthropic: {e}")
            raise


class MockProvider(LLMProvider):
    """Mock provider for testing and development."""

    def __init__(self):
        pass

    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate mock content for testing."""
        # Wait a bit to simulate API call
        await asyncio.sleep(0.1)

        # Return mock JSON responses based on prompt content
        if "professional summary" in prompt.lower():
            return self._mock_summary_response()
        elif "achievement" in prompt.lower():
            return self._mock_achievements_response()
        elif "optimize" in prompt.lower():
            return self._mock_optimization_response()
        else:
            return '{"message": "Mock response generated successfully"}'

    def _mock_summary_response(self) -> str:
        """Mock professional summary response."""
        return json.dumps(
            {
                "summaries": [
                    {
                        "version": "technical_focus",
                        "summary": "Results-driven Software Engineer with 5+ years developing scalable web applications using Python, React, and AWS. Specialized in microservices architecture and API development for SaaS platforms, with proven track record of improving system performance by 40% and reducing deployment time by 60%. Strong background in DevOps practices and agile methodologies, passionate about building robust, user-centric solutions.",
                        "word_count": 67,
                        "key_strengths": [
                            "technical expertise",
                            "performance optimization",
                            "modern technologies",
                        ],
                        "target_roles": [
                            "Senior Software Engineer",
                            "Full Stack Developer",
                            "Technical Lead",
                        ],
                    }
                ],
                "customization_notes": ["Mock response - customize for actual use"],
                "ats_optimization": {
                    "primary_keywords": ["software engineer", "python", "react", "aws"],
                    "secondary_keywords": ["microservices", "api", "devops"],
                    "keyword_density": "8-12%",
                },
            }
        )

    def _mock_achievements_response(self) -> str:
        """Mock achievements response."""
        return json.dumps(
            {
                "achievements": [
                    {
                        "bullet_point": "Led development of microservices architecture serving 1M+ users, reducing API response time by 40% and improving system reliability to 99.9% uptime",
                        "category": "technical_leadership",
                        "impact_type": "performance_improvement",
                        "quantified_metrics": [
                            "1M+ users",
                            "40% response time reduction",
                            "99.9% uptime",
                        ],
                        "keywords_used": [
                            "microservices",
                            "API",
                            "architecture",
                            "scalability",
                        ],
                    },
                    {
                        "bullet_point": "Implemented CI/CD pipeline reducing deployment time from 4 hours to 15 minutes while maintaining zero-downtime deployments",
                        "category": "process_improvement",
                        "impact_type": "efficiency_gain",
                        "quantified_metrics": [
                            "4 hours to 15 minutes",
                            "zero-downtime",
                        ],
                        "keywords_used": ["CI/CD", "deployment", "automation"],
                    },
                ],
                "suggested_variations": [],
                "missing_quantification_opportunities": [
                    "Consider adding team size metrics"
                ],
            }
        )

    def _mock_optimization_response(self) -> str:
        """Mock optimization response."""
        return json.dumps(
            {
                "optimized_summary": "Enhanced summary optimized for target job...",
                "optimized_experience": [],
                "optimized_skills": [],
                "optimized_projects": [],
                "keyword_analysis": {
                    "keywords_added": ["kubernetes", "docker"],
                    "keywords_emphasized": ["python", "aws"],
                    "missing_keywords": ["terraform", "monitoring"],
                    "ats_score_prediction": 85,
                },
                "optimization_notes": ["Mock optimization applied"],
            }
        )


class LLMService:
    """Main LLM service that manages providers and handles requests."""

    def __init__(self, provider_name: str = "mock", **provider_kwargs):
        self.provider = self._create_provider(provider_name, **provider_kwargs)
        self.provider_name = provider_name

    def _create_provider(self, provider_name: str, **kwargs) -> LLMProvider:
        """Create the specified LLM provider."""
        provider_name = provider_name.lower()

        if provider_name == "openai":
            if not OPENAI_AVAILABLE:
                logger.warning("OpenAI not available, falling back to mock provider")
                return MockProvider()
            return OpenAIProvider(**kwargs)

        elif provider_name == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                logger.warning("Anthropic not available, falling back to mock provider")
                return MockProvider()
            return AnthropicProvider(**kwargs)

        elif provider_name == "mock":
            return MockProvider()

        else:
            logger.warning(f"Unknown provider '{provider_name}', falling back to mock")
            return MockProvider()

    async def generate_content(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000, **kwargs
    ) -> str:
        """Generate content using the configured provider."""
        try:
            return await self.provider.generate_content(
                prompt=prompt, temperature=temperature, max_tokens=max_tokens, **kwargs
            )
        except Exception as e:
            logger.error(f"Error generating content: {e}")

            # Fall back to mock provider if the main provider fails
            if not isinstance(self.provider, MockProvider):
                logger.warning("Falling back to mock provider")
                mock_provider = MockProvider()
                return await mock_provider.generate_content(prompt, **kwargs)
            else:
                raise

    async def generate_json_content(
        self, prompt: str, expected_schema: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Generate content and parse as JSON."""
        try:
            content = await self.generate_content(prompt, **kwargs)

            # Try to parse as JSON
            try:
                result = json.loads(content)

                # Optionally validate against schema
                if expected_schema:
                    # Basic schema validation could be added here
                    pass

                return result

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                # Try to extract JSON from the response
                return self._extract_json_from_text(content)

        except Exception as e:
            logger.error(f"Error generating JSON content: {e}")
            raise

    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text that might contain other content."""
        try:
            # Find JSON-like content between braces
            start_idx = text.find("{")
            end_idx = text.rfind("}")

            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_text = text[start_idx : end_idx + 1]
                return json.loads(json_text)
            else:
                # Return fallback structure
                return {
                    "error": "Could not extract JSON from response",
                    "raw_text": text,
                }

        except Exception as e:
            logger.error(f"Error extracting JSON from text: {e}")
            return {"error": "JSON extraction failed", "raw_text": text}

    def get_provider_info(self) -> Dict[str, str]:
        """Get information about the current provider."""
        return {
            "provider": self.provider_name,
            "model": getattr(self.provider, "model", "unknown"),
            "available": str(self.provider is not None),
        }


# Factory function for easy service creation
def create_llm_service(provider: str = None, **kwargs) -> LLMService:
    """Create an LLM service with the best available provider."""

    # Try to determine the best provider if not specified
    if provider is None:
        if os.getenv("OPENAI_API_KEY") and OPENAI_AVAILABLE:
            provider = "openai"
        elif os.getenv("ANTHROPIC_API_KEY") and ANTHROPIC_AVAILABLE:
            provider = "anthropic"
        else:
            provider = "mock"
            logger.warning("No API keys found, using mock provider for development")

    logger.info(f"Creating LLM service with {provider} provider")
    return LLMService(provider, **kwargs)
