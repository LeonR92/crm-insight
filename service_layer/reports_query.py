from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session, joinedload

from database import Report


class ReportSchema(BaseModel):
    """Simple, flat schema for reports."""

    id: int
    insurance_company_name: str
    practice_area_name: str
    department_visited: str
    visited_key_personnel: str
    report_date: datetime
    report_content: str

    model_config = ConfigDict(from_attributes=True)


class ReportAIOutput(BaseModel):
    """Final output for the AI."""

    insurance_company_name: str
    practice_area_name: str
    reports: List[ReportSchema]
    qualitative_summary: str = Field(description="Zusammenfassung auf Deutsch")


def get_report_analysis_payload(
    session: Session, insurance_company_id: int, practice_area_id: int
):
    # Fetch with joinedload to keep it fast
    db_reports = (
        session.query(Report)
        .options(joinedload(Report.insurance_company), joinedload(Report.practice_area))
        .filter(
            Report.insurance_company_id == insurance_company_id,
            Report.practice_area_id == practice_area_id,
        )
        .all()
    )

    if not db_reports:
        return None

    # Manually map the database objects to the flat Pydantic model
    report_list = [
        ReportSchema(
            id=r.id,
            insurance_company_name=(
                r.insurance_company.name if r.insurance_company else "Unbekannt"
            ),
            practice_area_name=r.practice_area.name if r.practice_area else "Unbekannt",
            department_visited=r.department_visited,
            visited_key_personnel=r.visited_key_personnel,
            report_date=r.report_date,
            report_content=r.report_content,
        )
        for r in db_reports
    ]

    return {
        "insurance_company_name": report_list[0].insurance_company_name,
        "practice_area_name": report_list[0].practice_area_name,
        "reports": report_list,
    }
