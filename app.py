import os

import fastapi
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBearer
from fastapi.templating import Jinja2Templates
from requests import Session

from agent.agent import run_simple_360
from dependencies import get_current_user, get_db
from service_layer.dropdown_queries import (
    get_insurance_companies_for_dropdowns,
    get_practice_areas_for_dropdowns,
)
from service_layer.kpi_query import get_analytics_payload
from service_layer.reports_query import get_report_by_id

load_dotenv()

app = fastapi.FastAPI()

templates = Jinja2Templates(directory="templates")
security = HTTPBearer()


@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_redirect_handler(request: Request, exc: HTTPException):
    return RedirectResponse(url="/")


@app.get("/auth/callback")
def auth_callback(request: Request):
    return templates.TemplateResponse("callback.html", {"request": request})


@app.get("/")
def welcome_page(request: Request):
    return templates.TemplateResponse(
        "welcome.html",
        {
            "request": request,
            "supabase_url": os.getenv("SUPABASE_URL"),
            "supabase_key": os.getenv("SUPABASE_ANON_KEY"),
        },
    )


@app.get("/dashboard", dependencies=[Depends(get_current_user)])
def dashboard(
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    insurance_companies = get_insurance_companies_for_dropdowns(db_session=db)
    practice_areas = get_practice_areas_for_dropdowns(db_session=db)

    return templates.TemplateResponse(
        "dashboard.html",
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


@app.get("/analytics")
def analytics_page(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse(
        "analytics.html",
        {
            "request": request,
            "user": user,
        },
    )


@app.get("/api/analytics")
def analytics_api(db: Session = Depends(get_db)):
    return get_analytics_payload(db)


@app.get("/profile")
def profile(request: Request, user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse(
            "profile.html", {"request": request, "user": {}, "metadata": {}}
        )

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user,
            "metadata": getattr(user, "user_metadata", {}),
        },
    )


@app.get("/about")
def about(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("about.html", {"request": request, "user": user})


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response
