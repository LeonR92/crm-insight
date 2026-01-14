import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, InsuranceCompany, PracticeArea
from service_layer.dropdown_queries import (
    get_insurance_companies_for_dropdowns,
    get_practice_areas_for_dropdowns,
)


@pytest.fixture(name="db_session")
def session_fixture():
    """Setup a clean in-memory database for dropdown testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()


def test_get_insurance_companies_dropdown_success(db_session):
    companies = [
        InsuranceCompany(name="Allianz"),
        InsuranceCompany(name="AXA"),
        InsuranceCompany(name="Zurich"),
    ]
    db_session.add_all(companies)
    db_session.commit()

    result = get_insurance_companies_for_dropdowns(db_session)

    assert len(result) == 3
    assert result[0] == {"id": 1, "name": "Allianz"}
    assert result[1] == {"id": 2, "name": "AXA"}
    assert isinstance(result, list)
    assert isinstance(result[0], dict)


def test_get_insurance_companies_dropdown_empty(db_session):
    """Ensure an empty table returns an empty list, not None."""
    result = get_insurance_companies_for_dropdowns(db_session)
    assert result == []


def test_get_practice_areas_dropdown_success(db_session):
    # 1. Seed the database
    areas = [PracticeArea(name="Cyber Risk"), PracticeArea(name="Marine Liability")]
    db_session.add_all(areas)
    db_session.commit()

    result = get_practice_areas_for_dropdowns(db_session)

    assert len(result) == 2
    for item in result:
        assert "id" in item
        assert "name" in item

    assert result[0]["name"] == "Cyber Risk"


def test_get_practice_areas_dropdown_empty(db_session):
    result = get_practice_areas_for_dropdowns(db_session)
    assert result == []
