"""Supabase Client integration for RiskLens AI.
Provides direct access to Supabase hosted PostgreSQL backend and authentication.
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

logger = logging.getLogger("risklens.supabase")

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """Return an initialized Supabase Client if credentials are configured."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    supabase_url = os.environ.get("SUPABASE_URL", "").strip()
    supabase_key = os.environ.get("SUPABASE_SECRET_KEY", "") or os.environ.get("SUPABASE_PUBLISHABLE_KEY", "").strip()

    if not supabase_url or not supabase_key:
        logger.debug("Supabase credentials not fully configured; operating in direct database mode.")
        return None

    try:
        _supabase_client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully for %s", supabase_url)
        return _supabase_client
    except Exception as exc:
        logger.warning("Failed to initialize Supabase client: %s", exc)
        return None
