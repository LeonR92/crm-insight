import os
import random

from dotenv import load_dotenv
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import KPI, Base, InsuranceCompany, PracticeArea, Report

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
# Configuration
fake = Faker("de_DE")


engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


def populate_database():
    # 1. Create Tables
    Base.metadata.create_all(engine)

    # 2. Populate Practice Areas (5)
    practice_names = [
        "Verkehrsrecht",
        "Haftpflichtrecht",
        "Versicherungsbetrug",
        "Personenschaden",
        "Sachversicherungsrecht",
    ]
    p_areas = [PracticeArea(name=name) for name in practice_names]
    session.add_all(p_areas)
    session.commit()

    # 3. Populate Insurance Companies (10)
    # Using real-sounding German insurance names
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
    ]
    companies = [InsuranceCompany(name=name) for name in insurance_names]
    session.add_all(companies)
    session.commit()

    # 4. Populate KPI Data (10 rows)
    for _ in range(10):
        kpi = KPI(
            insurance_company_id=random.choice(companies).id,
            practice_area_id=random.choice(p_areas).id,
            incoming_fees=random.randint(5000, 50000),
            fees_collected=random.randint(4000, 45000),
            new_mandates=random.randint(5, 100),
        )
        session.add(kpi)

    # 5. Populate Reports (20 rows) with meaningful content
    departments = [
        "Schadenabteilung",
        "Rechtsabteilung",
        "Betrugsprävention",
        "Key Account Management",
    ]

    report_templates = [
        "Besprechung der aktuellen Schadenquote im Bereich {area}. Optimierungspotenzial bei Prozesslaufzeiten identifiziert.",
        "Vorstellung der neuen Legal-Tech-Lösung zur automatisierten Deckungsprüfung. Feedback von {person} war sehr positiv.",
        "Review-Termin zu laufenden Großschadenfällen. Strategiewechsel bei Fall {num} beschlossen.",
        "Schulung der Sachbearbeiter in der Abteilung {dept} zu aktuellen Urteilen des BGH im {area}.",
        "Quartalsmeeting zur Analyse der Regressmöglichkeiten. Fokus auf Subrogation im Bereich {area}.",
    ]

    for _ in range(20):
        selected_area = random.choice(p_areas)
        person = fake.name()
        dept = random.choice(departments)

        content = random.choice(report_templates).format(
            area=selected_area.name,
            person=person,
            dept=dept,
            num=random.randint(1000, 9999),
        )

        report = Report(
            insurance_company_id=random.choice(companies).id,
            practice_area_id=selected_area.id,
            department_visited=dept,
            visited_key_personnel=person,
            report_date=fake.date_time_between(start_date="-1y", end_date="now"),
            report_content=content,
        )
        session.add(report)

    session.commit()
    print("Database populated successfully with German insurance data.")


if __name__ == "__main__":
    populate_database()
