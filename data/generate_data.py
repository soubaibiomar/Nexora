"""
Scalable Data Generator for Nexora / ExpertLink
Generates comprehensive, realistic content for the knowledge platform.

Usage:
    python generate_data.py                  # default (medium)
    python generate_data.py --scale small    # 100 employees
    python generate_data.py --scale medium   # 500 employees
    python generate_data.py --scale large    # 2000 employees
"""

import argparse
import json
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────

FIRST_NAMES = [
    "Alexandre", "Marie", "Thomas", "Sophie", "Pierre", "Julie", "Nicolas", "Camille",
    "Antoine", "Emma", "Lucas", "Léa", "Mathieu", "Chloé", "David", "Sarah",
    "Julien", "Laura", "Sébastien", "Manon", "François", "Alice", "Baptiste", "Clara",
    "Guillaume", "Lucie", "Romain", "Anaïs", "Maxime", "Pauline", "Olivier", "Marion",
    "Vincent", "Louise", "Jérôme", "Margot", "Laurent", "Justine", "Benjamin", "Charlotte",
    "Michaël", "Amandine", "Christophe", "Nadia", "Yannick", "Fatima", "Malik", "Aisha",
    "James", "Emily", "Robert", "Jennifer", "Michael", "Jessica", "John", "Elizabeth",
    "William", "Lisa", "Daniel", "Amanda", "Christopher", "Rachel", "Kevin", "Michelle",
    "Omar", "Yuki", "Wei", "Priya", "Carlos", "Ingrid", "Hans", "Mei",
    "Ravi", "Olga", "Tariq", "Elena", "Noah", "Liam", "Ava", "Mia",
    "Ethan", "Sophia", "Isabella", "Olivia", "Aiden", "Harper", "Mason", "Ella",
    "Ahmed", "Leila", "Dmitri", "Svetlana", "Jorge", "Ana", "Kenji", "Haruki",
]

LAST_NAMES = [
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand",
    "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel", "Garcia", "David",
    "Bertrand", "Roux", "Vincent", "Fournier", "Morel", "Girard", "André", "Mercier",
    "Dupont", "Lambert", "Bonnet", "François", "Martinez", "Nguyen", "Chen", "Kim",
    "López", "Smith", "Johnson", "Williams", "Brown", "Jones", "Wilson", "Taylor",
    "Anderson", "Thompson", "White", "Harris", "Clark", "Lewis", "Young", "Walker",
    "Patel", "Singh", "Müller", "Schmidt", "Fischer", "Weber", "Suzuki", "Tanaka",
    "Ivanov", "Petrov", "Santos", "Oliveira", "Johansson", "Nielsen", "Kowalski", "Novak",
]

DEPARTMENTS = [
    "Engineering", "Data Science", "DevOps", "Security", "Cloud Infrastructure",
    "AI Research", "Web Development", "Mobile Development", "Quality Assurance",
    "Platform Engineering", "Machine Learning", "Architecture", "Product Development",
    "Backend Engineering", "Frontend Engineering", "Infrastructure", "SRE",
]

ROLES = [
    "Junior Developer", "Senior Developer", "Lead Developer", "Tech Lead",
    "Software Architect", "Data Scientist", "ML Engineer", "DevOps Engineer",
    "Security Engineer", "Cloud Architect", "Full Stack Developer", "Backend Developer",
    "Frontend Developer", "Principal Engineer", "Staff Engineer", "Engineering Manager",
    "Research Scientist", "Platform Engineer", "SRE", "Solutions Architect",
    "Data Engineer", "QA Engineer", "Technical Writer", "Product Manager",
]

LOCATIONS = [
    "Paris, France", "Lyon, France", "Marseille, France", "Bordeaux, France",
    "Toulouse, France", "Nantes, France", "Strasbourg, France", "Lille, France",
    "London, UK", "Berlin, Germany", "Amsterdam, Netherlands", "Dublin, Ireland",
    "Brussels, Belgium", "Geneva, Switzerland", "Barcelona, Spain", "Milan, Italy",
    "New York, USA", "San Francisco, USA", "Toronto, Canada", "Singapore",
    "Tokyo, Japan", "Sydney, Australia", "Dubai, UAE", "São Paulo, Brazil",
    "Stockholm, Sweden", "Copenhagen, Denmark", "Oslo, Norway", "Helsinki, Finland",
]

