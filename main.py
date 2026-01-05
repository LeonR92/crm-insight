from typing import List

from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelSettings

from ai_model import model
from config import TEMPERATURE
from database import session
from service_layer.kpi_query import (
    KPIAIOutput,
    KPISchema,
    get_kpis_by_insurance_company_and_practice_area,
)
from service_layer.reports_query import (
    ReportAIOutput,
    ReportSchema,
    get_report_analysis_payload,
)


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


kpi_agent = Agent(
    model,
    system_prompt="Du bist ein hilfreicher Assistent, der KPI-Daten für Versicherungsgesellschaften und Sachgebiete analysiert und zusammenfasst.",
    model_settings=ModelSettings(temperature=TEMPERATURE),
    output_type=KPIAIOutput,
)

report_agent = Agent(
    model,
    system_prompt="Du bist ein hilfreicher Assistent, der Besuchsberichte für Versicherungsgesellschaften und Sachgebiete analysiert und zusammenfasst.",
    model_settings=ModelSettings(temperature=TEMPERATURE),
    output_type=ReportAIOutput,
)


summarise_agent = Agent(
    model,
    model_settings=ModelSettings(temperature=TEMPERATURE),
    output_type=Insurance360Output,
    system_prompt=(
        "Du bist der Chef-Analyst. Deine Aufgabe ist es, einen 360-Grad-Bericht zu erstellen."
        "Nutze die verfügbaren Daten, um eine tiefgreifende Analyse zu liefern."
    ),
)


@summarise_agent.tool_plain
async def generate_full_analysis(company_id: int, area_id: int) -> Insurance360Output:
    """Erstellt eine vollständige 360-Grad-Analyse durch Delegation an Sub-Agenten."""

    # 1. Fetch Raw Data
    kpi_raw = get_kpis_by_insurance_company_and_practice_area(
        session, company_id, area_id
    )
    report_raw = get_report_analysis_payload(session, company_id, area_id)

    kpi_result = await kpi_agent.run(f"Analysiere diese KPIs: {kpi_raw}")

    report_result = await report_agent.run(f"Analysiere diese Berichte: {report_raw}")

    # 3. Construct the 360 Object
    return Insurance360Output(
        insurance_company_name=report_raw["insurance_company_name"],
        practice_area_name=report_raw["practice_area_name"],
        kpi_data=kpi_raw,
        visit_reports=report_raw["reports"],
        kpi_analysis=kpi_result.output.summary_german,
        report_analysis=report_result.output.qualitative_summary,
        final_executive_summary="",
    )


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


if __name__ == "__main__":
    result = summarise_agent.run_sync(
        "Erstelle einen 360-Bericht für Versicherung 3 im Bereich 4.",
    )

    print(f"--- 360 BERICHT FÜR {result.output.insurance_company_name} ---")
    print(f"KPI FAZIT: {result.output.kpi_analysis}")
    print(f"REPORT FAZIT: {result.output.report_analysis}")
    print(f"EXECUTIVE SUMMARY: {result.output.final_executive_summary}")
