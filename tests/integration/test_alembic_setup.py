"""Integration tests for Alembic configuration and migration discovery."""

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_config_and_script_discovery():
    """Verifies that alembic.ini is parseable and discovers baseline migration."""
    alembic_ini_path = Path("alembic.ini")
    assert alembic_ini_path.exists(), "alembic.ini missing!"

    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)

    # Verify head revision is present
    heads = script.get_heads()
    assert len(heads) == 1, f"Expected exactly 1 head revision, found {len(heads)}: {heads}"
    assert len(heads[0]) > 0

    # Verify base revision exists
    base_revision = script.get_base()
    assert base_revision == "0001_baseline_v2"

    # Verify linear history (no branches)
    rev_0001 = script.get_revision("0001_baseline_v2")
    assert rev_0001 is not None
    assert rev_0001.down_revision is None

    rev_0002 = script.get_revision("0002_identity_org_audit")
    assert rev_0002 is not None
    assert rev_0002.down_revision == "0001_baseline_v2"

    rev_0003 = script.get_revision("0003_org_domain_complete")
    assert rev_0003 is not None
    assert rev_0003.down_revision == "0002_identity_org_audit"

    rev_0004 = script.get_revision("0004_hr_domain_complete")
    assert rev_0004 is not None
    assert rev_0004.down_revision == "0003_org_domain_complete"

    rev_0005 = script.get_revision("0005_crm_domain_complete")
    assert rev_0005 is not None
    assert rev_0005.down_revision == "0004_hr_domain_complete"

    rev_0006 = script.get_revision("0006_inventory_procurement")
    assert rev_0006 is not None
    assert rev_0006.down_revision == "0005_crm_domain_complete"

    rev_0007 = script.get_revision("0007_finance_accounting_domain")
    assert rev_0007 is not None
    assert rev_0007.down_revision == "0006_inventory_procurement"

    rev_0008 = script.get_revision("0008_manufacturing_mrp_domain")
    assert rev_0008 is not None
    assert rev_0008.down_revision == "0007_finance_accounting_domain"

    rev_0009 = script.get_revision("0009_analytics_reporting_domain")
    assert rev_0009 is not None
    assert rev_0009.down_revision == "0008_manufacturing_mrp_domain"

    rev_0010 = script.get_revision("0010_ai_platform_domain")
    assert rev_0010 is not None
    assert rev_0010.down_revision == "0009_analytics_reporting_domain"

    rev_0011 = script.get_revision("0011_rag_knowledge_domain")
    assert rev_0011 is not None
    assert rev_0011.down_revision == "0010_ai_platform_domain"

    rev_0012 = script.get_revision("0012_background_processing")
    assert rev_0012 is not None
    assert rev_0012.down_revision == "0011_rag_knowledge_domain"

    rev_0013 = script.get_revision("0013_enforce_postgresql_rls")
    assert rev_0013 is not None
    assert rev_0013.down_revision == "0012_background_processing"

    rev_0014 = script.get_revision("0014_pgvector_hnsw_indexes")
    assert rev_0014 is not None
    assert rev_0014.down_revision == "0013_enforce_postgresql_rls"

    rev_0015 = script.get_revision("0015_schema_alignment")
    assert rev_0015 is not None
    assert rev_0015.down_revision == "0014_pgvector_hnsw_indexes"

    assert heads[0] == "0015_schema_alignment"
