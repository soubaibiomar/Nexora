from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from ..database import get_db, is_neo4j_available
from .. import fallback_data
from ..auth_guards import require_auth, require_manager

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_global_stats(db=Depends(get_db), _user: dict = Depends(require_auth)):
    """
    Get global platform statistics.
    Uses: Requête Aggregation (count, sum)
    """
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        stats = fallback_data.get_dashboard_stats()
        return {
            "persons": stats["total_experts"],
            "skills": stats["total_skills"],
            "projects": stats["total_projects"],
            "documents": stats["total_documents"],
            "technologies": 0,
            "total_nodes": stats["total_experts"] + stats["total_skills"] + stats["total_projects"] + stats["total_documents"],
            "total_relationships": 0
        }
    
    query = """
    MATCH (p:Person) WITH count(p) as person_count
    MATCH (s:Skill) WITH person_count, count(s) as skill_count
    MATCH (proj:Project) WITH person_count, skill_count, count(proj) as project_count
    MATCH (d:Document) WITH person_count, skill_count, project_count, count(d) as doc_count
    MATCH (t:Technology) WITH person_count, skill_count, project_count, doc_count, count(t) as tech_count
    RETURN person_count, skill_count, project_count, doc_count, tech_count,
           person_count + skill_count + project_count + doc_count + tech_count as total_nodes
    """
    
    result = db.run(query, {})
    record = result.single()
    
    # Get relationship count
    rel_query = "MATCH ()-[r]->() RETURN count(r) as rel_count"
    rel_result = db.run(rel_query, {})
    rel_record = rel_result.single()
    
    return {
        "persons": record["person_count"] if record else 0,
        "skills": record["skill_count"] if record else 0,
        "projects": record["project_count"] if record else 0,
        "documents": record["doc_count"] if record else 0,
        "technologies": record["tech_count"] if record else 0,
        "total_nodes": record["total_nodes"] if record else 0,
        "total_relationships": rel_record["rel_count"] if rel_record else 0
    }


@router.get("/top-skills")
async def get_top_skills(
    limit: int = Query(10, le=50),
    db=Depends(get_db)
):
    """
    Get top skills by demand and expert count.
    Uses: Requête Aggregation (count, order by)
    """
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        skills = fallback_data.get_skills()
        skills_sorted = sorted(skills, key=lambda x: x.get("demand", 0), reverse=True)
        return skills_sorted[:limit]
    
    query = """
    MATCH (s:Skill)
    OPTIONAL MATCH (p:Person)-[:HAS_SKILL]->(s)
    WITH s, count(p) as expert_count
    RETURN s.id as id, s.name as name, s.category as category,
           s.level as level, s.demand as demand, expert_count
    ORDER BY s.demand DESC, expert_count DESC
    LIMIT $limit
    """
    
    result = db.run(query, {"limit": limit})
    return [dict(record) for record in result]


@router.get("/skill-gaps")
async def get_skill_gaps(
    limit: int = Query(10, le=50),
    db=Depends(get_db)
):
    """
    Identify critical skill gaps (high demand, low supply).
    Uses: Requête Aggregation + Filter
    """
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        skills = fallback_data.get_skills()
        high_demand = [s for s in skills if s.get("demand", 0) >= 50]
        return high_demand[:limit]
    
    query = """
    MATCH (s:Skill)
    WHERE s.demand >= 50
    OPTIONAL MATCH (p:Person)-[:HAS_SKILL]->(s)
    WHERE p.expertise_level >= 4
    WITH s, count(p) as expert_count
    WITH s, expert_count, s.demand - (expert_count * 10) as gap_score
    WHERE gap_score > 0
    RETURN s.id as id, s.name as name, s.category as category,
           s.demand as demand, expert_count, gap_score
    ORDER BY gap_score DESC
    LIMIT $limit
    """
    
    result = db.run(query, {"limit": limit})
    return [dict(record) for record in result]


@router.get("/departments")
async def get_department_stats(db=Depends(get_db), _user: dict = Depends(require_auth)):
    """
    Get statistics by department.
    Uses: Requête Aggregation (GROUP BY equivalent)
    """
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        stats = fallback_data.get_dashboard_stats()
        return stats["department_distribution"]
    
    query = """
    MATCH (p:Person)
    WITH p.department as department, count(p) as person_count,
         avg(p.experience_years) as avg_experience,
         avg(p.expertise_level) as avg_expertise
    RETURN department, person_count, 
           round(avg_experience * 10) / 10 as avg_experience,
           round(avg_expertise * 10) / 10 as avg_expertise
    ORDER BY person_count DESC
    """
    
    result = db.run(query, {})
    return [dict(record) for record in result]


