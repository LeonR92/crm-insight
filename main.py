from pydantic_ai import Agent, ModelSettings

from ai_model import model
from config import TEMPERATURE
from database import session
from service_layer.kpi_query import (
    KPIAIOutput,
    get_kpis_by_insurance_company_and_practice_area,
)

kpi_agent = Agent(
    model,
    system_prompt="Du bist ein hilfreicher Assistent, der KPI-Daten für Versicherungsgesellschaften und Sachgebiete analysiert und zusammenfasst.",
    model_settings=ModelSettings(temperature=TEMPERATURE),
    output_type=KPIAIOutput,
)


if __name__ == "__main__":
    kpis = get_kpis_by_insurance_company_and_practice_area(session, 3, 4)
    answer = kpi_agent.run_sync(f"what are these kpis {kpis}?")
    print(answer.output)
