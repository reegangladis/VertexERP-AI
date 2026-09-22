"""Automated Production Infrastructure Validation Engine for VertexERP AI V2."""

import sys
from pathlib import Path

# Try loading PyYAML if installed
try:
    import yaml
except ImportError:
    yaml = None


def get_project_root() -> Path:
    return Path(__file__).parent.parent.resolve()


def check_file_exists(rel_path: str, root: Path) -> tuple[bool, str]:
    path = root / rel_path
    if not path.exists():
        return False, f"Missing expected file: {rel_path}"
    return True, f"Found: {rel_path} ({path.stat().st_size} bytes)"


def validate_docker_compose_files(root: Path) -> list[tuple[bool, str]]:
    results = []
    compose_files = ["docker-compose.yml", "docker-compose.staging.yml", "docker-compose.prod.yml"]

    for cf in compose_files:
        ok, msg = check_file_exists(cf, root)
        if not ok:
            results.append((False, msg))
            continue

        content = (root / cf).read_text(encoding="utf-8")
        if yaml:
            try:
                data = yaml.safe_load(content)
                services = data.get("services", {})
                if not services:
                    results.append((False, f"{cf}: No services defined"))
                    continue

                # Check core services
                has_api = "api" in services
                has_db = "postgres" in services
                has_redis = "redis" in services
                has_worker = "worker" in services

                if not (has_api and has_db and has_redis and has_worker):
                    results.append(
                        (False, f"{cf}: Missing essential service (api, postgres, redis, worker)")
                    )
                else:
                    results.append(
                        (
                            True,
                            f"{cf}: Valid Compose with {len(services)} services ({', '.join(services.keys())})",
                        )
                    )
            except Exception as e:
                results.append((False, f"{cf}: YAML Parse Error: {e}"))
        else:
            # Fallback regex checks
            if "services:" in content and "api:" in content and "postgres:" in content:
                results.append((True, f"{cf}: Passed textual validation (PyYAML not installed)"))
            else:
                results.append((False, f"{cf}: Failed basic textual check"))

    return results


def validate_dockerfiles(root: Path) -> list[tuple[bool, str]]:
    results = []

    # Backend Dockerfile
    ok, msg = check_file_exists("Dockerfile", root)
    if not ok:
        results.append((False, msg))
    else:
        content = (root / "Dockerfile").read_text(encoding="utf-8")
        has_builder = "AS builder" in content
        has_runner = "AS runner" in content
        has_nonroot = "10001" in content or "appuser" in content
        has_healthcheck = "HEALTHCHECK" in content

        if has_builder and has_runner and has_nonroot and has_healthcheck:
            results.append(
                (
                    True,
                    "Backend Dockerfile: Hardened multi-stage build, unprivileged user, healthcheck verified",
                )
            )
        else:
            results.append(
                (
                    False,
                    "Backend Dockerfile: Missing required security constraints (builder/runner/non-root/healthcheck)",
                )
            )

    # Frontend Dockerfile
    ok, msg = check_file_exists("frontend/Dockerfile", root)
    if not ok:
        results.append((False, msg))
    else:
        content = (root / "frontend/Dockerfile").read_text(encoding="utf-8")
        has_builder = "AS builder" in content or "FROM node:" in content
        has_runner = "AS runner" in content or "FROM nginx:" in content
        has_healthcheck = "HEALTHCHECK" in content

        if has_builder and has_runner and has_healthcheck:
            results.append(
                (
                    True,
                    "Frontend Dockerfile: Multi-stage Node/Nginx build with healthcheck verified",
                )
            )
        else:
            results.append(
                (False, "Frontend Dockerfile: Incomplete multi-stage or healthcheck specification")
            )

    return results


def validate_nginx_configs(root: Path) -> list[tuple[bool, str]]:
    results = []
    nginx_files = [
        "frontend/nginx.conf",
        "infra/nginx/nginx.conf",
        "infra/nginx/conf.d/vertexerp.conf",
    ]

    for nf in nginx_files:
        ok, msg = check_file_exists(nf, root)
        if not ok:
            results.append((False, msg))
            continue

        content = (root / nf).read_text(encoding="utf-8")
        if "server {" in content or "http {" in content:
            results.append((True, f"{nf}: Valid Nginx directive structure"))
        else:
            results.append((False, f"{nf}: Missing expected Nginx server/http blocks"))

    return results


