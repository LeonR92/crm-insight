import os
import random

from dotenv import load_dotenv
from faker import Faker
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker

# Import your models
from database import KPI, Base, InsuranceCompany, PracticeArea, Report

# Setup
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
fake = Faker("de_DE")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


def clear_database():
    """Wipes data in correct order to respect Foreign Key constraints."""
    print("Cleaning database...")
    session.execute(delete(Report))
    session.execute(delete(KPI))
    session.execute(delete(InsuranceCompany))
    session.execute(delete(PracticeArea))
    session.commit()


def populate_database(number_of_rows: int):
    Base.metadata.create_all(engine)
    clear_database()

    # 1. Create Practice Areas
    practice_names = [
        "Verkehrsrecht",
        "Haftpflichtrecht",
        "Versicherungsbetrug",
        "Personenschaden",
        "Sachversicherungsrecht",
        "D&O Versicherung",
        "Rechtsschutz",
        "Cyber-Risiken",
        "Arbeitsrecht (AVB)",
    ]
    p_areas = [PracticeArea(name=name) for name in practice_names]
    session.add_all(p_areas)
    session.flush()  # Flush to get IDs without committing full transaction yet

    # 2. Create Insurance Companies
    insurance_names = [
        "Allianz SE",
        "AXA Konzern AG",
        "HUK-COBURG",
        "Signal Iduna",
        "R+V Versicherung",
        "Ergo Group",
        "DEVK Versicherungen",
        "Generali Deutschland",
        "Barmenia",
        "Gothaer",
        "VHV Versicherungen",
    ]
    companies = [InsuranceCompany(name=name) for name in insurance_names]
    session.add_all(companies)
    session.flush()

    # 3. Create THE COMBINATION (KPIs)
    # This ensures that every report generated later belongs to a valid Co/Area pair
    print("Generating KPI data (The Matrix)...")
    active_combinations = []

    for co in companies:
        # Each company works with a random subset of practice areas
        target_areas = random.sample(p_areas, k=random.randint(4, len(p_areas)))
        for area in target_areas:
            mandates = random.randint(15, 200)
            avg_val = random.randint(900, 3500)
            incoming = mandates * avg_val
            collected = int(incoming * random.uniform(0.88, 0.99))

            kpi = KPI(
                insurance_company_id=co.id,
                practice_area_id=area.id,
                new_mandates=mandates,
                incoming_fees=incoming,
                fees_collected=collected,
            )
            session.add(kpi)
            # Store the valid combinations for the Report generation
            active_combinations.append((co, area))

    # 4. Generate Reports based ON THOSE COMBINATIONS
    print(f"Generating {number_of_rows} Reports based on combinations...")

    report_templates = [
        "Strategiemeeting mit {co_name} in {city}. {person} plant die Ausweitung der Zusammenarbeit im Bereich {area}.",
        "Workshop zur Betrugsprävention im Bereich {area}. Identifikation neuer Auffälligkeitsmuster in {city}.",
        "Review der Durchlaufzeiten im Bereich {area}. {person} mahnt eine schnellere Bearbeitung an.",
        "Besprechung von komplexen Großschadenfällen im {area}. Strategiewechsel durch {person} empfohlen.",
        "Feedback-Gespräch: {person} lobt die Erreichbarkeit unserer Anwälte bei {area}-Anfragen.",
    ]

    for i in range(number_of_rows):
        # IMPORTANT: We pick a valid combination so reports match existing KPIs
        co, area = random.choice(active_combinations)

        dept = random.choice(["Schaden", "Recht", "Regress", "Compliance"])
        city = random.choice(["Berlin", "München", "Hamburg", "Köln"])
        person = (
            f"{fake.prefix()} {fake.last_name()}"
            if random.random() > 0.4
            else fake.name()
        )

        content = random.choice(report_templates).format(
            area=area.name, person=person, co_name=co.name, city=city
        )

        report = Report(
            insurance_company_id=co.id,
            practice_area_id=area.id,
            department_visited=dept,
            visited_key_personnel=person,
            report_date=fake.date_time_between(start_date="-2y", end_date="now"),
            report_content=f"ID: {random.randint(1000,9999)}\n---\n{content}",
        )
        session.add(report)

    session.commit()
    print("Database populated successfully.")


if __name__ == "__main__":
    populate_database(400)
