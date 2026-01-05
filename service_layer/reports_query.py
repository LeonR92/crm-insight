from typing import List

from sqlalchemy.orm import Session

from database import Report


def get_reports_by_insurance_company_and_practice_area(
    session: Session, insurance_company_id: int, practice_area_id: int
) -> List[Report]:
    return (
        session.query(Report)
        .filter(
            Report.insurance_company_id == insurance_company_id,
            Report.practice_area_id == practice_area_id,
        )
        .all()
    )
