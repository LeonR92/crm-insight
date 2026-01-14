import re
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from agent.agent import Insurance360Output, run_simple_360
from database import KPI, Base, InsuranceCompany, PracticeArea, Report


@pytest.fixture
def eval_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    company = InsuranceCompany(id=1, name="Test Insurance")
    area = PracticeArea(id=1, name="Legal Tech")
    session.add_all([company, area])
    session.commit()

    session.add(
        KPI(
            id=101,
            insurance_company_id=1,
            practice_area_id=1,
            incoming_fees=5000,
            fees_collected=4000,
            new_mandates=10,
        )
    )
    session.add(
        Report(
            id=201,
            insurance_company_id=1,
            practice_area_id=1,
            department_visited="Claims",
            visited_key_personnel="John Doe",
            report_date=datetime.now(),
            report_content="The efficiency is high.",
        )
    )
    session.commit()
    yield session
    session.close()


def test_agent_output_deterministics(eval_session):
    """
    Evaluates the agent's output without using an LLM judge.
    Tests grounding, citations, and structural integrity.
    """
    company_id, area_id = 1, 1
    output = run_simple_360(eval_session, company_id, area_id)

    assert isinstance(output, Insurance360Output)
    assert output.insurance_company_name == "Test Insurance"
    assert output.practice_area_name == "Legal Tech"

    all_text = f"{output.kpi_analysis} {output.report_analysis} {output.final_executive_summary}"
    mentioned_ids = re.findall(r"\[([A-Za-z0-9-]+)\]", all_text)

    citation_source_ids = [c.source_id for c in output.citations]

    for mid in mentioned_ids:
        assert (
            mid in citation_source_ids
        ), f"Agent mentioned {mid} but didn't provide a citation object."

    kpi_values = [
        str(output.kpi_data[0].incoming_fees),
        str(output.kpi_data[0].fees_collected),
    ]
    for val in kpi_values:
        numbers_in_text = re.findall(r"\d{3,}", output.kpi_analysis)
        source_numbers = [str(k.incoming_fees) for k in output.kpi_data] + [
            str(k.fees_collected) for k in output.kpi_data
        ]

        for num in numbers_in_text:
            if num not in source_numbers:
                print(
                    f"Potential Hallucination: {num} found in text but not in source KPIs."
                )

    for citation in output.citations:
        assert citation.company_id == company_id
        assert citation.area_id == area_id
        assert f"/{company_id}/{area_id}" in citation.url
