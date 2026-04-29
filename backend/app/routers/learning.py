import json
import re
from pathlib import Path
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from ..database import get_db
from ..auth_guards import require_auth

router = APIRouter(prefix="/api/learning", tags=["learning"])

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


def _load_skills_from_jsonl() -> List[str]:
    """Load clean skill names from skills.jsonl as fallback."""
    path = DATA_DIR / "skills.jsonl"
    skills = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    name = record.get("name", "")
                    if name:
                        skills.append(name)
    return sorted(set(skills))


def _clean_skill_name(name: str) -> str:
    """Strip trailing numeric IDs from skill names (e.g. 'Advanced AI/ML 1009' -> 'Advanced AI/ML')."""
    return re.sub(r'\s+\d+$', '', name).strip()


class LearningPathRequest(BaseModel):
    current_skills: List[str]
    target_skill: str


class LearningStep(BaseModel):
    skill: str
    level: str
    estimated_hours: int
    resources: List[dict]
    mentors: List[dict]
    type: Optional[str] = None
    description: Optional[str] = None
    objectives: Optional[List[str]] = None
    key_topics: Optional[List[str]] = None


def _default_skill_meta(skill: str, level: str) -> dict:
    """Generate generic rich metadata for any skill."""
    hours = 20 if level != "Advanced" else 40
    return {
        "hours": hours,
        "description": f"Build solid expertise in {skill}. This module covers core concepts, "
                       f"hands-on exercises, and real-world projects to prepare you for professional-level work.",
        "objectives": [
            f"Understand the fundamental principles and architecture of {skill}",
            f"Build real-world projects using {skill} best practices",
            f"Debug and optimize {skill} applications effectively",
            f"Prepare for technical interviews on {skill}",
        ],
        "key_topics": [
            "Core Concepts & Fundamentals",
            "Hands-On Project Development",
            "Best Practices & Patterns",
            "Testing & Debugging",
            "Performance Optimization",
        ],
        "resources": [
            {"id": f"res_{skill}_1", "title": f"{skill} - The Complete Guide", "type": "Course", "rating": 4.8},
            {"id": f"res_{skill}_2", "title": f"Advanced {skill} Patterns & Best Practices", "type": "Tutorial", "rating": 4.6},
            {"id": f"res_{skill}_3", "title": f"{skill} Project-Based Learning", "type": "Workshop", "rating": 4.7},
        ],
        "mentors": [
            {"id": f"mentor_{skill}_1", "name": "Dr. Sarah Chen", "level": 5, "department": "Engineering"},
            {"id": f"mentor_{skill}_2", "name": "Alex Rivera", "level": 4, "department": "R&D"},
        ],
    }


