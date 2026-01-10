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


def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    try:
        # 2. Ask Supabase to verify the token
        user_data = supabase.auth.get_user(token)
        return user_data.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )


def require_role(allowed_roles: list[str]):
    def role_checker(user=Depends(get_current_user)):
        user_role = user.app_metadata.get("role", "user")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user_role}' does not have access here.",
            )
        return user

    return role_checker


@app.get("/auth/callback")
def auth_callback(request: Request):
    return templates.TemplateResponse("callback.html", {"request": request})


@app.get("/me")
def read_me(user=Depends(get_current_user)):
    return {"email": user.email, "role": user.app_metadata.get("role")}


@app.get("/welcome")
def welcome_page(request: Request):
    return templates.TemplateResponse(
        "welcome.html",
        {
            "request": request,
            "supabase_url": os.getenv("SUPABASE_URL"),
            "supabase_key": os.getenv("SUPABASE_ANON_KEY"),
        },
    )


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
