"""
config.py - Typed application configuration loader.

This module loads runtime configuration from environment variables (and an optional .env file),
validates required values, and exposes a single, typed Settings object for the application to use.

Notes:
- Provide a single source of truth (Settings) to simplify imports across the codebase.
- Fail fast with ConfigError for missing/invalid configuration so callers can map to exit codes.
- Compute filesystem paths relative to the package to avoid leaking assumptions to callers.

"""

from dataclasses import dataclass
import os
from typing import List, Tuple, Optional
from dotenv import load_dotenv
from exceptions import ConfigError


load_dotenv()

@dataclass(frozen=True)
class Settings:
    """
    Immutable container for application settings.

    Attributes:
        api_base: Base URL for the ILLiad API.
        api_key: API key used to authenticate to the ILLiad API.
        pickup_locations: Allowed pickup locations parsed from PICKUP_LOCATIONS.
        data_files_dir: Absolute path to the data_files directory.
        results_dir: Absolute path to the results directory (test/normal mode).
        test_results_dir: Absolute path to the test results directory (dev mode).
    """

    api_base: str
    api_key: str
    pickup_locations: List[str]
    data_files_dir: str
    results_dir: str
    test_results_dir: str

def _compute_paths() -> Tuple[str, str, str]:
    """
    Compute canonical filesystem paths used by the application.

    Returns:
        Tuple of (data_files_dir, results_dir, test_results_dir), all absolute paths.
    """

    package_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_files_dir = os.path.join(package_root, "data_files")
    results_dir = os.path.join(data_files_dir, "results")
    test_results_dir = os.path.join(package_root, "test", "data", "actual")
    return (data_files_dir, results_dir, test_results_dir)

def _load_settings(env_path: Optional[str] = None) -> Settings:
    """
    Read environment variables, validate them, and return a Settings instance.

    Args:
        env_path: Optional path to a .env file to load (if provided, load_dotenv is called on it).

    Raises:
        ConfigError: If any required configuration is missing or malformed.

    Notes:
        - PICKUP_LOCATIONS is parsed as a comma-separated list and trimmed.
        - This function raises ConfigError so callers can map the error
          to a specific exit code and user-facing message.
    """
    # Allow explicit .env path for testing; otherwise rely on previously loaded env.
    if env_path:
        load_dotenv(env_path)

    api_base = (os.getenv("API_BASE") or "").strip()
    api_key = (os.getenv("API_KEY") or "").strip()
    pickup_locations_raw = os.getenv("PICKUP_LOCATIONS", "")
    
    
    # Validate core values early to fail fast with a clear domain error.
    if not api_base:
        raise ConfigError("API_BASE not set; add to .env")
    if not api_key:
        raise ConfigError("API_KEY not set; add to .env")
    
    # Normalize pickup locations into a list, ignoring empty items.=
    pickup_locations = [p.strip() for p in pickup_locations_raw.split(",") if p.strip()]
    if not pickup_locations:
        raise ConfigError("PICKUP_LOCATIONS not set or empty; add to .env")
    
    data_files_dir, results_dir, test_results_dir = _compute_paths()
    
    return Settings(
        api_base=api_base,
        api_key=api_key,
        pickup_locations=pickup_locations,
        data_files_dir=os.path.abspath(data_files_dir),
        results_dir=os.path.abspath(results_dir),
        test_results_dir=os.path.abspath(test_results_dir),
    )


# Single source of truth for application configuration.
# Other modules should import `settings` and reference attributes (e.g., settings.api_key).
settings: Settings = _load_settings()