@router.get("/skill-distribution")
async def get_skill_distribution(db=Depends(get_db), _user: dict = Depends(require_auth)):
    """
    Get skill distribution by category.
    Uses: Requête Aggregation (category grouping)
    """
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        stats = fallback_data.get_dashboard_stats()
        return stats["skill_categories"]
    
    query = """
    MATCH (s:Skill)
    OPTIONAL MATCH (p:Person)-[:HAS_SKILL]->(s)
    WITH s.category as category, count(DISTINCT s) as skill_count,
         count(DISTINCT p) as expert_count
    RETURN category, skill_count, expert_count
    ORDER BY skill_count DESC
    """
    
    result = db.run(query, {})
    return [dict(record) for record in result]


@router.get("/project-status")
async def get_project_status(db=Depends(get_db), _user: dict = Depends(require_auth)):
    """
    Get project statistics by status.
    Uses: Requête Aggregation (status grouping)
    """
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        projects = fallback_data.get_projects()
        status_counts = {}
        for p in projects:
            status = p.get("status", "Unknown")
            if status not in status_counts:
                status_counts[status] = {"status": status, "count": 0, "total_budget": 0}
            status_counts[status]["count"] += 1
            status_counts[status]["total_budget"] += p.get("budget", 0)
        # Compute avg_budget for each status group
        result = []
        for entry in status_counts.values():
            entry["avg_budget"] = round(entry["total_budget"] / entry["count"]) if entry["count"] > 0 else 0
            result.append(entry)
        return result
    
    query = """
    MATCH (proj:Project)
    WITH proj.status as status, count(proj) as count, 
         sum(proj.budget) as total_budget,
         avg(proj.budget) as avg_budget
    RETURN status, count, 
           total_budget,
           round(avg_budget) as avg_budget
    ORDER BY count DESC
    """
    
    result = db.run(query, {})
    return [dict(record) for record in result]


@router.get("/collaboration-rate")
async def get_collaboration_rate(db=Depends(get_db), _user: dict = Depends(require_auth)):
    """
    Analyze inter-department collaboration.
    Uses: Requête Chemin (cross-department connections through projects)
    """
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        # Return sample collaboration data
        return [
            {"dept1": "Engineering", "dept2": "Data Science", "collaborations": 15},
            {"dept1": "DevOps", "dept2": "Security", "collaborations": 12}
        ]
    
    query = """
    MATCH (p1:Person)-[:WORKS_ON]->(proj:Project)<-[:WORKS_ON]-(p2:Person)
    WHERE p1.department <> p2.department AND id(p1) < id(p2)
    WITH p1.department as dept1, p2.department as dept2, count(*) as collaborations
    RETURN dept1, dept2, collaborations
    ORDER BY collaborations DESC
    LIMIT 20
    """
    
    result = db.run(query, {})
    return [dict(record) for record in result]


@router.get("/knowledge-silos")
async def detect_knowledge_silos(db=Depends(get_db), _user: dict = Depends(require_auth)):
    """
    Detect potential knowledge silos (skills held by few experts).
    Uses: Requête Aggregation + Filter
    """
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        skills = fallback_data.get_skills()
        # Return skills with high demand as potential silos
        high_demand = [s for s in skills if s.get("demand", 0) >= 30]
        return high_demand[:10]
    
    query = """
    MATCH (s:Skill)
    WHERE s.demand >= 30
    OPTIONAL MATCH (p:Person)-[:HAS_SKILL]->(s)
    WITH s, collect(DISTINCT p.id) as experts, count(DISTINCT p) as expert_count
    WHERE expert_count <= 2
    RETURN s.id as id, s.name as name, s.category as category,
           s.demand as demand, expert_count, experts
    ORDER BY s.demand DESC
    LIMIT 20
    """
    
    result = db.run(query, {})
    return [dict(record) for record in result]


# ── Predictive Analytics ───────────────────────────────────────────

from ..ml.analytics import analytics

@router.get("/predict-shortages")
async def predict_skill_shortages(_user: dict = Depends(require_auth)):
    """
    AI-powered skill shortage prediction for the next 6 months.
    Uses PySpark (if available) or Pandas for trend forecasting.
    """
    return analytics.predict_skill_shortages()


@router.get("/skill-trends")
async def get_skill_trends(_user: dict = Depends(require_auth)):
    """
    Quarterly skill trend data for visualization charts.
    """
    return analytics.get_trend_data()