# ── Skill category with (name, level_label, demand_score) ─────────

SKILL_CATEGORIES = {
    "Programming Languages": [
        ("Python", "Advanced", 95), ("JavaScript", "Advanced", 92), ("TypeScript", "Advanced", 88),
        ("Java", "Advanced", 85), ("Go", "Intermediate", 75), ("Rust", "Intermediate", 65),
        ("C++", "Advanced", 60), ("C#", "Advanced", 70), ("Ruby", "Intermediate", 45),
        ("PHP", "Intermediate", 50), ("Kotlin", "Intermediate", 55), ("Swift", "Intermediate", 52),
        ("Scala", "Intermediate", 48), ("R", "Intermediate", 42),
    ],
    "Frameworks": [
        ("React", "Advanced", 90), ("Vue.js", "Advanced", 70), ("Angular", "Advanced", 65),
        ("Django", "Advanced", 75), ("FastAPI", "Intermediate", 80), ("Spring Boot", "Advanced", 70),
        ("Node.js", "Advanced", 88), ("Next.js", "Advanced", 82), ("Flask", "Intermediate", 65),
        ("Express.js", "Advanced", 75), ("NestJS", "Intermediate", 60), ("Rails", "Intermediate", 45),
        ("Svelte", "Intermediate", 40), ("Flutter", "Intermediate", 58),
    ],
    "Cloud Platforms": [
        ("AWS", "Advanced", 92), ("Azure", "Advanced", 85), ("Google Cloud", "Advanced", 78),
        ("Kubernetes", "Advanced", 88), ("Docker", "Advanced", 95), ("Terraform", "Advanced", 82),
        ("AWS Lambda", "Intermediate", 75), ("Azure Functions", "Intermediate", 65),
        ("CloudFormation", "Intermediate", 55), ("Pulumi", "Beginner", 35),
    ],
    "Data & AI": [
        ("TensorFlow", "Advanced", 80), ("PyTorch", "Advanced", 82), ("Scikit-learn", "Advanced", 75),
        ("Pandas", "Advanced", 90), ("NumPy", "Advanced", 88), ("Spark", "Intermediate", 70),
        ("Kafka", "Intermediate", 65), ("Elasticsearch", "Advanced", 72), ("MongoDB", "Advanced", 78),
        ("PostgreSQL", "Advanced", 85), ("Redis", "Advanced", 80), ("GraphQL", "Intermediate", 68),
        ("Neo4j", "Intermediate", 60), ("Airflow", "Intermediate", 55),
        ("Hugging Face", "Intermediate", 72), ("LangChain", "Intermediate", 68),
        ("MLflow", "Intermediate", 50), ("dbt", "Intermediate", 48),
    ],
    "DevOps & Tools": [
        ("Git", "Advanced", 98), ("Jenkins", "Advanced", 75), ("GitLab CI", "Advanced", 80),
        ("GitHub Actions", "Advanced", 85), ("Ansible", "Intermediate", 65), ("Prometheus", "Intermediate", 70),
        ("Grafana", "Intermediate", 72), ("ArgoCD", "Intermediate", 55), ("Helm", "Intermediate", 60),
        ("Datadog", "Intermediate", 62), ("New Relic", "Intermediate", 50),
    ],
    "Security": [
        ("OWASP", "Advanced", 70), ("Penetration Testing", "Intermediate", 55),
        ("Security Auditing", "Intermediate", 60), ("IAM", "Advanced", 75),
        ("Encryption", "Advanced", 80), ("Network Security", "Intermediate", 65),
        ("Zero Trust", "Intermediate", 58), ("SOC 2", "Intermediate", 52),
    ],
}

