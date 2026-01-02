from sqlalchemy import DateTime, create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session, relationship
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

Base = declarative_base()

class InsuranceCompany(Base):
    __tablename__ = 'insurance_companies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class PracticeArea(Base):
    __tablename__ = 'practice_areas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class KPI(Base):
    __tablename__ = 'kpis'
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    insurance_company_id = Column(Integer, ForeignKey('insurance_companies.id'), nullable=False)
    practice_area_id = Column(Integer, ForeignKey('practice_areas.id'), nullable=False)
    
    incoming_fees = Column(Integer, nullable=False)
    fees_collected = Column(Integer, nullable=False)
    new_mandates = Column(Integer, nullable=False)

    insurance_company = relationship("InsuranceCompany", backref="kpis")
    practice_area = relationship("PracticeArea", backref="kpis")

class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    insurance_company_id = Column(Integer, ForeignKey('insurance_companies.id'), nullable=False)
    practice_area_id = Column(Integer, ForeignKey('practice_areas.id'), nullable=False)
    
    department_visited = Column(String, nullable=False)
    visited_key_personnel = Column(String, nullable=False)
    report_date = Column(DateTime, nullable=False) 
    report_content = Column(String, nullable=False)

    insurance_company = relationship("InsuranceCompany", backref="reports")
    practice_area = relationship("PracticeArea", backref="reports")