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
    
    # Department distribution
    dept_counts = {}
    for emp in employees:
        dept = emp.get("department", "Other")
        dept_counts[dept] = dept_counts.get(dept, 0) + 1
    
    # Skill category distribution
    skill_cats = {}
    for skill in skills:
        cat = skill.get("category", "Other")
        skill_cats[cat] = skill_cats.get(cat, 0) + 1
    
    return {
        "total_experts": len(employees),
        "total_documents": len(documents),
        "total_skills": len(skills),
        "total_projects": len(projects),
        "topic_distribution": [{"topic": k, "count": v} for k, v in topic_counts.items()],
        "department_distribution": [{"department": k, "count": v} for k, v in dept_counts.items()],
        "skill_categories": [{"category": k, "count": v} for k, v in skill_cats.items()],
        "recent_documents": documents[:5] if documents else [],
        "top_experts": sorted(employees, key=lambda x: x.get("expertise_level", 0), reverse=True)[:5]
    }


def get_graph_data() -> Dict[str, Any]:
    """Get data for graph visualization."""
    employees = get_employees()[:30]  # Limit for performance
    skills = get_skills()[:20]
    
    nodes = []
    links = []
    
    # Add employee nodes
    for emp in employees:
        nodes.append({
            "id": emp["id"],
            "name": emp.get("name", "Unknown"),
            "type": "Person",
            "group": emp.get("department", "Other")
        })
    
    # Add skill nodes
    for skill in skills:
        nodes.append({
            "id": skill["id"],
            "name": skill.get("name", "Unknown"),
            "type": "Skill",
            "group": skill.get("category", "Other")
        })
    
    # Create links between employees and skills
    for emp in employees:
        # Assign 2-4 random skills to each employee
        emp_skills = random.sample(skills, min(random.randint(2, 4), len(skills)))
        for skill in emp_skills:
            links.append({
                "source": emp["id"],
                "target": skill["id"],
                "type": "HAS_SKILL"
            })
    
    return {
        "nodes": nodes,
        "links": links
    }


def clear_cache():
    """Clear the data cache."""
    global _cache
    _cache = {}