# Department → likely skill categories mapping for realistic assignment
DEPT_SKILL_AFFINITY = {
    "Engineering":          ["Programming Languages", "Frameworks", "DevOps & Tools"],
    "Data Science":         ["Data & AI", "Programming Languages"],
    "DevOps":               ["DevOps & Tools", "Cloud Platforms"],
    "Security":             ["Security", "DevOps & Tools"],
    "Cloud Infrastructure": ["Cloud Platforms", "DevOps & Tools"],
    "AI Research":          ["Data & AI", "Programming Languages"],
    "Web Development":      ["Frameworks", "Programming Languages"],
    "Mobile Development":   ["Frameworks", "Programming Languages"],
    "Quality Assurance":    ["DevOps & Tools", "Frameworks"],
    "Platform Engineering": ["Cloud Platforms", "DevOps & Tools", "Programming Languages"],
    "Machine Learning":     ["Data & AI", "Programming Languages"],
    "Architecture":         ["Cloud Platforms", "Programming Languages", "Frameworks"],
    "Product Development":  ["Frameworks", "Programming Languages"],
    "Backend Engineering":  ["Programming Languages", "Data & AI", "DevOps & Tools"],
    "Frontend Engineering": ["Frameworks", "Programming Languages"],
    "Infrastructure":       ["Cloud Platforms", "DevOps & Tools"],
    "SRE":                  ["DevOps & Tools", "Cloud Platforms"],
}

# ── Document templates ─────────────────────────────────────────────

DOC_TOPICS = {
    "DevOps": [
        "CI/CD Pipeline Best Practices", "Kubernetes Deployment Strategies",
        "Infrastructure as Code with Terraform", "Docker Security and Optimization",
        "GitOps Workflow Implementation", "Monitoring with Prometheus and Grafana",
        "Microservices Deployment Patterns", "Ansible Configuration Management",
        "Container Orchestration", "Zero-Downtime Deployment",
    ],
    "Machine Learning": [
        "Deep Learning with TensorFlow and PyTorch", "NLP Fundamentals",
        "Computer Vision with CNNs", "Feature Engineering Best Practices",
        "MLOps and Model Deployment", "Reinforcement Learning Applications",
        "Time Series Forecasting with LSTMs", "Transfer Learning for Classification",
        "Ensemble Methods and Stacking", "Neural Network Optimization",
    ],
    "Cloud": [
        "AWS Architecture for Scale", "Multi-Cloud Strategy",
        "Serverless with Lambda and Azure Functions", "Cloud Cost Optimization",
        "Hybrid Cloud Design", "Cloud Security Framework",
        "EKS vs AKS vs GKE", "Database Migration to Cloud",
        "Cloud Networking and VPC", "Auto-scaling Patterns",
    ],
    "Security": [
        "OWASP Application Security", "Zero Trust Architecture",
        "Penetration Testing Methodology", "IAM Best Practices",
        "Secure Coding for Developers", "Incident Response Guide",
        "Network Firewall Configuration", "Encryption Key Management",
        "Vulnerability Assessment", "SOC Setup Guide",
    ],
    "Web Development": [
        "Modern React with Hooks and Context", "Full-Stack Node.js Development",
        "Progressive Web Apps", "RESTful API Design",
        "Frontend Performance Optimization", "TypeScript at Scale",
        "State Management Patterns", "Next.js SSR Guide",
        "GraphQL API Development", "Responsive CSS Grid Layouts",
    ],
    "AI": [
        "LLM Fine-tuning and Deployment", "Generative AI Applications",
        "AI Ethics and Responsible Development", "Chatbot Development",
        "Computer Vision in Industry", "Recommendation Systems",
        "Speech Recognition and Synthesis", "AI Document Processing",
        "Predictive Analytics with AI", "Edge AI and Mobile ML",
    ],
}

