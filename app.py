import os

import fastapi
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBearer
from fastapi.templating import Jinja2Templates
from requests import Session
from supabase import Client, create_client

from agent.agent import run_simple_360
from database import get_db
from service_layer.dropdown_queries import (
    get_insurance_companies_for_dropdowns,
    get_practice_areas_for_dropdowns,
)
from service_layer.reports_query import get_report_by_id

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
    if request.url.hostname in ["localhost", "127.0.0.1"]:
        return None
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Log in required"
        )

    try:
        user_data = supabase.auth.get_user(token)
        return user_data.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired"
        )


@app.get("/auth/callback")
def auth_callback(request: Request):
    return templates.TemplateResponse("callback.html", {"request": request})


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


@app.get("/", dependencies=[Depends(get_current_user)])
def dashboard(
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    insurance_companies = get_insurance_companies_for_dropdowns(db_session=db)
    practice_areas = get_practice_areas_for_dropdowns(db_session=db)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "insurance_companies": insurance_companies,
            "practice_areas": practice_areas,
            "user": user,
        },
    )


@app.get(
    "/report/{report_id}",
    response_class=HTMLResponse,
    tags=["Reports"],
    dependencies=[Depends(get_current_user)],
)
def get_specific_report(
    request: Request, report_id: int, db: Session = Depends(get_db)
):
    report = get_report_by_id(session=db, report_id=report_id)

    if not report:
        raise fastapi.HTTPException(status_code=404, detail="Report not found")

    return templates.TemplateResponse(
        "report.html", {"request": request, "report": report}
    )


@app.get(
    "/prompt/{company_id}/{area_id}",
    summary="Get company and area id prompt",
    tags=["Prompt"],
    dependencies=[Depends(get_current_user)],
)
def prompt(company_id: int, area_id: int, db: Session = Depends(get_db)):

    result = run_simple_360(session=db, company_id=company_id, area_id=area_id)

    if not result:
        raise fastapi.HTTPException(status_code=404, detail="Data not found")

    return result


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/welcome")
    response.delete_cookie("access_token")
    return response
