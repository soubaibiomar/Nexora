"""
Fallback Data Service - Serves data from JSONL files when Neo4j is unavailable
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import random

# Data directory path
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"

# Cache for loaded data
_cache = {}


def load_jsonl(filename: str) -> List[Dict[str, Any]]:
    """Load JSONL file and cache the results."""
    if filename in _cache:
        return _cache[filename]
    
    filepath = DATA_DIR / filename
    records = []
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    _cache[filename] = records
    return records


def get_employees() -> List[Dict[str, Any]]:
    """Get all employees."""
    return load_jsonl("employees.jsonl")


def get_documents() -> List[Dict[str, Any]]:
    """Get all documents."""
    return load_jsonl("documents.jsonl")


def get_skills() -> List[Dict[str, Any]]:
    """Get all skills."""
    return load_jsonl("skills.jsonl")


def get_projects() -> List[Dict[str, Any]]:
    """Get all projects."""
    return load_jsonl("projects.jsonl")


def search_documents(
    q: Optional[str] = None,
    doc_type: Optional[str] = None,
    topic: Optional[str] = None,
    min_rating: Optional[float] = None,
    limit: int = 20,
    skip: int = 0
) -> List[Dict[str, Any]]:
    """Search documents with filters."""
    docs = get_documents()
    results = []
    
    for doc in docs:
        # Apply filters
        if q:
            q_lower = q.lower()
            title = (doc.get("title") or "").lower()
            topic_val = (doc.get("topic") or "").lower()
            content = (doc.get("content") or "").lower()
            if q_lower not in title and q_lower not in topic_val and q_lower not in content:
                continue
        
        if doc_type and doc.get("type") != doc_type:
            continue
            
        if topic:
            topic_lower = topic.lower()
            doc_topic = (doc.get("topic") or "").lower()
            if topic_lower not in doc_topic:
                continue
                
        if min_rating and (doc.get("rating") or 0) < min_rating:
            continue
            
        results.append(doc)
    
    # Sort by date and rating
    results.sort(key=lambda x: (x.get("date") or "", x.get("rating") or 0), reverse=True)
    
    return results[skip:skip + limit]


def get_document_by_id(doc_id: str) -> Optional[Dict[str, Any]]:
    """Get a single document by ID."""
    docs = get_documents()
    for doc in docs:
        if doc.get("id") == doc_id:
            # Get author details if available
            author_id = doc.get("author")
            author_details = None
            if author_id:
                employees = get_employees()
                for emp in employees:
                    if emp.get("id") == author_id:
                        author_details = {
                            "id": emp.get("id"),
                            "name": emp.get("name"),
                            "department": emp.get("department")
                        }
                        break
            
            result = dict(doc)
            result["author_details"] = author_details
            result["related_skills"] = []
            return result
    return None


def search_experts(
    q: Optional[str] = None,
    skill: Optional[str] = None,
    department: Optional[str] = None,
    location: Optional[str] = None,
    min_experience: Optional[int] = None,
    limit: int = 20,
    skip: int = 0
) -> List[Dict[str, Any]]:
    """Search experts/employees with filters."""
    employees = get_employees()
    results = []
    
    for emp in employees:
        if q:
            q_lower = q.lower()
            name = (emp.get("name") or "").lower()
            role = (emp.get("role") or "").lower()
            dept = (emp.get("department") or "").lower()
            if q_lower not in name and q_lower not in role and q_lower not in dept:
                continue
        
        if department:
            emp_dept = (emp.get("department") or "").lower()
            if department.lower() not in emp_dept:
                continue
                
        if location:
            emp_location = (emp.get("location") or "").lower()
            if location.lower() not in emp_location:
                continue
                
        if min_experience and (emp.get("experience_years") or 0) < min_experience:
            continue
            
        results.append(emp)
    
    # Sort by expertise level
    results.sort(key=lambda x: x.get("expertise_level") or 0, reverse=True)
    
    return results[skip:skip + limit]


def get_expert_by_id(expert_id: str) -> Optional[Dict[str, Any]]:
    """Get a single expert by ID."""
    employees = get_employees()
    for emp in employees:
        if emp.get("id") == expert_id:
            result = dict(emp)
            # Add random skills for the expert
            skills = get_skills()
            result["skills"] = random.sample(skills, min(5, len(skills)))
            return result
    return None


def get_dashboard_stats() -> Dict[str, Any]:
    """Get dashboard statistics."""
    employees = get_employees()
    documents = get_documents()
    skills = get_skills()
    projects = get_projects()
    
    # Topic distribution
    topic_counts = {}
    for doc in documents:
        topic = doc.get("topic", "Other")
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    # Department distribution (with person_count and avg_expertise)
    dept_data = {}
    for emp in employees:
        dept = emp.get("department", "Other")
        if dept not in dept_data:
            dept_data[dept] = {"person_count": 0, "total_expertise": 0, "total_experience": 0}
        dept_data[dept]["person_count"] += 1
        dept_data[dept]["total_expertise"] += emp.get("expertise_level", 3)
        dept_data[dept]["total_experience"] += emp.get("experience_years", 2)
    
    # Skill category distribution (with skill_count and expert_count)
    skill_cats = {}
    for skill in skills:
        cat = skill.get("category", "Other")
        if cat not in skill_cats:
            skill_cats[cat] = {"skill_count": 0, "expert_count": 0}
        skill_cats[cat]["skill_count"] += 1
        skill_cats[cat]["expert_count"] += skill.get("demand", 0) // 10  # approximate
    
    department_distribution = []
    for dept, data in dept_data.items():
        count = data["person_count"]
        department_distribution.append({
            "department": dept,
            "person_count": count,
            "avg_experience": round(data["total_experience"] / count, 1) if count else 0,
            "avg_expertise": round(data["total_expertise"] / count, 1) if count else 0,
        })
    
    skill_categories = []
    for cat, data in skill_cats.items():
        skill_categories.append({
            "category": cat,
            "skill_count": data["skill_count"],
            "expert_count": data["expert_count"],
        })
    
    return {
        "total_experts": len(employees),
        "total_documents": len(documents),
        "total_skills": len(skills),
        "total_projects": len(projects),
        "topic_distribution": [{"topic": k, "count": v} for k, v in topic_counts.items()],
        "department_distribution": department_distribution,
        "skill_categories": skill_categories,
        "recent_documents": documents[:5] if documents else [],
        "top_experts": sorted(employees, key=lambda x: x.get("expertise_level", 0), reverse=True)[:5]
    }


def get_graph_data(node_type: str = None, search: str = None, limit: int = 200) -> Dict[str, Any]:
    """Get data for graph visualization with real project connections."""
    employees = get_employees()
    skills = get_skills()
    projects = get_projects()

    # Build lookup maps
    skill_map = {s["id"]: s for s in skills}
    skill_name_map = {s.get("name", "").lower(): s for s in skills}
    emp_map = {e["id"]: e for e in employees}

    nodes = []
    links = []
    node_ids = set()

    def add_node(nid, name, ntype, group="", props=None):
        if nid not in node_ids:
            node_ids.add(nid)
            nodes.append({
                "id": nid,
                "label": name,
                "name": name,
                "type": ntype,
                "group": group,
                "properties": props or {},
            })

    # --- Add Project nodes + links to team members & required skills ---
    for proj in projects[:40]:
        pid = proj["id"]
        add_node(pid, proj.get("name", ""), "Project", proj.get("domain", ""),
                 {"status": proj.get("status"), "domain": proj.get("domain"),
                  "team_size": proj.get("team_size", 0), "priority": proj.get("priority")})

        # WORKS_ON links (employee -> project)
        for emp_id in proj.get("team_members", []):
            emp = emp_map.get(emp_id)
            if emp:
                add_node(emp_id, emp.get("name", ""), "Person", emp.get("department", ""),
                         {"role": emp.get("role"), "department": emp.get("department"),
                          "location": emp.get("location")})
                links.append({"source": emp_id, "target": pid, "type": "WORKS_ON"})

        # REQUIRES links (project -> skill)
        for skill_name in proj.get("required_skills", []):
            sk = skill_name_map.get(skill_name.lower())
            if sk:
                add_node(sk["id"], sk.get("name", ""), "Skill", sk.get("category", ""))
                links.append({"source": pid, "target": sk["id"], "type": "REQUIRES"})

    # --- Add HAS_SKILL links from employee skills ---
    for emp in employees[:60]:
        eid = emp["id"]
        for skill_name in emp.get("skills", []):
            sk = skill_name_map.get(skill_name.lower())
            if sk and eid in node_ids:
                add_node(sk["id"], sk.get("name", ""), "Skill", sk.get("category", ""))
                links.append({"source": eid, "target": sk["id"], "type": "HAS_SKILL"})

    # --- Filtering ---
    if node_type:
        allowed_ids = {n["id"] for n in nodes if n["type"] == node_type}
        # Also keep connected nodes
        for link in links:
            s, t = link["source"], link["target"]
            if s in allowed_ids:
                allowed_ids.add(t)
            if t in allowed_ids:
                allowed_ids.add(s)
        nodes = [n for n in nodes if n["id"] in allowed_ids]
        links = [l for l in links if l["source"] in allowed_ids and l["target"] in allowed_ids]

    if search:
        q = search.lower()
        match_ids = {n["id"] for n in nodes if q in (n.get("label") or n.get("name") or "").lower()}
        for link in links:
            if link["source"] in match_ids:
                match_ids.add(link["target"])
            if link["target"] in match_ids:
                match_ids.add(link["source"])
        nodes = [n for n in nodes if n["id"] in match_ids]
        links = [l for l in links if l["source"] in match_ids and l["target"] in match_ids]

    # Deduplicate links
    seen = set()
    unique_links = []
    for l in links:
        key = (l["source"], l["target"], l["type"])
        if key not in seen:
            seen.add(key)
            unique_links.append(l)

    return {
        "nodes": nodes[:limit],
        "links": unique_links,
    }


def clear_cache():
    """Clear the data cache."""
    global _cache
    _cache = {}
