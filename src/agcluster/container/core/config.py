"""Configuration settings for AgCluster"""

import os
from pydantic_settings import BaseSettings
from typing import Optional, List, Dict


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False

    # CORS Settings
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Provider Configuration
    container_provider: str = "docker"  # docker | fly_machines | cloudflare | vercel

    # Docker Settings
    docker_network: str = "agcluster-container_agcluster-network"  # Docker Compose creates network with project prefix
    agent_image: str = "agcluster/agent:latest"

    # Container Resource Limits (defaults when not specified in config)
    container_cpu_quota: int = 200000  # 2 CPUs
    container_memory_limit: str = "4g"
    container_storage_limit: str = "10g"

    # Agent Defaults
    default_system_prompt: str = "You are a helpful AI assistant with access to tools."
    default_allowed_tools: str = "Bash,Read,Write,Grep"

    # Container Cleanup
    inactive_container_timeout: int = 1800  # 30 minutes in seconds

    # Logging
    log_level: str = "info"

    # Fly Machines Provider Settings
    fly_api_token: Optional[str] = None
    fly_app_name: Optional[str] = None
    fly_region: str = "iad"  # Default: US East

    # Cloudflare Provider Settings
    cloudflare_api_token: Optional[str] = None
    cloudflare_account_id: Optional[str] = None
    cloudflare_namespace_id: Optional[str] = None

    # Vercel Provider Settings
    vercel_token: Optional[str] = None
    vercel_project_id: Optional[str] = None
    vercel_team_id: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow CONTAINER_ENV_* variables to be present without validation errors

    def get_container_env_vars(self) -> Dict[str, str]:
        """
        Extract environment variables prefixed with CONTAINER_ENV_ for injection into containers.

        The prefix CONTAINER_ENV_ will be removed from the variable name.
        For example, CONTAINER_ENV_HTTP_PROXY becomes HTTP_PROXY in the container.

        Variables are collected from two sources:
        1. Pydantic Settings extra fields (from .env file)
        2. OS environment variables (runtime)

        Returns:
            Dict[str, str]: Dictionary of environment variables to inject into containers
        """
        container_env = {}
        prefix_upper = "CONTAINER_ENV_"
        prefix_lower = "container_env_"

        # First, check Pydantic Settings extra fields (from .env file)
        # These are stored in __pydantic_extra__ when extra="allow"
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__:
            for key, value in self.__pydantic_extra__.items():
                # Pydantic converts to lowercase due to case_sensitive=False
                if key.lower().startswith(prefix_lower):
                    # Remove prefix and convert to uppercase for container
                    container_key = key[len(prefix_lower) :].upper()
                    container_env[container_key] = str(value)

        # Second, check OS environment variables (these take precedence)
        for key, value in os.environ.items():
            if key.startswith(prefix_upper):
                # Remove prefix and add to container env
                container_key = key[len(prefix_upper) :]
                container_env[container_key] = value

        return container_env


# Global settings instance
settings = Settings()
