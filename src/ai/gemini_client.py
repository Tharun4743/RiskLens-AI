"""Gemini API Client integration using official google-genai SDK.
Handles API key discovery, timeouts, structured output parsing, and graceful degradation.
"""
import os
import logging
from typing import Optional, Any
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger("risklens.ai")


class GeminiUnavailableException(Exception):
    """Raised when Gemini API is unavailable or unconfigured."""
    pass


class GeminiClient:
    """Client for Google Gemini API."""

    def __init__(self, api_key: Optional[str] = None):
        if api_key is not None:
            self.api_key = api_key.strip()
        else:
            self.api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        self.model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not configured. AI explanation features will use deterministic fallback.")
            self._client = None
            return

        try:
            from google import genai
            from google.genai import types
            self._client = genai.Client(
                api_key=self.api_key,
                http_options=types.HttpOptions(timeout=15000)
            )
            logger.info("Gemini client initialized successfully with model %s", self.model_name)
        except Exception as e:
            logger.warning("Failed to initialize Gemini Client: %s", str(e))
            self._client = None

    def is_available(self) -> bool:
        """Return True if Gemini is initialized and has an API key."""
        return self._client is not None and bool(self.api_key)

    def generate_explanation(
        self,
        system_instruction: str,
        prompt: str,
        response_schema: Any = None
    ) -> Optional[str]:
        """
        Calls Gemini to generate structured investigation explanation.
        Returns raw JSON string response or None if failed.
        """
        if not self.is_available():
            raise GeminiUnavailableException("GEMINI_API_KEY missing or Gemini client uninitialized.")

        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
                response_mime_type="application/json",
                response_schema=response_schema
            )

            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            if response and response.text:
                return response.text
            return None

        except Exception as e:
            logger.warning("Gemini generation failed: %s", str(e))
            raise GeminiUnavailableException(f"Gemini API error: {str(e)}")

    def answer_investigation_question(
        self,
        system_instruction: str,
        prompt: str
    ) -> str:
        """Answers analyst investigation queries grounded in evidence."""
        if not self.is_available():
            raise GeminiUnavailableException("Gemini API is unavailable.")

        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3
            )

            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            return response.text if response and response.text else "Unable to generate answer."

        except Exception as e:
            logger.warning("Gemini query failed: %s", str(e))
            raise GeminiUnavailableException(f"Gemini query failed: {str(e)}")
