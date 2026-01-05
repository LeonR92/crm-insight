from typing import List

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from ai_model import model
from database import session
from service_layer.kpi_query import (
    KPISchema,
    get_kpis_by_insurance_company_and_practice_area,
)
from service_layer.reports_query import ReportSchema, get_report_analysis_payload


class Insurance360Output(BaseModel):
    """The complete executive dashboard model."""

    insurance_company_name: str
    practice_area_name: str

    kpi_data: List[KPISchema]
    visit_reports: List[ReportSchema]

    kpi_analysis: str = Field(description="Quantitative Analyse der Kennzahlen.")
    report_analysis: str = Field(description="Qualitative Analyse der Besuchsberichte.")

    final_executive_summary: str = Field(
        description="Ein Gesamtfazit, das Zahlen und Berichte verknüpft."
    )


simple_agent = Agent(
    model,
    output_type=Insurance360Output,
    system_prompt=(
        "You are a Senior Insurance Analyst. Analyze the provided KPI data and "
        "visit reports to create a combined executive summary in German."
    ),
)


def run_simple_360(company_id: int, area_id: int):
    kpis = get_kpis_by_insurance_company_and_practice_area(session, company_id, area_id)
    reports = get_report_analysis_payload(session, company_id, area_id)

    prompt = f"Analyze this data for {reports['insurance_company_name']}:\n\nKPIs: {kpis}\n\nReports: {reports}"

    result = simple_agent.run_sync(prompt)
    return result.output


if __name__ == "__main__":
    final_data = run_simple_360(3, 4)
    print(f"Executive Summary: {final_data.final_executive_summary}")