PROJECT_DOMAINS = [
    "E-Commerce Platform", "Healthcare System", "Financial Services", "Education Platform",
    "IoT Platform", "Logistics System", "Media Streaming", "Social Network",
    "CRM System", "Supply Chain", "HR Management", "Analytics Dashboard",
    "Real-time Collaboration", "Marketplace", "Insurance Platform", "Gaming Backend",
    "Smart City Platform", "Autonomous Vehicles", "Digital Banking", "Telemedicine",
]

PROJECT_TECH_STACKS = [
    ["React", "Node.js", "PostgreSQL", "AWS"],
    ["Vue.js", "Python", "MongoDB", "Google Cloud"],
    ["Angular", "Java", "MySQL", "Azure"],
    ["Next.js", "FastAPI", "Redis", "Kubernetes"],
    ["React", "Go", "Cassandra", "AWS"],
    ["Flutter", "Django", "PostgreSQL", "Docker"],
    ["Svelte", "Rust", "ScyllaDB", "Kubernetes"],
    ["React", "GraphQL", "Neo4j", "AWS"],
    ["TypeScript", "NestJS", "PostgreSQL", "Google Cloud"],
    ["Python", "FastAPI", "Elasticsearch", "Docker"],
]


# ── Scale presets ──────────────────────────────────────────────────

SCALE = {
    "small":  {"employees": 100,  "documents": 200,  "projects": 50,  "seed": 42},
    "medium": {"employees": 500,  "documents": 500,  "projects": 120, "seed": 42},
    "large":  {"employees": 2000, "documents": 1000, "projects": 300, "seed": 42},
}


# ── Generators ─────────────────────────────────────────────────────

def _deterministic_hash(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest(), 16)


def generate_skills():
    """Generate skill records from predefined categories."""
    skills = []
    sid = 1
    for category, items in SKILL_CATEGORIES.items():
        for name, level, demand in items:
            skills.append({
                "id": f"skill_{sid}",
                "name": name,
                "category": category,
                "level": level,
                "demand": demand,
            })
            sid += 1
    return skills


