"""Tests for container environment variables configuration"""

import os
import pytest
from agcluster.container.core.config import Settings


@pytest.fixture
def clean_env():
    """Clean up CONTAINER_ENV_* variables before and after test"""
    original_env = os.environ.copy()
    # Remove any existing CONTAINER_ENV_* variables
    for key in list(os.environ.keys()):
        if key.startswith("CONTAINER_ENV_"):
            del os.environ[key]
    yield
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


def test_get_container_env_vars_from_os_environ(clean_env):
    """Test reading CONTAINER_ENV_* from actual OS environment"""
    # Set environment variables
    os.environ["CONTAINER_ENV_HTTP_PROXY"] = "http://proxy.example.com:8080"
    os.environ["CONTAINER_ENV_TEST_VAR"] = "test_value"

    # Create settings instance
    settings = Settings()

    # Get container env vars
    container_env = settings.get_container_env_vars()

    # Verify
    assert "HTTP_PROXY" in container_env
    assert container_env["HTTP_PROXY"] == "http://proxy.example.com:8080"
    assert "TEST_VAR" in container_env
    assert container_env["TEST_VAR"] == "test_value"


def test_get_container_env_vars_from_pydantic_extra(clean_env, tmp_path):
    """Test reading CONTAINER_ENV_* from .env file via Pydantic Settings"""
    # Create a temporary .env file
    env_file = tmp_path / ".env"
    env_file.write_text(
        "CONTAINER_ENV_HTTP_PROXY=http://proxy.example.com:8080\n"
        "CONTAINER_ENV_HTTPS_PROXY=https://proxy.example.com:8443\n"
        "CONTAINER_ENV_CUSTOM_VAR=custom_value\n"
    )

    # Create settings instance with custom env_file
    settings = Settings(_env_file=str(env_file))

    # Get container env vars
    container_env = settings.get_container_env_vars()

    # Verify - these should be found even though they're not in os.environ
    assert "HTTP_PROXY" in container_env
    assert container_env["HTTP_PROXY"] == "http://proxy.example.com:8080"
    assert "HTTPS_PROXY" in container_env
    assert container_env["HTTPS_PROXY"] == "https://proxy.example.com:8443"
    assert "CUSTOM_VAR" in container_env
    assert container_env["CUSTOM_VAR"] == "custom_value"


def test_get_container_env_vars_mixed_sources(clean_env, tmp_path):
    """Test reading CONTAINER_ENV_* from both .env file and OS environment"""
    # Set OS environment variable
    os.environ["CONTAINER_ENV_OS_VAR"] = "from_os"

    # Create a temporary .env file
    env_file = tmp_path / ".env"
    env_file.write_text("CONTAINER_ENV_FILE_VAR=from_file\n")

    # Create settings instance
    settings = Settings(_env_file=str(env_file))

    # Get container env vars
    container_env = settings.get_container_env_vars()

    # Verify both sources
    assert "OS_VAR" in container_env
    assert container_env["OS_VAR"] == "from_os"
    assert "FILE_VAR" in container_env
    assert container_env["FILE_VAR"] == "from_file"


def test_get_container_env_vars_empty(clean_env, tmp_path):
    """Test get_container_env_vars returns empty dict when no variables"""
    # Use empty .env file to avoid picking up project's .env
    env_file = tmp_path / ".env"
    env_file.write_text("")

    settings = Settings(_env_file=str(env_file))
    container_env = settings.get_container_env_vars()
    assert container_env == {}


def test_get_container_env_vars_prefix_removal(clean_env):
    """Test that CONTAINER_ENV_ prefix is correctly removed"""
    os.environ["CONTAINER_ENV_MY_VARIABLE"] = "value"
    os.environ["CONTAINER_ENV_ANOTHER_ONE"] = "another"

    settings = Settings()
    container_env = settings.get_container_env_vars()

    # Check prefix is removed
    assert "MY_VARIABLE" in container_env
    assert "ANOTHER_ONE" in container_env
    # Original keys should not exist
    assert "CONTAINER_ENV_MY_VARIABLE" not in container_env
    assert "CONTAINER_ENV_ANOTHER_ONE" not in container_env
