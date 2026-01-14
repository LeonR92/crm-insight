from typing import List

from pydantic import BaseModel, Field, computed_field
from pydantic_ai import Agent, ModelSettings
from sqlalchemy.orm import Session

from agent.ai_model import TEMPERATURE, model
from agent.prompt import PROMPT_V1
from service_layer.kpi_query import (
    KPISchema,
    get_kpis_by_insurance_company_and_practice_area,
)
from service_layer.reports_query import ReportSchema, get_report_analysis_payload


class Citation(BaseModel):
    source_id: str = Field(description="The ID of the report or KPI (e.g., 'KPI-1')")
    company_id: int = Field(description="The company_id provided in the prompt")
    area_id: int = Field(description="The area_id provided in the prompt")

    @computed_field
    @property
    def url(self) -> str:
        return f"http://0.0.0.0:8000/overview/{self.company_id}/{self.area_id}"


class Insurance360Output(BaseModel):
    insurance_company_name: str
    practice_area_name: str
    kpi_data: List[KPISchema]
    visit_reports: List[ReportSchema]

    kpi_analysis: str = Field(description="Quantitative Analyse mit [ID] Zitaten.")
    report_analysis: str = Field(description="Qualitative Analyse mit Zitaten.")
    final_executive_summary: str = Field(
        description="Ein Gesamtfazit mit verknüpften [ID] Zitaten."
    )
    citations: List[Citation] = Field(default_factory=list)


simple_agent = Agent(
    model,
    output_type=Insurance360Output,
    system_prompt=PROMPT_V1,
    model_settings=ModelSettings(temperature=TEMPERATURE),
)


def run_simple_360(session: Session, company_id: int, area_id: int):
    kpis = get_kpis_by_insurance_company_and_practice_area(session, company_id, area_id)
    reports = get_report_analysis_payload(session, company_id, area_id)

    prompt = (
        f"Context IDs: company_id={company_id}, area_id={area_id}\n\n"
        f"Analyze this data for {reports.get('insurance_company_name', 'Unknown')}:\n\n"
        f"KPIs: {kpis}\n\n"
        f"Reports: {reports}"
    )

    result = simple_agent.run_sync(prompt)
    return result.output