def _build_skill_metadata() -> dict:
    """Build a curated catalog of rich skill metadata."""
    catalog = {
        "Python": {
            "hours": 35,
            "description": "Master Python from data structures to advanced OOP, async programming, "
                           "and ecosystem tools. Covers web development, automation, and data science applications.",
            "objectives": [
                "Write idiomatic Python code following PEP 8 standards",
                "Build web APIs with Flask/FastAPI and async frameworks",
                "Work with data analysis libraries (Pandas, NumPy)",
                "Implement design patterns and testing strategies",
            ],
            "key_topics": ["Data Structures & Algorithms", "OOP & Design Patterns", "Async/Await & Concurrency",
                           "Web Frameworks (Flask/FastAPI)", "Testing with Pytest"],
            "resources": [
                {"id": "py1", "title": "Python 3 Complete Masterclass", "type": "Course", "rating": 4.9},
                {"id": "py2", "title": "Automate the Boring Stuff with Python", "type": "Book", "rating": 4.8},
                {"id": "py3", "title": "Python Design Patterns & Best Practices", "type": "Tutorial", "rating": 4.7},
            ],
            "mentors": [
                {"id": "m_py1", "name": "Dr. Sarah Chen", "level": 5, "department": "Data Science"},
                {"id": "m_py2", "name": "Michael Torres", "level": 4, "department": "Backend Engineering"},
            ],
        },
        "JavaScript": {
            "hours": 30,
            "description": "Deep-dive into modern JavaScript (ES2024+), covering async patterns, closures, "
                           "prototypes, event loop, modules, and full-stack development.",
            "objectives": [
                "Master ES2024+ features and modern syntax",
                "Understand closures, prototypes, and the event loop",
                "Build full-stack applications with Node.js",
                "Write type-safe code with TypeScript integration",
            ],
            "key_topics": ["ES2024+ Modern Syntax", "Async/Await & Promises", "DOM Manipulation & Events",
                           "Node.js & NPM Ecosystem", "TypeScript Fundamentals"],
            "resources": [
                {"id": "js1", "title": "JavaScript: The Definitive Guide", "type": "Book", "rating": 4.8},
                {"id": "js2", "title": "Modern JS Deep Dive", "type": "Course", "rating": 4.7},
                {"id": "js3", "title": "Node.js Complete Developer Course", "type": "Course", "rating": 4.6},
            ],
            "mentors": [
                {"id": "m_js1", "name": "Emma Watson", "level": 5, "department": "Frontend Engineering"},
                {"id": "m_js2", "name": "James Park", "level": 4, "department": "Full-Stack"},
            ],
        },
        "React": {
            "hours": 30,
            "description": "Build modern, performant UIs with React 19+. Covers hooks, state management, "
                           "server components, concurrent features, and production-grade architecture.",
            "objectives": [
                "Build component-based UIs with hooks and context",
                "Implement state management with Redux/Zustand",
                "Optimize rendering with memoization and concurrent features",
                "Deploy production-ready React apps with SSR/SSG",
            ],
            "key_topics": ["Hooks & Custom Hooks", "State Management (Redux/Zustand)", "React Server Components",
                           "Performance Optimization", "Testing with React Testing Library"],
            "resources": [
                {"id": "re1", "title": "React 19 - The Complete Guide", "type": "Course", "rating": 4.9},
                {"id": "re2", "title": "Advanced React Patterns", "type": "Workshop", "rating": 4.8},
                {"id": "re3", "title": "React Testing Best Practices", "type": "Tutorial", "rating": 4.5},
            ],
            "mentors": [
                {"id": "m_re1", "name": "Lisa Fleming", "level": 5, "department": "Frontend"},
                {"id": "m_re2", "name": "Daniel Kim", "level": 4, "department": "UI Engineering"},
            ],
        },
        "TypeScript": {
            "hours": 25,
            "description": "Add static typing to JavaScript for safer, more maintainable code. "
                           "Covers generics, utility types, decorators, and integration with React/Node.",
            "objectives": [
                "Write type-safe code with interfaces, generics, and utility types",
                "Configure and optimize TypeScript compiler settings",
                "Integrate TypeScript with React and Node.js projects",
                "Use advanced type patterns for complex applications",
            ],
            "key_topics": ["Type System Fundamentals", "Generics & Utility Types", "Decorators & Metadata",
                           "Module System & Configuration", "React + TypeScript Patterns"],
            "resources": [
                {"id": "ts1", "title": "TypeScript Deep Dive", "type": "Book", "rating": 4.8},
                {"id": "ts2", "title": "Advanced TypeScript Patterns", "type": "Course", "rating": 4.7},
                {"id": "ts3", "title": "TypeScript with React & Node", "type": "Workshop", "rating": 4.6},
            ],
            "mentors": [
                {"id": "m_ts1", "name": "Arun Patel", "level": 5, "department": "Platform Engineering"},
                {"id": "m_ts2", "name": "Maria Gonzalez", "level": 4, "department": "Frontend"},
            ],
        },
        "FastAPI": {
            "hours": 25,
            "description": "Build high-performance REST APIs with FastAPI. Covers async endpoints, "
                           "Pydantic validation, dependency injection, OAuth2, and deployment.",
            "objectives": [
                "Design and build REST APIs with automatic OpenAPI docs",
                "Implement authentication with OAuth2 and JWT",
                "Use dependency injection and middleware patterns",
                "Deploy and scale FastAPI with Docker and Kubernetes",
            ],
            "key_topics": ["Path Operations & Routing", "Pydantic Models & Validation", "Dependency Injection",
                           "Authentication & Authorization", "Async Database Integration"],
            "resources": [
                {"id": "fa1", "title": "FastAPI Full-Stack Web Development", "type": "Course", "rating": 4.8},
                {"id": "fa2", "title": "Building APIs with FastAPI", "type": "Tutorial", "rating": 4.7},
                {"id": "fa3", "title": "FastAPI + Docker Deployment Guide", "type": "Guide", "rating": 4.5},
            ],
            "mentors": [
                {"id": "m_fa1", "name": "Dr. Ahmed Hassan", "level": 5, "department": "Backend"},
                {"id": "m_fa2", "name": "Sophie Laurent", "level": 4, "department": "API Engineering"},
            ],
        },
        "Django": {
            "hours": 35,
            "description": "Master Django for building scalable web applications with built-in ORM, "
                           "admin, auth, and RESTful API capabilities via DRF.",
            "objectives": [
                "Build full-stack web applications with Django MTV pattern",
                "Design database models and optimize queries with Django ORM",
                "Create REST APIs using Django REST Framework",
                "Implement authentication, permissions, and security best practices",
            ],
            "key_topics": ["Models, Views & Templates", "Django ORM & Migrations", "Django REST Framework",
                           "Authentication & Permissions", "Admin Customization & Signals"],
            "resources": [
                {"id": "dj1", "title": "Django for Professionals", "type": "Book", "rating": 4.8},
                {"id": "dj2", "title": "Django REST Framework Masterclass", "type": "Course", "rating": 4.7},
                {"id": "dj3", "title": "Django Deployment on AWS", "type": "Tutorial", "rating": 4.5},
            ],
            "mentors": [
                {"id": "m_dj1", "name": "Robert Williams", "level": 5, "department": "Backend"},
                {"id": "m_dj2", "name": "Priya Sharma", "level": 4, "department": "Full-Stack"},
            ],
        },
        "Node.js": {
            "hours": 30,
            "description": "Build scalable server-side applications with Node.js. Covers event-driven "
                           "architecture, Express/Fastify, streams, real-time apps, and microservices.",
            "objectives": [
                "Build RESTful APIs with Express.js/Fastify",
                "Implement real-time features with WebSockets",
                "Work with databases (MongoDB, PostgreSQL) in Node.js",
                "Deploy microservices with Docker and PM2",
            ],
            "key_topics": ["Event Loop & Streams", "Express.js / Fastify", "Database Integration",
                           "WebSockets & Real-Time", "Microservices Architecture"],
            "resources": [
                {"id": "nd1", "title": "Node.js Design Patterns", "type": "Book", "rating": 4.8},
                {"id": "nd2", "title": "Node.js Complete Developer Course", "type": "Course", "rating": 4.7},
                {"id": "nd3", "title": "Microservices with Node.js", "type": "Workshop", "rating": 4.6},
            ],
            "mentors": [
                {"id": "m_nd1", "name": "Kevin Zhang", "level": 5, "department": "Platform"},
                {"id": "m_nd2", "name": "Anna Morrison", "level": 4, "department": "Backend"},
            ],
        },
        "Docker": {
            "hours": 20,
            "description": "Containerize applications with Docker. Covers images, volumes, networking, "
                           "Docker Compose, and CI/CD pipeline integration.",
            "objectives": [
                "Create optimized Docker images with multi-stage builds",
                "Orchestrate multi-container apps with Docker Compose",
                "Set up Docker networking and volume management",
                "Integrate Docker into CI/CD pipelines",
            ],
            "key_topics": ["Dockerfiles & Multi-Stage Builds", "Docker Compose", "Networking & Volumes",
                           "Container Security", "CI/CD Integration"],
            "resources": [
                {"id": "dk1", "title": "Docker Deep Dive", "type": "Book", "rating": 4.7},
                {"id": "dk2", "title": "Docker & Kubernetes Bootcamp", "type": "Course", "rating": 4.8},
                {"id": "dk3", "title": "Production Docker Workflows", "type": "Tutorial", "rating": 4.5},
            ],
            "mentors": [
                {"id": "m_dk1", "name": "Marcus Johnson", "level": 5, "department": "DevOps"},
                {"id": "m_dk2", "name": "Yuki Tanaka", "level": 4, "department": "Infrastructure"},
            ],
        },
    }
    # Also provide entries for Angular, Vue, Go, Rust, Kubernetes, AWS, etc.
    for skill in ["Angular", "Vue.js", "Go", "Rust", "C++", "C#", "Java", "Kotlin", "Swift",
                   "Ruby", "PHP", "Next.js", "Spring Boot", "Kubernetes", "AWS", "SQL", "MongoDB",
                   "GraphQL", "Machine Learning", "Deep Learning", "DevOps", "Cybersecurity"]:
        if skill not in catalog:
            catalog[skill] = _default_skill_meta(skill, "Intermediate")
    return catalog


