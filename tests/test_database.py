import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import (
    KPI,
    Base,  # Import your actual app code
    InsuranceCompany,
    PracticeArea,
    Report,
)

# Test db
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create table
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_create_insurance_with_kpi(db):
    # Create Company
    company = InsuranceCompany(name="Global Insure")
    db.add(company)
    db.commit()

    # Create Practice Area
    area = PracticeArea(name="Cyber Security")
    db.add(area)
    db.commit()

    # Create KPI linked to both
    new_kpi = KPI(
        insurance_company_id=company.id,
        practice_area_id=area.id,
        incoming_fees=5000,
        fees_collected=4500,
        new_mandates=10,
    )
    db.add(new_kpi)
    db.commit()

    assert len(company.kpis) == 1
    assert company.kpis[0].incoming_fees == 5000
    assert area.kpis[0].new_mandates == 10


def test_report_creation(db):
    company = InsuranceCompany(name="Test Corp")
    area = PracticeArea(name="General")
    db.add_all([company, area])
    db.commit()

    from datetime import datetime

    report = Report(
        insurance_company_id=company.id,
        practice_area_id=area.id,
        department_visited="Claims",
        visited_key_personnel="John Doe",
        report_date=datetime.now(),
        report_content="Excellent meeting.",
    )
    db.add(report)
    db.commit()

    assert report.id is not None
    assert report.insurance_company.name == "Test Corp"
