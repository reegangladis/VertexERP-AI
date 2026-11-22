"""Unit tests for Production Infrastructure definitions, Compose topologies, and Dockerfiles."""

from pathlib import Path

import pytest

from scripts.validate_infra import (
    validate_docker_compose_files,
    validate_dockerfiles,
    validate_env_templates,
    validate_kubernetes_manifests,
    validate_nginx_configs,
)


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).parent.parent.parent.resolve()


def test_docker_compose_topologies(project_root: Path):
    """Verify all Docker Compose files are present and valid."""
    results = validate_docker_compose_files(project_root)
    assert len(results) >= 3
    for ok, msg in results:
        assert ok is True, f"Docker Compose validation failed: {msg}"


def test_dockerfiles_hardening(project_root: Path):
    """Verify multi-stage builds, non-root user, and healthcheck definitions."""
    results = validate_dockerfiles(project_root)
    assert len(results) >= 2
    for ok, msg in results:
        assert ok is True, f"Dockerfile validation failed: {msg}"


def test_nginx_reverse_proxy_configurations(project_root: Path):
    """Verify Nginx reverse proxy and frontend webserver configurations."""
    results = validate_nginx_configs(project_root)
    assert len(results) >= 3
    for ok, msg in results:
        assert ok is True, f"Nginx config validation failed: {msg}"


def test_environment_templates_and_secrets(project_root: Path):
    """Verify completeness and fail-closed security of .env templates."""
    results = validate_env_templates(project_root)
    assert len(results) >= 4
    for ok, msg in results:
        assert ok is True, f"Env template validation failed: {msg}"


def test_kubernetes_manifests_validity(project_root: Path):
    """Verify Kubernetes manifests parse and contain required API objects."""
    results = validate_kubernetes_manifests(project_root)
    assert len(results) >= 8
    for ok, msg in results:
        assert ok is True, f"Kubernetes manifest validation failed: {msg}"
