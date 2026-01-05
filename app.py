import fastapi

from database import session
from service_layer.kpi_query import get_kpis_by_insurance_company_and_practice_area
from service_layer.reports_query import get_report_analysis_payload

app = fastapi.FastAPI()


@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}


@app.get(
    "/overview/{company_id}/{area_id}",
    summary="Get company report overview",
    tags=["Reports"],
)
def get_report_overview(
    company_id: int,
    area_id: int,
):
    kpis = get_kpis_by_insurance_company_and_practice_area(session, company_id, area_id)
    reports = get_report_analysis_payload(session, company_id, area_id)

    if not kpis and not reports:
        raise fastapi.HTTPException(status_code=404, detail="Data not found")
    print(kpis, reports)
    # 3. Construct the response
    return {"kpis": kpis, "reports": reports}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
