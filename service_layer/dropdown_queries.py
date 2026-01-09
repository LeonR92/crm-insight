from typing import List

from requests import Session

from database import InsuranceCompany, PracticeArea


def get_insurance_companies_for_dropdowns(db_session: Session) -> List[dict]:
    """
    Fetches a list of insurance companies for dropdown menus.

    Args:
        db_session: The database session to use for the query.

    Returns:
        A list of dictionaries containing insurance company names and IDs.
    """
    insurance_companies = db_session.query(InsuranceCompany).all()
    return [{"id": company.id, "name": company.name} for company in insurance_companies]


def get_practice_areas_for_dropdowns(db_session: Session) -> List[dict]:
    """
    Fetches a list of practice areas for dropdown menus.

    Args:
        db_session: The database session to use for the query.

    Returns:
        A list of dictionaries containing practice area names and IDs.
    """
    practice_areas = db_session.query(PracticeArea).all()
    return [{"id": area.id, "name": area.name} for area in practice_areas]
