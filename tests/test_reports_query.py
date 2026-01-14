from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, InsuranceCompany, PracticeArea, Report
from service_layer.reports_query import (
    ReportSchema,
    get_report_analysis_payload,
    get_report_by_id,
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

    # Seed basic data
    allianz = InsuranceCompany(name="Allianz")
    marine = PracticeArea(name="Marine")
    session.add_all([allianz, marine])
    session.commit()

    # Create a report
    report = Report(
        insurance_company_id=allianz.id,
        practice_area_id=marine.id,
        department_visited="Claims Management",
        visited_key_personnel="Dr. Müller",
        report_date=datetime(2024, 1, 15, 10, 0),
        report_content="Detailed meeting notes here.",
    )
    session.add(report)
    session.commit()

    yield session
    session.close()


def test_get_report_analysis_payload_success(session):
    company = session.query(InsuranceCompany).first()
    area = session.query(PracticeArea).first()

    result = get_report_analysis_payload(session, company.id, area.id)

    assert result is not None
    assert result["insurance_company_name"] == "Allianz"
    assert result["practice_area_name"] == "Marine"
    assert len(result["reports"]) == 1

    report_item = result["reports"][0]
    assert isinstance(report_item, ReportSchema)
    assert report_item.visited_key_personnel == "Dr. Müller"
    assert isinstance(report_item.report_date, datetime)


def test_get_report_analysis_payload_not_found(session):
    """Ensure None is returned if no reports match the filters."""
    result = get_report_analysis_payload(session, 999, 999)
    assert result is None


def test_get_report_by_id_success(session):
    report_in_db = session.query(Report).first()

    result = get_report_by_id(session, report_in_db.id)

    assert result is not None
    assert result.id == report_in_db.id
    assert result.insurance_company_name == "Allianz"
    assert result.report_content == "Detailed meeting notes here."


def test_get_report_by_id_none(session):
    result = get_report_by_id(session, 9999)
    assert result is None


def test_report_schema_fallback_names(session):
    """Verify the 'Unbekannt' fallback when IDs exist but relationships aren't loaded."""
    orphan_report = Report(
        insurance_company_id=999,
        practice_area_id=888,
        department_visited="Secret",
        visited_key_personnel="None",
        report_date=datetime.now(),
        report_content="...",
    )

    session.add(orphan_report)
    session.flush()

    result = get_report_by_id(session, orphan_report.id)

    assert result.insurance_company_name == "Unbekannt"
    assert result.practice_area_name == "Unbekannt"