def _pick_skills_for_employee(department: str, experience: int, all_skills: list) -> list:
    """Assign realistic skills to an employee based on department and experience."""
    affinities = DEPT_SKILL_AFFINITY.get(department, ["Programming Languages"])
    
    # Primary skills from affinity categories
    primary_pool = [s for s in all_skills if s["category"] in affinities]
    other_pool = [s for s in all_skills if s["category"] not in affinities]
    
    # More experienced → more skills
    n_primary = min(len(primary_pool), random.randint(3, 4 + experience // 3))
    n_secondary = min(len(other_pool), random.randint(1, 2 + experience // 5))
    
    chosen = random.sample(primary_pool, n_primary) + random.sample(other_pool, n_secondary)
    
    result = []
    for s in chosen:
        # Level correlated with experience
        level = min(5, max(1, experience // 4 + random.randint(0, 2)))
        result.append({"name": s["name"], "level": level})
    
    return result


def generate_employees(count: int, all_skills: list):
    """Generate realistic employee records with embedded skills."""
    employees = []
    used_emails = set()
    
    for i in range(1, count + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        
        # Ensure unique email
        base_email = f"{first.lower()}.{last.lower()}@nexora.io"
        email = base_email
        suffix = 1
        while email in used_emails:
            email = f"{first.lower()}.{last.lower()}{suffix}@nexora.io"
            suffix += 1
        used_emails.add(email)
        
        department = random.choice(DEPARTMENTS)
        experience = random.randint(1, 20)
        expertise = min(5, max(1, experience // 4 + random.randint(0, 2)))
        hire_date = datetime.now() - timedelta(days=random.randint(30, 365 * 10))
        
        skills = _pick_skills_for_employee(department, experience, all_skills)
        
        employees.append({
            "id": f"emp_{i}",
            "name": name,
            "email": email,
            "department": department,
            "role": random.choice(ROLES),
            "location": random.choice(LOCATIONS),
            "hire_date": hire_date.strftime("%Y-%m-%d"),
            "experience_years": experience,
            "expertise_level": expertise,
            "skills": skills,
        })
    return employees


def generate_documents(count: int, employees: list):
    """Generate realistic document records with content."""
    documents = []
    topics = list(DOC_TOPICS.keys())
    doc_types = ["Guide", "Tutorial", "Case Study", "Documentation", "Report",
                 "Article", "Whitepaper", "Best Practice", "Reference"]
    
    for i in range(1, count + 1):
        topic = random.choice(topics)
        titles = DOC_TOPICS[topic]
        title = random.choice(titles)
        doc_type = random.choice(doc_types)
        title = f"{title} — {doc_type} #{i}"
        
        overview = f"Comprehensive {doc_type.lower()} covering {topic.lower()} concepts, best practices, and real-world implementation strategies."
        content = f"Overview\n--------\n{overview}\n\nKey Concepts\n------------\n- Core principles of {topic}\n- Implementation patterns and anti-patterns\n- Performance considerations and benchmarks\n- Security implications and mitigations\n\nWalkthrough\n-----------\n1) Understand the fundamentals\n2) Set up the development environment\n3) Implement the solution step by step\n4) Test and validate results\n5) Deploy to production"
        
        author = random.choice(employees)["id"]
        date = (datetime.now() - timedelta(days=random.randint(1, 365 * 3))).strftime("%Y-%m-%d")
        
        documents.append({
            "id": f"doc_{i}",
            "title": title,
            "type": doc_type,
            "topic": topic,
            "content": content,
            "abstract": overview,
            "author": author,
            "date": date,
            "views": random.randint(50, 15000),
            "rating": round(random.uniform(3.0, 5.0), 1),
        })
    return documents


def generate_projects(count: int, employees: list):
    """Generate realistic project records with team members and required skills."""
    projects = []
    statuses = ["Active", "Completed", "Planning", "On Hold"]
    priorities = ["High", "Medium", "Low", "Critical"]
    
    for i in range(1, count + 1):
        domain = random.choice(PROJECT_DOMAINS)
        tech_stack = random.choice(PROJECT_TECH_STACKS)
        start_date = datetime.now() - timedelta(days=random.randint(-180, 365 * 2))
        team_size = random.randint(3, 12)
        team = [e["id"] for e in random.sample(employees, min(team_size, len(employees)))]
        
        projects.append({
            "id": f"proj_{i}",
            "name": f"{domain} — Phase {random.randint(1, 5)}",
            "domain": domain,
            "tech_stack": ", ".join(tech_stack),
            "required_skills": tech_stack,
            "date": start_date.strftime("%Y-%m-%d"),
            "status": random.choice(statuses),
            "budget": random.randint(50000, 5000000),
            "priority": random.choice(priorities),
            "team_members": team,
            "team_size": len(team),
        })
    return projects


# ── I/O ────────────────────────────────────────────────────────────

def save_jsonl(data: list, filepath: Path):
    with open(filepath, "w", encoding="utf-8") as f:
        for record in data:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"  ✓ {len(data):>5} records → {filepath.name}")


# ── Main ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate Nexora dataset")
    parser.add_argument("--scale", choices=["small", "medium", "large"], default="medium",
                        help="Dataset size preset (default: medium)")
    args = parser.parse_args()

    cfg = SCALE[args.scale]
    random.seed(cfg["seed"])
    out = Path(__file__).parent

    print(f"\n🚀 Generating Nexora dataset — scale={args.scale}")
    print(f"   Employees: {cfg['employees']}, Documents: {cfg['documents']}, Projects: {cfg['projects']}\n")

    skills = generate_skills()
    employees = generate_employees(cfg["employees"], skills)
    documents = generate_documents(cfg["documents"], employees)
    projects = generate_projects(cfg["projects"], employees)

    save_jsonl(skills, out / "skills.jsonl")
    save_jsonl(employees, out / "employees.jsonl")
    save_jsonl(documents, out / "documents.jsonl")
    save_jsonl(projects, out / "projects.jsonl")

    print(f"\n✅ Done! {len(skills)} skills, {len(employees)} employees, {len(documents)} documents, {len(projects)} projects")


if __name__ == "__main__":
    main()