@router.post("/path")
async def generate_learning_path(
    request: LearningPathRequest,
    db=Depends(get_db),
):
    """Generate a learning path using Neo4j when available.

    The endpoint first tries to build a path from the knowledge graph
    (skills, documents, mentors). If anything goes wrong or no graph
    data is found, it falls back to a simple heuristic path so the
    endpoint remains stable.
    """

    steps: List[LearningStep] = []
    difficulty: Optional[str] = None
    suggested_prerequisites: List[str] = []

    # --- Primary strategy: use Neo4j graph data ---
    try:
        query = """
        MATCH (target:Skill {name: $target_skill})

        // Prerequisite or related skills the user does not already have
        OPTIONAL MATCH (prereq:Skill)-[:PREREQUISITE_OF]->(target)
        WHERE NOT prereq.name IN $current_skills
        WITH target, collect(DISTINCT prereq.name) AS prereq_names

        OPTIONAL MATCH (target)<-[:RELATED_TO]-(related:Skill)
        WHERE NOT related.name IN $current_skills
        WITH target, prereq_names + collect(DISTINCT related.name) AS all_prereqs

        // Learning resources for the target skill
        OPTIONAL MATCH (d:Document)-[:COVERS_TOPIC]->(target)
        WITH target, all_prereqs,
             collect(DISTINCT {id: d.id, title: d.title, type: d.type, rating: d.rating})[..5] AS resources

        // Mentors with high expertise in the target skill
        OPTIONAL MATCH (p:Person)-[:HAS_SKILL]->(target)
        WHERE p.expertise_level >= 4
        WITH target, all_prereqs, resources,
             collect(DISTINCT {id: p.id, name: p.name, level: p.expertise_level, department: p.department})[..3] AS mentors

        RETURN target.name AS target_skill,
               coalesce(target.level, 'Advanced') AS difficulty,
               all_prereqs[..3] AS suggested_prerequisites,
               resources,
               mentors
        """

        result = db.run(
            query,
            {
                "target_skill": request.target_skill,
                "current_skills": request.current_skills,
            },
        )
        record = result.single()

        if record:
            data = dict(record)

            # Build steps from graph data
            for prereq in data.get("suggested_prerequisites") or []:
                if prereq:
                    # Fetch top documents for each prerequisite skill (recommended resources)
                    try:
                        docs_query = """
                        MATCH (s:Skill {name: $skill})<-[:COVERS_TOPIC]-(d:Document)
                        RETURN d.id as id, d.title as title, d.type as type, d.rating as rating
                        ORDER BY d.rating DESC, d.views DESC
                        LIMIT 3
                        """
                        docs_result = db.run(docs_query, {"skill": prereq})
                        prereq_resources = [dict(r) for r in docs_result]
                    except Exception:
                        prereq_resources = []

                    # Fallback: text match on document topic/title if no graph edges
                    if not prereq_resources:
                        try:
                            fallback_query = """
                            MATCH (d:Document)
                            WHERE toLower(d.topic) CONTAINS toLower($skill)
                               OR toLower(d.title) CONTAINS toLower($skill)
                            RETURN d.id as id, d.title as title, d.type as type, d.rating as rating
                            ORDER BY d.rating DESC, d.views DESC
                            LIMIT 3
                            """
                            fb_result = db.run(fallback_query, {"skill": prereq})
                            prereq_resources = [dict(r) for r in fb_result]
                        except Exception:
                            pass

                    steps.append(
                        LearningStep(
                            skill=prereq,
                            level="Intermediate",
                            estimated_hours=20,
                            resources=prereq_resources,
                            mentors=[],
                            type="prerequisite",
                        )
                    )

            # Prepare target step resources with fallback if graph edges are missing
            target_resources = data.get("resources") or []
            if not target_resources:
                try:
                    fb_target_query = """
                    MATCH (d:Document)
                    WHERE toLower(d.topic) CONTAINS toLower($skill)
                       OR toLower(d.title) CONTAINS toLower($skill)
                    RETURN d.id as id, d.title as title, d.type as type, d.rating as rating
                    ORDER BY d.rating DESC, d.views DESC
                    LIMIT 5
                    """
                    fb_target_res = db.run(fb_target_query, {"skill": data.get("target_skill", request.target_skill)})
                    target_resources = [dict(r) for r in fb_target_res]
                except Exception:
                    target_resources = []

            steps.append(
                LearningStep(
                    skill=data.get("target_skill", request.target_skill),
                    level=data.get("difficulty", "Advanced"),
                    estimated_hours=40,
                    resources=target_resources,
                    mentors=data.get("mentors") or [],
                    type="target",
                )
            )

            difficulty = data.get("difficulty", "Advanced")
            suggested_prerequisites = data.get("suggested_prerequisites") or []

    except Exception:
        # Any Neo4j/driver error will trigger the heuristic fallback below.
        steps = []

    # --- Fallback strategy: rich heuristic path ---
    if not steps:
        _skill_data = _build_skill_metadata()
        for skill in request.current_skills:
            meta = _skill_data.get(skill, _default_skill_meta(skill, "Intermediate"))
            steps.append(
                LearningStep(
                    skill=skill,
                    level="Intermediate",
                    estimated_hours=meta["hours"],
                    resources=meta["resources"],
                    mentors=meta["mentors"],
                    type="prerequisite",
                    description=meta["description"],
                    objectives=meta["objectives"],
                    key_topics=meta["key_topics"],
                )
            )

        if request.target_skill and request.target_skill not in request.current_skills:
            meta = _skill_data.get(request.target_skill, _default_skill_meta(request.target_skill, "Advanced"))
            steps.append(
                LearningStep(
                    skill=request.target_skill,
                    level="Advanced",
                    estimated_hours=meta["hours"],
                    resources=meta["resources"],
                    mentors=meta["mentors"],
                    type="target",
                    description=meta["description"],
                    objectives=meta["objectives"],
                    key_topics=meta["key_topics"],
                )
            )
        difficulty = difficulty or "Advanced"
        suggested_prerequisites = suggested_prerequisites or []

    return {
        "target_skill": request.target_skill,
        "total_steps": len(steps),
        "estimated_total_hours": sum(step.estimated_hours for step in steps),
        "steps": [step.dict() for step in steps],
        "difficulty": difficulty or "Advanced",
        "suggested_prerequisites": suggested_prerequisites,
    }


