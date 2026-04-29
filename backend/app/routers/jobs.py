"""
Jobs API Router
Job listings and AI-powered job recommendations.
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
import random
from ..auth_guards import require_auth

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"

_jobs: List[dict] = []
_applications: List[dict] = []
_initialized = False


class JobApplication(BaseModel):
    cover_letter: str = ""


def _load_employees():
    path = DATA_DIR / "employees.jsonl"
    employees = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    employees.append(json.loads(line))
    return employees


def _init_jobs():
    global _jobs, _initialized
    if _initialized:
        return

    job_listings = [
        # ── Technology & Engineering ──
        {"title": "Senior Full Stack Developer", "dept": "Engineering", "type": "Full-time", "level": "Senior",
         "desc": "Build scalable web applications using React, Node.js, and cloud technologies for high-impact projects.",
         "skills": ["React", "Node.js", "TypeScript", "AWS", "PostgreSQL"]},
        {"title": "Machine Learning Engineer", "dept": "AI Research", "type": "Full-time", "level": "Mid-Senior",
         "desc": "Develop and deploy production-grade ML models using state-of-the-art NLP and computer vision systems.",
         "skills": ["Python", "PyTorch", "TensorFlow", "MLOps", "Docker"]},
        {"title": "Data Scientist", "dept": "Data Science", "type": "Full-time", "level": "Mid",
         "desc": "Analyze complex datasets to drive business decisions. Build predictive models and data visualizations.",
         "skills": ["Python", "SQL", "Spark", "Statistics", "Tableau"]},
        {"title": "DevOps Engineer", "dept": "Cloud Infrastructure", "type": "Full-time", "level": "Mid-Senior",
         "desc": "Build CI/CD pipelines, manage cloud infrastructure, and ensure system reliability across platforms.",
         "skills": ["Docker", "Kubernetes", "Jenkins", "AWS", "Linux"]},

        # ── Healthcare & Medicine ──
        {"title": "Clinical Research Coordinator", "dept": "Healthcare", "type": "Full-time", "level": "Mid",
         "desc": "Coordinate clinical trials from start to finish, manage patient recruitment, ensure regulatory compliance, and maintain study documentation.",
         "skills": ["Clinical Trials", "GCP Compliance", "Patient Care", "Data Management", "Protocol Design"]},
        {"title": "Registered Nurse — ICU", "dept": "Healthcare", "type": "Full-time", "level": "Mid-Senior",
         "desc": "Provide critical care to patients in the intensive care unit. Monitor vital signs, administer treatments, and collaborate with physicians.",
         "skills": ["Patient Care", "Critical Care", "BLS/ACLS", "EMR Systems", "Team Collaboration"]},
        {"title": "Healthcare Data Analyst", "dept": "Healthcare", "type": "Full-time", "level": "Mid",
         "desc": "Analyze healthcare data to improve patient outcomes. Work with EHR systems, build dashboards, and identify trends in clinical data.",
         "skills": ["Healthcare Analytics", "SQL", "Tableau", "HIPAA", "Statistics"]},
        {"title": "Pharmacist", "dept": "Healthcare", "type": "Full-time", "level": "Senior",
         "desc": "Dispense medications, counsel patients on proper drug use, and collaborate with healthcare teams on optimal treatment plans.",
         "skills": ["Pharmacology", "Patient Counseling", "Drug Interactions", "Regulatory Compliance", "Clinical Knowledge"]},

        # ── Finance & Banking ──
        {"title": "Financial Analyst", "dept": "Finance", "type": "Full-time", "level": "Mid",
         "desc": "Analyze financial data, create forecasting models, and provide strategic recommendations to drive business growth and profitability.",
         "skills": ["Financial Modeling", "Excel", "Bloomberg", "Valuation", "Financial Reporting"]},
        {"title": "Investment Banking Associate", "dept": "Finance", "type": "Full-time", "level": "Mid-Senior",
         "desc": "Execute M&A transactions, perform due diligence, build financial models, and prepare pitch books for institutional clients.",
         "skills": ["M&A", "Financial Modeling", "Due Diligence", "Valuation", "Capital Markets"]},
        {"title": "Risk Manager", "dept": "Finance", "type": "Full-time", "level": "Senior",
         "desc": "Identify, assess, and mitigate financial risks. Develop risk frameworks, stress-test portfolios, and ensure regulatory compliance.",
         "skills": ["Risk Assessment", "Basel III", "VaR", "Stress Testing", "Regulatory Compliance"]},
        {"title": "Accountant (CPA)", "dept": "Finance", "type": "Full-time", "level": "Mid",
         "desc": "Manage financial statements, tax filings, and audit processes. Ensure compliance with GAAP and local tax regulations.",
         "skills": ["GAAP", "Tax Preparation", "Auditing", "QuickBooks", "Financial Reporting"]},

        # ── Marketing & Communications ──
        {"title": "Digital Marketing Manager", "dept": "Marketing", "type": "Full-time", "level": "Senior",
         "desc": "Lead digital marketing campaigns across SEO, SEM, social media, and email. Drive brand awareness and customer acquisition strategy.",
         "skills": ["SEO/SEM", "Google Analytics", "Social Media", "Content Strategy", "Campaign Management"]},
        {"title": "Content Strategist", "dept": "Marketing", "type": "Full-time", "level": "Mid",
         "desc": "Develop and execute content strategy across blog, social media, and web. Create compelling narratives that engage target audiences.",
         "skills": ["Content Creation", "SEO", "Copywriting", "Brand Storytelling", "CMS Platforms"]},
        {"title": "Public Relations Specialist", "dept": "Marketing", "type": "Full-time", "level": "Mid",
         "desc": "Manage media relations, write press releases, organize events, and build brand reputation through strategic communications.",
         "skills": ["Media Relations", "Press Releases", "Crisis Communication", "Event Planning", "Public Speaking"]},

        # ── Design & Creative ──
        {"title": "UX/UI Designer", "dept": "Design", "type": "Full-time", "level": "Mid",
         "desc": "Design intuitive, user-centered interfaces for web and mobile. Conduct user research, create wireframes, and build design systems.",
         "skills": ["Figma", "User Research", "Wireframing", "Prototyping", "Design Systems"]},
        {"title": "Graphic Designer", "dept": "Design", "type": "Full-time", "level": "Mid",
         "desc": "Create visual content for digital and print media. Design marketing materials, brand assets, and illustration packages.",
         "skills": ["Adobe Creative Suite", "Typography", "Brand Identity", "Illustration", "Layout Design"]},
        {"title": "3D Animator", "dept": "Design", "type": "Contract", "level": "Mid-Senior",
         "desc": "Create high-quality 3D animations for product visualization and marketing. Work with industry-leading tools and rendering pipelines.",
         "skills": ["Blender", "Maya", "3D Modeling", "Motion Graphics", "Rendering"]},

        # ── Legal ──
        {"title": "Corporate Lawyer", "dept": "Legal", "type": "Full-time", "level": "Senior",
         "desc": "Provide legal counsel on corporate transactions, contracts, and compliance matters. Manage litigation and regulatory affairs.",
         "skills": ["Corporate Law", "Contract Drafting", "Regulatory Compliance", "M&A", "Litigation"]},
        {"title": "Intellectual Property Paralegal", "dept": "Legal", "type": "Full-time", "level": "Mid",
         "desc": "Support IP attorneys with patent filings, trademark research, and legal documentation. Manage case files and deadlines.",
         "skills": ["IP Law", "Patent Filing", "Legal Research", "Case Management", "Documentation"]},

        # ── Education ──
        {"title": "Curriculum Designer", "dept": "Education", "type": "Full-time", "level": "Mid",
         "desc": "Design and develop learning programs and course curricula. Create engaging educational content aligned with learning outcomes.",
         "skills": ["Curriculum Design", "Instructional Design", "LMS Platforms", "Assessment Design", "Pedagogy"]},
        {"title": "University Lecturer — Mathematics", "dept": "Education", "type": "Full-time", "level": "Senior",
         "desc": "Teach undergraduate and graduate mathematics courses. Conduct research, mentor students, and publish academic papers.",
         "skills": ["Mathematics", "Research", "Teaching", "Academic Writing", "Student Mentoring"]},

        # ── Human Resources ──
        {"title": "HR Business Partner", "dept": "Human Resources", "type": "Full-time", "level": "Senior",
         "desc": "Partner with business leaders on workforce strategy, talent development, and organizational design. Drive HR initiatives across departments.",
         "skills": ["Talent Management", "Organizational Design", "Employee Relations", "HRIS", "Change Management"]},
        {"title": "Talent Acquisition Specialist", "dept": "Human Resources", "type": "Full-time", "level": "Mid",
         "desc": "Manage end-to-end recruitment. Source candidates, conduct interviews, and build talent pipelines across all business functions.",
         "skills": ["Recruiting", "Interviewing", "ATS Systems", "Employer Branding", "Sourcing"]},

        # ── Supply Chain & Operations ──
        {"title": "Supply Chain Manager", "dept": "Operations", "type": "Full-time", "level": "Senior",
         "desc": "Optimize end-to-end supply chain operations. Manage vendor relationships, logistics, and inventory across global markets.",
         "skills": ["Supply Chain Management", "Logistics", "SAP", "Inventory Management", "Vendor Relations"]},
        {"title": "Operations Analyst", "dept": "Operations", "type": "Full-time", "level": "Mid",
         "desc": "Analyze operational processes, identify inefficiencies, and implement improvements. Work cross-functionally to streamline workflows.",
         "skills": ["Process Improvement", "Data Analysis", "Lean Six Sigma", "Excel", "Project Management"]},

        # ── Architecture & Civil Engineering ──
        {"title": "Architect — Sustainable Design", "dept": "Architecture", "type": "Full-time", "level": "Senior",
         "desc": "Design sustainable, energy-efficient buildings and urban spaces. Lead LEED-certified projects from concept to construction documentation.",
         "skills": ["AutoCAD", "Revit", "LEED Certification", "Sustainable Design", "Building Codes"]},
        {"title": "Civil Engineer", "dept": "Engineering", "type": "Full-time", "level": "Mid",
         "desc": "Design and supervise construction of infrastructure projects including roads, bridges, and water treatment facilities.",
         "skills": ["Structural Analysis", "AutoCAD", "Project Management", "Geotechnical Engineering", "Construction"]},

        # ── Biotech & Pharmaceutical ──
        {"title": "Biotech Research Scientist", "dept": "Biotechnology", "type": "Full-time", "level": "Mid-Senior",
         "desc": "Conduct research in molecular biology and genomics. Design experiments, analyze data, and contribute to drug discovery pipelines.",
         "skills": ["Molecular Biology", "Genomics", "CRISPR", "Bioinformatics", "Lab Techniques"]},

        # ── Media & Journalism ──
        {"title": "Investigative Journalist", "dept": "Media", "type": "Full-time", "level": "Mid-Senior",
         "desc": "Research and report on in-depth stories of public interest. Conduct interviews, verify sources, and produce compelling multimedia content.",
         "skills": ["Investigative Reporting", "Research", "Interviewing", "AP Style Writing", "Multimedia Production"]},

        # ── Consulting ──
        {"title": "Management Consultant", "dept": "Consulting", "type": "Full-time", "level": "Mid-Senior",
         "desc": "Advise organizations on strategy, operations, and transformation. Conduct market analysis and deliver actionable recommendations.",
         "skills": ["Strategy", "Business Analysis", "PowerPoint", "Financial Modeling", "Client Management"]},

        # ── Hospitality & Tourism ──
        {"title": "Hotel General Manager", "dept": "Hospitality", "type": "Full-time", "level": "Manager",
         "desc": "Oversee all hotel operations including front desk, housekeeping, F&B, and guest services. Maximize revenue and guest satisfaction.",
         "skills": ["Hotel Management", "Revenue Management", "Guest Relations", "Staff Leadership", "P&L Management"]},

        # ── Environmental Science ──
        {"title": "Environmental Scientist", "dept": "Environmental Science", "type": "Full-time", "level": "Mid",
         "desc": "Conduct environmental impact assessments, monitor pollution levels, and develop sustainability strategies for industrial projects.",
         "skills": ["Environmental Impact Assessment", "GIS", "Field Research", "Sustainability", "Regulatory Compliance"]},

        # ── Product & Business ──
        {"title": "Product Manager", "dept": "Product Development", "type": "Full-time", "level": "Senior",
         "desc": "Define product vision, prioritize roadmap, and work with cross-functional teams to deliver features that delight users.",
         "skills": ["Product Strategy", "Analytics", "Agile", "User Research", "Communication"]},
        {"title": "Business Development Manager", "dept": "Business Development", "type": "Full-time", "level": "Senior",
         "desc": "Identify new market opportunities, build strategic partnerships, and drive revenue growth across key business segments.",
         "skills": ["Business Strategy", "Negotiation", "Sales", "Market Analysis", "Partnership Management"]},
    ]

    locations = ["San Francisco, CA", "New York, NY", "London, UK", "Berlin, Germany", "Remote",
                 "Toronto, Canada", "Paris, France", "Singapore", "Dubai, UAE", "Tokyo, Japan",
                 "Sydney, Australia", "Mumbai, India", "São Paulo, Brazil", "Amsterdam, Netherlands"]

    # Load companies dynamically from JSONL
    companies_path = DATA_DIR / "companies.jsonl"
    companies_list = []
    if companies_path.exists():
        with open(companies_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    companies_list.append(json.loads(line))

    # Fallback if JSONL missing
    if not companies_list:
        companies_list = [
            {"id": f"comp_{i:03d}", "name": n, "industry": "Technology", "rating": 4.0, "size": "Medium"}
            for i, n in enumerate(["ExpertLink", "TechNova", "MedCore", "FinanceHub",
                                    "GreenBuild", "EduVerse", "BioGenix", "CloudScale"], 1)
        ]

    now = datetime.utcnow()

    for i, job in enumerate(job_listings):
        company = random.choice(companies_list)
        _jobs.append({
            "id": str(uuid.uuid4()),
            "title": job["title"],
            "company": company.get("name"),
            "company_id": company.get("id"),
            "company_industry": company.get("industry"),
            "company_rating": company.get("rating"),
            "company_size": company.get("size"),
            "department": job["dept"],
            "location": random.choice(locations),
            "type": job["type"],
            "level": job["level"],
            "description": job["desc"],
            "required_skills": job["skills"],
            "salary_range": f"${random.randint(60, 150)}K - ${random.randint(150, 250)}K",
            "posted_at": (now - timedelta(days=random.randint(1, 30))).isoformat(),
            "applicants": random.randint(15, 200),
            "is_promoted": i < 2,
            "easy_apply": random.choice([True, True, False]),
        })

    _initialized = True


@router.get("")
async def get_jobs(
    department: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    level: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 20,
):
    _init_jobs()
    results = _jobs.copy()

    if department:
        results = [j for j in results if department.lower() in j["department"].lower()]
    if location:
        results = [j for j in results if location.lower() in j["location"].lower()]
    if job_type:
        results = [j for j in results if j["type"].lower() == job_type.lower()]
    if level:
        results = [j for j in results if level.lower() in j["level"].lower()]
    if q:
        q_lower = q.lower()
        results = [j for j in results if q_lower in j["title"].lower() or q_lower in j["description"].lower()
                    or any(q_lower in s.lower() for s in j["required_skills"])]

    return {"jobs": results[:limit], "total": len(results)}


@router.get("/recommended")
async def get_recommended_jobs(_user: dict = Depends(require_auth)):
    _init_jobs()
    # Return top 5 jobs shuffled
    recommended = random.sample(_jobs, min(5, len(_jobs)))
    return {"jobs": recommended}


@router.get("/{job_id}")
async def get_job(job_id: str, _user: dict = Depends(require_auth)):
    _init_jobs()
    for job in _jobs:
        if job["id"] == job_id:
            return job
    return {"error": "Job not found"}


@router.post("/{job_id}/apply")
async def apply_to_job(job_id: str, application: JobApplication, _user: dict = Depends(require_auth)):
    _init_jobs()
    for job in _jobs:
        if job["id"] == job_id:
            app = {
                "id": str(uuid.uuid4()),
                "job_id": job_id,
                "job_title": job["title"],
                "applied_at": datetime.utcnow().isoformat(),
                "status": "submitted",
                "cover_letter": application.cover_letter,
            }
            _applications.append(app)
            return {"status": "applied", "application": app}
    return {"error": "Job not found"}


@router.get("/companies")
async def get_job_companies(industry: str = None, _user: dict = Depends(require_auth)):
    """All companies available for job listings."""
    companies_path = DATA_DIR / "companies.jsonl"
    companies = []
    if companies_path.exists():
        with open(companies_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    companies.append(json.loads(line))
    if industry:
        companies = [c for c in companies if c.get("industry", "").lower() == industry.lower()]
    return {"companies": companies, "total": len(companies)}
