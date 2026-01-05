from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Session, joinedload

from database import KPI


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


class KPIAIOutput(BaseModel):
    """Finaler Report für PydanticAI."""

    insurance_company_name: str
    practice_area_name: str
    data: List[KPISchema]
    summary_german: str = Field(..., description="Management-Summary auf Deutsch")

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
