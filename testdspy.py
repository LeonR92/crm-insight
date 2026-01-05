import os
from typing import List

import dspy
from dotenv import load_dotenv
from pydantic import BaseModel, Field, computed_field

# --- 1. SCHEMAS (From your existing code) ---


class KPISchema(BaseModel):
    id: str
    name: str
    value: float
    unit: str


class ReportSchema(BaseModel):
    id: str
    title: str
    content: str


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


# --- 2. DSPY SIGNATURE ---


class Insurance360Signature(dspy.Signature):
    """
    You are a Senior Insurance Analyst. Analyze the provided KPI and Report data.
    Provide a professional summary in German.

    STRICT CITATION RULES:
    1. Every claim must be cited using square brackets, e.g., [KPI-1] or [REPORT-10].
    2. For every citation object, use the exact company_id and area_id provided.
    3. Ensure all cited IDs are listed in the final 'citations' field.
    """

    company_id = dspy.InputField(desc="Unique ID of the insurance company")
    area_id = dspy.InputField(desc="Unique ID of the practice area")
    kpis = dspy.InputField(desc="List of quantitative KPI data")
    reports = dspy.InputField(desc="List of qualitative visit reports")

    output: Insurance360Output = dspy.OutputField(desc="The structured analysis result")


# --- 3. DSPY MODULE ---


class InsuranceAnalyst(dspy.Module):
    def __init__(self):
        super().__init__()
        # TypedChainOfThought handles the Pydantic parsing and reasoning
        self.analyze = dspy.ChainOfThought(Insurance360Signature)

    def forward(self, company_id, area_id, kpis, reports):
        # We call the predictor
        result = self.analyze(
            company_id=company_id, area_id=area_id, kpis=kpis, reports=reports
        )
        return result.output


# --- 4. EXECUTION ---


def main():
    load_dotenv()

    lm = dspy.LM(
        "mistral/mistral-large-latest",
        api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.2,
    )
    dspy.configure(lm=lm)

    company_id = 3
    area_id = 4
    mock_kpis = [{"id": "KPI-1", "name": "Loss Ratio", "value": 75.5, "unit": "%"}]
    mock_reports = [
        {
            "id": "REPORT-10",
            "title": "Q4 Visit",
            "content": "Claims processing is slowing down.",
        }
    ]

    module = InsuranceAnalyst()

    print("--- RUNNING ANALYSIS ---")
    prediction = module.forward(
        company_id=company_id, area_id=area_id, kpis=mock_kpis, reports=mock_reports
    )

    print(f"Company: {prediction.insurance_company_name}")
    print(f"Summary: {prediction.final_executive_summary}")
    print("\nCitations Generated:")
    for cit in prediction.citations:
        print(f"- {cit.source_id}: {cit.url}")

    print("\n--- THE DSPY PROMPT ---")
    lm.inspect_history(n=1)


if __name__ == "__main__":
    main()