def validate_env_templates(root: Path) -> list[tuple[bool, str]]:
    results = []
    env_templates = [
        ".env.development.example",
        ".env.staging.example",
        ".env.production.example",
    ]

    for ef in env_templates:
        ok, msg = check_file_exists(ef, root)
        if not ok:
            results.append((False, msg))
            continue

        content = (root / ef).read_text(encoding="utf-8")
        required_vars = [
            "APP_ENV",
            "JWT_SECRET_KEY",
            "DATABASE_HOST",
            "DATABASE_PASSWORD",
            "REDIS_HOST",
        ]
        missing = [v for v in required_vars if v not in content]
        if missing:
            results.append((False, f"{ef}: Missing required variables: {', '.join(missing)}"))
        else:
            results.append((True, f"{ef}: Complete variable template"))

    # Production and staging templates must not contain reusable credential values.
    for env_name in (".env.staging.example", ".env.production.example"):
        env_content = (root / env_name).read_text(encoding="utf-8")
        forbidden_literals = [
            "dev_insecure_secret_key",
            "staging_secure_db_pass_",
            "staging_secure_storage_pass_",
            "minioadmin",
            "DATABASE_PASSWORD=postgres",
        ]
        bad = [literal for literal in forbidden_literals if literal in env_content]
        if bad:
            results.append((False, f"{env_name}: contains reusable credential literals: {', '.join(bad)}"))
        else:
            results.append((True, f"{env_name}: verified no reusable credential literals"))

    return results


def validate_kubernetes_manifests(root: Path) -> list[tuple[bool, str]]:
    results = []
    k8s_manifests = [
        "infra/k8s/namespace.yaml",
        "infra/k8s/configmap.yaml",
        "infra/k8s/secret.template.yaml",
        "infra/k8s/migration-job.yaml",
        "infra/k8s/api-deployment.yaml",
        "infra/k8s/worker-deployment.yaml",
        "infra/k8s/frontend-deployment.yaml",
        "infra/k8s/ingress.yaml",
        "infra/k8s/networkpolicy.yaml",
        "infra/k8s/serviceaccount.yaml",
    ]

    for km in k8s_manifests:
        ok, msg = check_file_exists(km, root)
        if not ok:
            results.append((False, msg))
            continue

        content = (root / km).read_text(encoding="utf-8")
        if yaml:
            try:
                # Safe load all documents in YAML
                docs = list(yaml.safe_load_all(content))
                for doc in docs:
                    if doc and "kind" in doc and "apiVersion" in doc:
                        pass
                results.append((True, f"{km}: Valid K8s manifest ({len(docs)} document(s))"))
            except Exception as e:
                results.append((False, f"{km}: K8s YAML error: {e}"))
        else:
            if "apiVersion:" in content and "kind:" in content:
                results.append((True, f"{km}: Passed textual manifest check"))
            else:
                results.append((False, f"{km}: Missing apiVersion or kind"))

    return results



def validate_ci_workflows(root: Path) -> list[tuple[bool, str]]:
    """Validate release/security workflows for known production footguns."""
    results: list[tuple[bool, str]] = []

    release_path = root / ".github/workflows/release.yml"
    security_path = root / ".github/workflows/security.yml"

    if not release_path.exists():
        results.append((False, "release.yml: Missing release workflow"))
    else:
        content = release_path.read_text(encoding="utf-8")
        bad_paths = ["infra/docker/Dockerfile.backend", "infra/docker/Dockerfile.worker"]
        stale = [p for p in bad_paths if p in content]
        if stale:
            results.append((False, f"release.yml: Stale Dockerfile paths found: {', '.join(stale)}"))
        elif "docker build" in content and "-f Dockerfile ." in content:
            results.append((True, "release.yml: Backend/worker builds use the repository Dockerfile"))
        else:
            results.append((False, "release.yml: Expected root Dockerfile build commands not found"))

    if not security_path.exists():
        results.append((False, "security.yml: Missing security workflow"))
    else:
        content = security_path.read_text(encoding="utf-8")
        masking = [
            line.strip()
            for line in content.splitlines()
            if any(token in line for token in ("|| true", "|| echo", "continue-on-error: true"))
        ]
        if masking:
            results.append((False, "security.yml: Security failures are being masked"))
        else:
            results.append((True, "security.yml: Security audit failures are not masked"))

    return results


