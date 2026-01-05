import os
import random

from dotenv import load_dotenv
from faker import Faker
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker

# Importiere deine Modelle (Pfade ggf. anpassen)
from database import KPI, Base, InsuranceCompany, PracticeArea, Report

# Setup
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
fake = Faker("de_DE")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


def clear_database():
    """Löscht alle vorhandenen Daten in der richtigen Reihenfolge."""
    print("Bereinige Datenbank...")
    session.execute(delete(Report))
    session.execute(delete(KPI))
    session.execute(delete(InsuranceCompany))
    session.execute(delete(PracticeArea))
    session.commit()


def populate_database(number_of_rows: int):
    # 1. Tabellen erstellen falls nicht existent
    Base.metadata.create_all(engine)
    clear_database()

    # 2. Fachbereiche (Practice Areas)
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
    session.commit()

    # 3. Versicherungen
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
    session.commit()

    # IDs neu laden
    companies = session.query(InsuranceCompany).all()
    p_areas = session.query(PracticeArea).all()

    # 4. KPI Daten generieren
    print("Generiere KPI Daten...")
    for co in companies:
        for area in random.sample(p_areas, k=random.randint(4, len(p_areas))):
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

    print(f"Generiere {number_of_rows} Reports...")
    departments = [
        "Schadenabteilung",
        "Rechtsabteilung",
        "Betrugsprävention",
        "Zentraler Regress",
        "Compliance",
        "Key Account",
    ]
    cities = [
        "Berlin",
        "München",
        "Hamburg",
        "Köln",
        "Frankfurt",
        "Stuttgart",
        "Hannover",
        "Düsseldorf",
    ]

    report_templates = [
        # Strategie & Akquise
        "Strategiemeeting mit {co_name} in {city}. {person} plant die Ausweitung der Zusammenarbeit im Bereich {area}.",
        "Vorstellung unserer neuen digitalen Schnittstelle in der {dept}. Ziel ist die papierlose Aktenübertragung bei {area}-Fällen.",
        "Pitch-Termin bei der {dept}. Diskussion über Pauschalhonorar-Modelle für standardisierte {area}-Verfahren.",
        "Marktanalyse mit {person}: Wettbewerbsvergleich der Schadenquoten im Segment {area}.",
        "Sondierungsgespräch über die Übernahme eines Altschaden-Portfolios im Bereich {area}.",
        "Diskussion über Kapazitätserweiterungen: {co_name} benötigt zusätzliche Ressourcen in der {dept}.",
        "Präsentation der Kanzlei-Erfolgsbilanz vor dem Vorstand. Fokus auf Kosteneinsparung bei {area}.",
        "Abstimmung über Key-Performance-Indikatoren (KPI) für das nächste Quartal mit {person}.",
        # Fachliches & Recht
        "Inhouse-Schulung für Sachbearbeiter der {dept}. Thema: 'Aktuelle Beweislastumkehr im {area}'.",
        "Sonderbericht zu einer Grundsatzentscheidung im {area}. {person} bittet um Einschätzung der Auswirkungen.",
        "Workshop zur Betrugsprävention im Bereich {area}. Identifikation neuer Auffälligkeitsmuster in {city}.",
        "Fachvortrag zum Thema 'Digitalisierung der Beweisaufnahme' im {area}. {person} war sehr interessiert.",
        "Update-Termin: Neue Richtlinien der BaFin zur Schadenregulierung im Bereich {area}.",
        "Deep-Dive-Session: Analyse der Rechtsprechung des OLG zur Kausalität im {area}.",
        "Erstellung eines Leitfadens für die {dept} zur Erstbewertung von {area}-Schäden.",
        "Diskussion über die Auswirkungen der neuen Gesetzesänderung auf laufende {area}-Mandate.",
        # Operatives & Controlling
        "Review der Durchlaufzeiten im Bereich {area}. {person} mahnt eine schnellere Bearbeitung an.",
        "Audit-Termin durch {co_name}. Die Prüfung der {dept} ergab eine exzellente Einhaltung der SLA.",
        "Besprechung von komplexen Großschadenfällen im {area}. Strategiewechsel durch {person} empfohlen.",
        "Qualitätskontrolle der Aktenführung in der {dept}. Keine nennenswerten Beanstandungen im {area}.",
        "Analyse der Prozessverluste im letzten Halbjahr. {person} fordert Ursachenforschung für {area}.",
        "Abstimmung der Vergleichs-Vollmachten: {co_name} erhöht das Limit für Vergleiche im {area}.",
        "Reporting-Termin: Vorstellung der Einsparungen durch konsequente Regressprüfung im {area}.",
        "Prüfung der Rückstellungsbildung für drohende Großschäden im {area} gemeinsam mit der {dept}.",
        # Beziehungsmanagement
        "Informeller Austausch mit {person} ({dept}) am Rande der Fachkonferenz in {city}.",
        "Jahresabschlussgespräch mit der Leitung der {dept}. Dank für die kompetente Vertretung im {area}.",
        "Klärung von Abrechnungsdifferenzen bei {co_name}. {person} bestätigt die Freigabe der Honorarnoten.",
        "Lunch-Termin mit {person}: Networking und Austausch über Markttrends in der {area}-Sparte.",
        "Besuch der neuen Räumlichkeiten der {dept}. Kurzes Update zu laufenden Projekten im {area}.",
        "Feedback-Gespräch: {person} lobt die Erreichbarkeit unserer Anwälte bei {area}-Anfragen.",
        "Teilnahme am Sommerfest von {co_name}. Vertiefung der Kontakte zur gesamten {dept}.",
        "Glückwünsche zur Beförderung von {person}. Neue Zuständigkeiten im Bereich {area}.",
        # Sonderfälle
        "Eilige Prüfung einer Deckungszusage für ein medienwirksames Verfahren im {area}.",
        "Task-Force-Meeting zur Bekämpfung organisierter Kriminalität im {area}-Sektor der {dept}.",
        "Unterstützung bei einer internen Revision von {co_name} bezüglich {area}-Prozessen.",
        "Ad-hoc-Einsatz wegen eines drohenden Reputationsschadens im Bereich {area}.",
        "Besprechung der Digitalisierungsstrategie 2026 für die Sparte {area} mit {person}.",
        "Vorbereitung einer Panel-Diskussion zum Thema {area} mit Vertretern der {dept}.",
        "Analyse von Deckungslücken in neuen Versicherungsprodukten der {co_name} ({area}).",
        "Quartals-Review der Prozesskostenentwicklung im Fachbereich {area}.",
    ]

    for i in range(number_of_rows):
        co = random.choice(companies)
        area = random.choice(p_areas)
        dept = random.choice(departments)
        city = random.choice(cities)
        person = (
            f"{fake.prefix()} {fake.last_name()}"
            if random.random() > 0.4
            else fake.name()
        )

        base_text = random.choice(report_templates).format(
            area=area.name, person=person, dept=dept, co_name=co.name, city=city
        )

        # Formatierung für mehr Realismus
        case_id = (
            f"{co.name[:2].upper()}-{random.randint(100, 999)}/{random.randint(23, 25)}"
        )
        full_content = f"Protokoll {case_id}\nOrt: {city} | Prio: {random.choice(['Normal', 'Hoch'])}\n---\n{base_text}"

        report = Report(
            insurance_company_id=co.id,
            practice_area_id=area.id,
            department_visited=dept,
            visited_key_personnel=person,
            report_date=fake.date_time_between(start_date="-2y", end_date="now"),
            report_content=full_content,
        )
        session.add(report)

        if i % 50 == 0:
            session.commit()

    session.commit()
    print(
        f"Fertig! Datenbank wurde mit {number_of_rows} Berichten und konsistenten IDs befüllt."
    )


if __name__ == "__main__":
    populate_database(400)
