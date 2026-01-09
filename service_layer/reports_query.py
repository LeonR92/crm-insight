from datetime import datetime

from pydantic import BaseModel, ConfigDict
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


def get_report_by_id(session: Session, report_id: int) -> ReportSchema | None:
    db_report = session.query(Report).filter(Report.id == report_id).first()
    if not db_report:
        return None
    report = ReportSchema(
        id=db_report.id,
        insurance_company_name=(
            db_report.insurance_company.name
            if db_report.insurance_company
            else "Unbekannt"
        ),
        practice_area_name=(
            db_report.practice_area.name if db_report.practice_area else "Unbekannt"
        ),
        department_visited=db_report.department_visited,
        visited_key_personnel=db_report.visited_key_personnel,
        report_date=db_report.report_date,
        report_content=db_report.report_content,
    )

    return report
