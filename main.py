from typing import List

from pydantic import BaseModel, Field, computed_field
from pydantic_ai import Agent, ModelSettings

from ai_model import model
from config import TEMPERATURE
from database import session
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


system_prompt = """
    Your input fields are:
1. `company_id` (str): Unique ID of the insurance company
2. `area_id` (str): Unique ID of the practice area
3. `kpis` (str): List of quantitative KPI data
4. `reports` (str): List of qualitative visit reports
Your output fields are:
1. `reasoning` (str): 
2. `output` (Insurance360Output): The structured analysis result
All interactions will be structured in the following way, with the appropriate values filled in.

[[ ## company_id ## ]]
{company_id}

[[ ## area_id ## ]]
{area_id}

[[ ## kpis ## ]]
{kpis}

[[ ## reports ## ]]
{reports}

[[ ## reasoning ## ]]
{reasoning}

[[ ## output ## ]]
{output}      
In adhering to this structure, your objective is: 
        You are a Senior Insurance Analyst. Analyze the provided KPI and Report data.
        Provide a professional summary in German.
        
        STRICT CITATION RULES:
        1. Every claim must be cited using square brackets, e.g., [KPI-1] or URL.
        2. For every citation object, use the exact company_id and area_id provided.
        3. Ensure all cited IDs are listed in the final 'citations' field.
"""

simple_agent = Agent(
    model,
    output_type=Insurance360Output,  # Note: result_type is the standard Pydantic AI parameter
    system_prompt=system_prompt,
    model_settings=ModelSettings(temperature=TEMPERATURE),
)


def run_simple_360(company_id: int, area_id: int):
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


if __name__ == "__main__":

    final_data = run_simple_360(3, 4)
    print(f"Executive Summary: {final_data.final_executive_summary}")

    if final_data.citations:
        print(f"Sample Citation URL: {final_data.citations[0].url}")
