import os

import fastapi
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer
from fastapi.templating import Jinja2Templates
from supabase import Client, create_client

from agent.agent import run_simple_360
from database import session
from service_layer.dropdown_queries import (
    get_insurance_companies_for_dropdowns,
    get_practice_areas_for_dropdowns,
)
from service_layer.kpi_query import get_kpis_by_insurance_company_and_practice_area
from service_layer.reports_query import get_report_analysis_payload, get_report_by_id

load_dotenv()

app = fastapi.FastAPI()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
if not url or not key:
    raise ValueError("Missing Supabase credentials in .env file")
supabase: Client = create_client(url, key)
templates = Jinja2Templates(directory="templates")
security = HTTPBearer()


def get_current_user():
    response = supabase.auth.sign_in_with_password(
        {"email": "leonjy92@gmail.com", "password": "AWyFH48GlkibXn20"}
    )
    token = response.session.access_token
    try:
        user = supabase.auth.get_user(token)
        return user.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


@app.get("/me", tags=["Authentication"])
def get_my_profile(user=Depends(get_current_user)):
    return user


@app.get("/")
def hello_world(request: Request):
    insurance_companies = get_insurance_companies_for_dropdowns(session)
    practice_areas = get_practice_areas_for_dropdowns(session)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "insurance_companies": insurance_companies,
            "practice_areas": practice_areas,
        },
    )


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
    return {"kpis": kpis, "reports": reports}


@app.get("/report/{report_id}", response_class=HTMLResponse, tags=["Reports"])
def get_specific_report(request: Request, report_id: int):
    report = get_report_by_id(session, report_id)

    if not report:
        raise fastapi.HTTPException(status_code=404, detail="Report not found")

    return templates.TemplateResponse(
        "report.html", {"request": request, "report": report}
    )


@app.get(
    "/prompt/{company_id}/{area_id}",
    summary="Get company and area id prompt",
    tags=["Prompt"],
)
def prompt_test(
    company_id: int,
    area_id: int,
):
    result = run_simple_360(session, company_id, area_id)
    if not result:
        raise fastapi.HTTPException(status_code=404, detail="Data not found")
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
