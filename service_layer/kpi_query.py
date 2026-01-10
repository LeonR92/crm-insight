from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from database import KPI, InsuranceCompany, PracticeArea


class KPISchema(BaseModel):
    """Schema representing a single KPI record with resolved names."""

    id: int = Field(..., description="Eindeutige ID des KPI-Eintrags")
    incoming_fees: int = Field(..., ge=0, description="Eingegangene Honorare in EUR")
    fees_collected: int = Field(..., ge=0, description="Realisierte Honorare in EUR")
    new_mandates: int = Field(..., ge=0, description="Anzahl neuer Mandate")

    insurance_company_name: str = Field(..., description="Name der Versicherung")
    practice_area_name: str = Field(..., description="Name des Sachgebiets")

    @field_validator("insurance_company_name", mode="before")
    @classmethod
    def get_name_from_obj(cls, v, info):
        if hasattr(v, "name"):
            return v.name
        return v

    model_config = ConfigDict(from_attributes=True)


def get_kpis_by_insurance_company_and_practice_area(
    session: Session, insurance_company_id: int, practice_area_id: int
) -> List[KPISchema]:
    """
    Fetches KPIs and eagerly loads related names to populate the schema.
    """
    kpis = (
        session.query(KPI)
        .options(joinedload(KPI.insurance_company), joinedload(KPI.practice_area))
        .filter(
            KPI.insurance_company_id == insurance_company_id,
            KPI.practice_area_id == practice_area_id,
        )
        .all()
    )

    result = []
    for k in kpis:
        data = KPISchema(
            id=k.id,
            incoming_fees=k.incoming_fees,
            fees_collected=k.fees_collected,
            new_mandates=k.new_mandates,
            insurance_company_name=k.insurance_company.name,
            practice_area_name=k.practice_area.name,
        )
        result.append(data)

    return result


def _get_raw_kpi_stats(session: Session):
    """Only responsible for the database join and aggregation."""
    return (
        session.query(
            InsuranceCompany.name.label("company"),
            PracticeArea.name.label("area"),
            func.sum(KPI.incoming_fees).label("incoming"),
            func.sum(KPI.fees_collected).label("collected"),
            func.sum(KPI.new_mandates).label("mandates"),
        )
        .join(KPI, KPI.insurance_company_id == InsuranceCompany.id)
        .join(PracticeArea, KPI.practice_area_id == PracticeArea.id)
        .group_by("company", "area")
        .all()
    )


def get_analytics_payload(session: Session) -> Dict[str, Any]:
    """Generates the analytics payload for the dashboard.

    :param session: The database session
    :type session: Session
    :return: The analytics payload
    :rtype: Dict[str, Any]
    """
    stats = _get_raw_kpi_stats(session)

    area_totals = {}
    company_mandates = {}

    for row in stats:

        area_totals.setdefault(row.area, {"in": 0, "out": 0})
        area_totals[row.area]["in"] += row.incoming
        area_totals[row.area]["out"] += row.collected

        company_mandates[row.company] = (
            company_mandates.get(row.company, 0) + row.mandates
        )

    return {
        "bar": {
            "labels": list(area_totals.keys()),
            "incoming": [v["in"] for v in area_totals.values()],
            "collected": [v["out"] for v in area_totals.values()],
        },
        "donut": {
            "labels": list(company_mandates.keys()),
            "series": list(company_mandates.values()),
        },
    }
