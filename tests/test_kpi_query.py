import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import KPI, Base, InsuranceCompany, PracticeArea
from service_layer.kpi_query import (
    KPISchema,
    get_analytics_payload,
    get_kpis_by_insurance_company_and_practice_area,
)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 1. Seed Data
    allianz = InsuranceCompany(name="Allianz")
    axa = InsuranceCompany(name="AXA")
    marine = PracticeArea(name="Marine")
    cyber = PracticeArea(name="Cyber")
    session.add_all([allianz, axa, marine, cyber])
    session.commit()

    # 2. Add KPIs
    kpis = [
        # Allianz - Marine
        KPI(
            insurance_company=allianz,
            practice_area=marine,
            incoming_fees=1000,
            fees_collected=800,
            new_mandates=5,
        ),
        KPI(
            insurance_company=allianz,
            practice_area=marine,
            incoming_fees=2000,
            fees_collected=1200,
            new_mandates=3,
        ),
        # Allianz - Cyber
        KPI(
            insurance_company=allianz,
            practice_area=cyber,
            incoming_fees=5000,
            fees_collected=4000,
            new_mandates=10,
        ),
        # AXA - Marine
        KPI(
            insurance_company=axa,
            practice_area=marine,
            incoming_fees=3000,
            fees_collected=2500,
            new_mandates=2,
        ),
    ]
    session.add_all(kpis)
    session.commit()

    yield session
    session.close()


# --- Tests ---


def test_kpi_schema_validation():
    """Test if KPISchema handles object attributes correctly."""
    # Test with raw data
    data = {
        "id": 1,
        "incoming_fees": 100,
        "fees_collected": 80,
        "new_mandates": 2,
        "insurance_company_name": "Test Co",
        "practice_area_name": "Test Area",
    }
    schema = KPISchema(**data)
    assert schema.insurance_company_name == "Test Co"


def test_get_kpis_by_filters(session):
    """Test fetching specific KPIs for a company and area."""
    allianz = session.query(InsuranceCompany).filter_by(name="Allianz").first()
    marine = session.query(PracticeArea).filter_by(name="Marine").first()

    results = get_kpis_by_insurance_company_and_practice_area(
        session, allianz.id, marine.id
    )

    assert len(results) == 2
    assert results[0].insurance_company_name == "Allianz"
    assert results[0].practice_area_name == "Marine"
    assert results[0].incoming_fees == 1000


def test_get_analytics_payload_structure(session):
    """Test the aggregation logic for the dashboard payload."""
    payload = get_analytics_payload(session)

    assert "Marine" in payload["bar"]["labels"]
    marine_idx = payload["bar"]["labels"].index("Marine")
    assert payload["bar"]["incoming"][marine_idx] == 6000
    assert payload["bar"]["collected"][marine_idx] == 4500

    assert "Allianz" in payload["donut"]["labels"]
    allianz_idx = payload["donut"]["labels"].index("Allianz")
    assert payload["donut"]["series"][allianz_idx] == 18

    assert "AXA" in payload["donut"]["labels"]
    axa_idx = payload["donut"]["labels"].index("AXA")
    assert payload["donut"]["series"][axa_idx] == 2


def test_get_analytics_empty_db(session):
    """Ensure code doesn't crash if no KPIs exist."""
    session.query(KPI).delete()
    session.commit()

    payload = get_analytics_payload(session)
    assert payload["bar"]["labels"] == []
    assert payload["donut"]["series"] == []
