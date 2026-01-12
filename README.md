# crm-insight

**Project URL:** [https://crm-insight.onrender.com/](https://crm-insight.onrender.com/)

## Executive Summary

crm-insight is an agentic AI platform designed to transform fragmented CRM data into high-level business intelligence. The system automates the synthesis of structured performance metrics (KPIs) and unstructured qualitative data (visit reports), providing users with a validated, 360-degree view of account performance and relationship health.

---

## Technical Core

### Agentic Analysis Engine

The platform utilizes **PydanticAI** to manage the reasoning layer. Unlike traditional chatbot implementations, this system enforces strict schema validation on the model's output. The agent is tasked with:

- **Quantitative Reasoning:** Analyzing financial and performance-based KPIs.
- **Qualitative Synthesis:** Extracting themes and risks from raw visit reports.
- **Cross-Reference Logic:** Linking AI insights to specific database records via a computed citation system.

### The Stack

- **Framework:** FastAPI (Asynchronous Python)
- **AI Orchestration:** PydanticAI
- **Authentication:** Supabase Auth (JWT-based)
- **Database:** SQLAlchemy ORM / PostgreSQL
- **Templating:** Jinja2 for server-side rendered analytics

---

## System Architecture

### Data Integration

The system fetches data through a multi-step service layer:

1. **Dropdown Queries:** Populates industry-specific filters (Insurance Companies and Practice Areas).
2. **KPI Extraction:** Retrieves numerical performance data.
3. **Report Payload:** Gathers raw text from recent site visits and stakeholder meetings.

### AI Workflow

The `run_simple_360` function acts as the orchestrator. It passes context-specific IDs and raw data into the `simple_agent`, which generates a structured `Insurance360Output`. This output includes:

- **kpi_analysis:** A quantitative breakdown with internal citations.
- **report_analysis:** Qualitative insights derived from text.
- **final_executive_summary:** A high-level conclusion for leadership.
- **citations:** Metadata containing source IDs and direct deep-links to the source data.

---

## Project Roadmap

### Phase 1: Core Infrastructure (Complete)

- FastAPI backend and Supabase auth integration.
- Agentic reasoning loop with Pydantic validation.
- Database schema for KPIs and visit reports.

### Phase 2: UI/UX Enhancements (In Progress)

- Integration of dynamic HTML dropdowns for real-time data selection.
- Asynchronous display of agent prompt results on the dashboard.
- Advanced visualization for the analytics module.

---

## Installation

1. **Environment Setup**
   Configure your `.env` with the following:

```text
SUPABASE_URL=your_url
SUPABASE_ANON_KEY=your_key
DATABASE_URL=your_db_url

```

2. **Run Locally**

```bash
pip install -r requirements.txt
uvicorn main:app --reload

```

Would you like me to provide the HTML and JavaScript logic for the dashboard dropdowns and result displays?