@router.get("/mentors/{skill}")
async def get_skill_mentors(
    skill: str,
    limit: int = Query(5, le=20),
    db=Depends(get_db)
):
    """
    Get mentors for a specific skill.
    Uses: Requête Filter with Aggregation
    """
    query = """
    MATCH (p:Person)-[:HAS_SKILL]->(s:Skill)
    WHERE s.name = $skill AND p.expertise_level >= 4
    OPTIONAL MATCH (p)-[:AUTHORED]->(d:Document)
    WITH p, s, count(d) as doc_count
    RETURN p.id as id, p.name as name, p.email as email,
           p.department as department, p.expertise_level as expertise_level,
           p.experience_years as experience_years, doc_count
    ORDER BY p.expertise_level DESC, doc_count DESC
    LIMIT $limit
    """
    
    result = db.run(query, {"skill": skill, "limit": limit})
    return [dict(record) for record in result]


@router.get("/skills/recommended")
async def get_recommended_skills(
    current_skills: List[str] = Query(..., description="List of current skill names"),
    limit: int = Query(5, le=20),
    db=Depends(get_db)
):
    """
    Get recommended next skills based on current skills.
    Uses: Requête Chemin + Aggregation
    """
    query = """
    MATCH (current:Skill)<-[:HAS_SKILL]-(p:Person)-[:HAS_SKILL]->(other:Skill)
    WHERE current.name IN $current_skills
      AND NOT other.name IN $current_skills
    WITH other.name as skill, other.category as category, 
         other.demand as demand, count(DISTINCT p) as co_occurrence
    ORDER BY co_occurrence DESC, demand DESC
    LIMIT $limit
    RETURN skill, category, demand, co_occurrence
    """
    
    result = db.run(query, {"current_skills": current_skills, "limit": limit})
    return [dict(record) for record in result]


@router.get("/skills/list")
async def get_all_skills(db=Depends(get_db), _user: dict = Depends(require_auth)):
    """Get all unique skills from the graph, falling back to JSONL data."""
    try:
        query = "MATCH (s:Skill) RETURN DISTINCT s.name as name ORDER BY name"
        result = db.run(query)
        raw_names = [record["name"] for record in result if record["name"]]
        if raw_names:
            # Strip trailing numeric IDs (e.g. "Advanced AI/ML 1009" -> "Advanced AI/ML")
            cleaned = sorted(set(_clean_skill_name(n) for n in raw_names if n))
            return [n for n in cleaned if n]
    except Exception:
        pass

    # Fallback: read from skills.jsonl
    return _load_skills_from_jsonl()