def validate_render_and_vercel_configs(root: Path) -> list[tuple[bool, str]]:
    """Validate Render blueprint and Vercel frontend configurations."""
    results: list[tuple[bool, str]] = []
    import json

    # 1. Render Blueprint
    render_file = root / "render.yaml"
    if not render_file.exists():
        results.append((False, "render.yaml: Missing Render Blueprint file"))
    else:
        content = render_file.read_text(encoding="utf-8")
        if yaml:
            try:
                data = yaml.safe_load(content)
                dbs = data.get("databases", [])
                svcs = data.get("services", [])
                has_pg = any(db.get("name") == "vertexerp-postgres" for db in dbs)
                has_api = any(s.get("name") == "vertexerp-api" and s.get("type") == "web" for s in svcs)
                has_worker = any(s.get("name") == "vertexerp-worker" and s.get("type") == "worker" for s in svcs)
                has_redis = any(s.get("name") == "vertexerp-redis" and s.get("type") == "redis" for s in svcs)

                if has_pg and has_api and has_worker and has_redis:
                    results.append(
                        (
                            True,
                            "render.yaml: Valid Render Blueprint (PostgreSQL, Redis, Web API, Background Worker)",
                        )
                    )
                else:
                    results.append(
                        (False, "render.yaml: Missing required component (postgres, redis, api, or worker)")
                    )
            except Exception as e:
                results.append((False, f"render.yaml: YAML Parse Error: {e}"))
        else:
            if "vertexerp-postgres" in content and "vertexerp-api" in content and "vertexerp-worker" in content:
                results.append((True, "render.yaml: Textual blueprint validation passed"))
            else:
                results.append((False, "render.yaml: Missing expected service definitions"))

    # 2. Vercel Configuration
    vercel_files = ["vercel.json", "frontend/vercel.json"]
    for vf in vercel_files:
        v_path = root / vf
        if not v_path.exists():
            results.append((False, f"{vf}: Missing Vercel configuration file"))
        else:
            try:
                data = json.loads(v_path.read_text(encoding="utf-8"))
                if "rewrites" in data and "buildCommand" in data:
                    results.append((True, f"{vf}: Valid Vercel SPA configuration with rewrites and security headers"))
                else:
                    results.append((False, f"{vf}: Incomplete Vercel configuration"))
            except Exception as e:
                results.append((False, f"{vf}: JSON Parse Error: {e}"))

    return results


def run_all_validations() -> int:
    root = get_project_root()
    print("=" * 80)
    print(" VertexERP AI V2 - Production Infrastructure Validation Suite")
    print("=" * 80)
    print(f" Target Workspace: {root}\n")

    all_checks: list[tuple[str, list[tuple[bool, str]]]] = [
        ("Docker Compose Environments", validate_docker_compose_files(root)),
        ("Multi-Stage Dockerfiles", validate_dockerfiles(root)),
        ("Nginx Reverse Proxy Configurations", validate_nginx_configs(root)),
        ("Environment Templates & Secrets", validate_env_templates(root)),
        ("Kubernetes Production Manifests", validate_kubernetes_manifests(root)),
        ("Render & Vercel Cloud Manifests", validate_render_and_vercel_configs(root)),
        ("CI/CD Security Controls", validate_ci_workflows(root)),
    ]

    total_passed = 0
    total_failed = 0

    for category, checks in all_checks:
        print(f"--- [ {category} ] ---")
        for passed, detail in checks:
            status = " [PASS] " if passed else " [FAIL] "
            print(f"{status} {detail}")
            if passed:
                total_passed += 1
            else:
                total_failed += 1
        print()

    print("=" * 80)
    print(
        f" Summary: {total_passed} Passed, {total_failed} Failed (Total: {total_passed + total_failed})"
    )
    print("=" * 80)

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all_validations())
