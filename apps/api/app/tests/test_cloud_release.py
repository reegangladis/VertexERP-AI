import pytest
from app.services.release_engineering_service import ReleaseEngineeringService
from app.services.cloud_deployment_service import CloudDeploymentService
from app.services.finops_service import FinOpsService
from app.services.incident_management_service import IncidentManagementService


# 1. Release Engineering Tests
def test_semver_validation():
    rel = ReleaseEngineeringService()
    assert rel.validate_semver("v1.0.0") is True
    assert rel.validate_semver("v1.2.3-rc.1") is True
    assert rel.validate_semver("1.0.0") is True
    assert rel.validate_semver("invalid_version") is False


def test_create_v1_0_0_release():
    rel = ReleaseEngineeringService()
    release = rel.create_release(
        version="v1.0.0",
        release_name="VertexERP AI Global Enterprise Release",
        release_type="MAJOR",
        git_sha="a7f9b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1",
    )

    assert release["version"] == "v1.0.0"
    assert release["status"] == "RELEASED"
    assert "Highlights & Features" in release["release_notes"]
    assert "docker_api_digest" in release["artifacts"]


def test_execute_rollback():
    rel = ReleaseEngineeringService()
    rollback = rel.execute_rollback(
        target_version="v0.9.5",
        environment_name="Production",
        reason="Performance test regression",
    )

    assert rollback["status"] == "COMPLETED"
    assert rollback["target_version"] == "v0.9.5"
    assert rollback["traffic_drained"] is True


# 2. Cloud Deployment & Multi-Region Tests
def test_cloud_region_listing_and_failover():
    deploy = CloudDeploymentService()
    regions = deploy.list_regions()
    assert len(regions) >= 3

    primary = next((r for r in regions if r["role"] == "PRIMARY"), None)
    assert primary is not None
    assert primary["region_code"] == "us-east-1"

    # Trigger failover
    failover = deploy.trigger_regional_failover(
        primary_region="us-east-1",
        secondary_region="eu-central-1",
        reason="Outage simulation drill",
    )
    assert failover["status"] == "COMPLETED"
    assert failover["new_primary"] == "eu-central-1"
    assert failover["geo_dns_updated"] is True


def test_canary_deployment_trigger():
    deploy = CloudDeploymentService()
    dep = deploy.trigger_canary_deployment(
        environment_name="Production-US-East",
        version="v1.0.0",
        traffic_percent=15.0,
    )

    assert dep["status"] == "SUCCESS"
    assert dep["strategy"] == "CANARY"
    assert dep["canary_traffic_percent"] == 15.0


# 3. FinOps Engine Tests
def test_finops_monthly_cost_summary():
    finops = FinOpsService()
    summary = finops.get_monthly_cost_summary()

    assert summary["total_cost_usd"] > 0.0
    assert summary["budget_utilized_percent"] <= 100.0
    assert "kubernetes_eks" in summary["service_breakdown"]
    assert len(summary["recommendations"]) >= 3


def test_finops_budget_alert():
    finops = FinOpsService()
    alert_normal = finops.evaluate_budget_alert(current_spend=35000.0, budget=50000.0)
    assert alert_normal["alert_triggered"] is False

    alert_warning = finops.evaluate_budget_alert(current_spend=43500.0, budget=50000.0)
    assert alert_warning["alert_triggered"] is True
    assert alert_warning["severity"] == "MEDIUM"


# 4. Incident Management Tests
def test_incident_logging_and_resolution():
    inc = IncidentManagementService()
    logged = inc.log_incident(
        title="Test Gateway Latency Spike",
        severity="P2",
        affected_services=["api_gateway"],
    )

    assert logged["status"] == "INVESTIGATING"
    assert "INC-2026-" in logged["incident_number"]

    resolved = inc.resolve_incident(
        incident_number=logged["incident_number"],
        mttr_minutes=12.5,
        root_cause="Transient Redis connection exhaustion",
    )
    assert resolved["status"] == "RESOLVED"
    assert resolved["mttr_minutes"] == 12.5

    summary = inc.get_mttr_summary()
    assert summary["average_mttr_minutes"] > 0.0
    assert summary["mttr_sla_met"] is True
