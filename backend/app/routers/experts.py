from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from ..database import get_db, is_neo4j_available
from ..models.person import Person, PersonWithConnections, PersonUpdate, PersonCreate
from ..auth_utils import get_current_user
from .. import fallback_data
from uuid import uuid4

router = APIRouter(prefix="/api/experts", tags=["experts"])


@router.get("/search", response_model=List[Person])
async def search_experts(
    q: Optional[str] = Query(None, description="Search by name or role"),
    skill: Optional[str] = Query(None, description="Filter by skill name"),
    skills: Optional[List[str]] = Query(None, description="Filter by multiple skills"),
    level: Optional[int] = Query(None, ge=1, le=5, description="Minimum expertise level"),
    location: Optional[str] = Query(None, description="Filter by location"),
    department: Optional[str] = Query(None, description="Filter by department"),
    experience: Optional[int] = Query(None, description="Minimum years of experience"),
    limit: int = Query(20, le=100),
    skip: int = Query(0),
    db=Depends(get_db)
):
    """
    Search experts with filters.
    Uses: Requête Filter (WHERE clause filtering)
    """
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        return fallback_data.search_experts(
            q=q, department=department, location=location,
            min_experience=experience, limit=limit, skip=skip
        )
    
    # Build dynamic Cypher query with filters
    conditions = []
    params = {"limit": limit, "skip": skip}
    
    if level:
        conditions.append("p.expertise_level >= $level")
        params["level"] = level
    if location:
        conditions.append("p.location = $location")
        params["location"] = location
    if department:
        conditions.append("p.department = $department")
        params["department"] = department
    if experience:
        conditions.append("p.experience_years >= $experience")
        params["experience"] = experience
    
    # Base query
    if skill or skills:
        skill_list = skills if skills else [skill]
        query = "MATCH (p:Person)-[:HAS_SKILL]->(s:Skill) "
        conditions.append("any(s_name IN $skills WHERE toLower(s.name) CONTAINS toLower(s_name))")
        params["skills"] = skill_list
    else:
        query = "MATCH (p:Person) "

    if q:
        q_cond = """
        (toLower(p.name) CONTAINS toLower($q) OR 
         toLower(p.role) CONTAINS toLower($q) OR
         EXISTS {
            MATCH (p)-[:HAS_SKILL]->(s2:Skill)
            WHERE toLower(s2.name) CONTAINS toLower($q)
         })
        """
        conditions.append(q_cond)
        params["q"] = q
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += """
    RETURN DISTINCT p.id as id, 
           coalesce(p.name, 'Unnamed Expert') as name, 
           coalesce(p.email, '') as email,
           coalesce(p.department, 'N/A') as department, 
           coalesce(p.role, 'Expert') as role, 
           coalesce(p.location, 'Unknown') as location,
           p.hire_date as hire_date, 
           coalesce(p.experience_years, 0) as experience_years,
           coalesce(p.expertise_level, 1) as expertise_level,
           coalesce(p.created_at, p.hire_date, '2020-01-01') as sort_date
    ORDER BY sort_date DESC, expertise_level DESC
    SKIP $skip LIMIT $limit
    """
    
    result = db.run(query, params)
    experts = [dict(record) for record in result]
    return experts


@router.get("/{expert_id}", response_model=PersonWithConnections)
async def get_expert_profile(expert_id: str, db=Depends(get_db)):
    """
    Get expert profile with all connections.
    Uses: Requête Simple (basic node retrieval with relationships)
    """
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        expert = fallback_data.get_expert_by_id(expert_id)
        if not expert:
            raise HTTPException(status_code=404, detail="Expert not found")
        # Add additional fields expected by the response model
        expert["projects"] = []
        expert["documents"] = []
        expert["connections"] = len(expert.get("skills", []))
        return expert
    
    query = """
    MATCH (p:Person {id: $id})
    OPTIONAL MATCH (p)-[:HAS_SKILL]->(s:Skill)
    OPTIONAL MATCH (p)-[:WORKS_ON]->(proj:Project)
    OPTIONAL MATCH (p)-[:AUTHORED]->(d:Document)
    WITH p, 
         collect(DISTINCT {id: s.id, name: s.name, level: s.level}) as skills,
         collect(DISTINCT {id: proj.id, name: proj.name, status: proj.status}) as projects,
         collect(DISTINCT {id: d.id, title: d.title, type: d.type}) as documents
    RETURN p.id as id, p.name as name, p.email as email,
           p.department as department, p.role as role, p.location as location,
           p.hire_date as hire_date, p.experience_years as experience_years,
           p.expertise_level as expertise_level,
           skills, projects, documents,
           size(skills) + size(projects) + size(documents) as connections
    """
    
    result = db.run(query, {"id": expert_id})
    record = result.single()
    
    if not record:
        raise HTTPException(status_code=404, detail="Expert not found")
    
    return dict(record)


@router.get("/{expert_id}/network")
async def get_expert_network(
    expert_id: str,
    hops: int = Query(2, ge=1, le=3),
    db=Depends(get_db)
):
    """
    Get expert's network graph for visualization.
    Uses: Requête Chemin (path query with variable length)
    """
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        return fallback_data.get_graph_data()
    
    query = """
    MATCH path = (p:Person {id: $id})-[*1..""" + str(hops) + """]->(connected)
    WHERE connected:Skill OR connected:Project OR connected:Person
    WITH nodes(path) as nodes, relationships(path) as rels
    UNWIND nodes as node
    WITH DISTINCT node, rels
    RETURN 
        collect(DISTINCT {
            id: node.id,
            label: COALESCE(node.name, node.title),
            type: labels(node)[0],
            properties: properties(node)
        }) as nodes,
        collect(DISTINCT {
            source: startNode(head(rels)).id,
            target: endNode(head(rels)).id,
            type: type(head(rels))
        }) as links
    """
    
    result = db.run(query, {"id": expert_id})
    record = result.single()
    
    if not record:
        return {"nodes": [], "links": []}
    
    return dict(record)


@router.put("/{expert_id}", response_model=Person)
async def update_expert(
    expert_id: str,
    update: PersonUpdate,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Update expert profile.
    Uses: Requête de Modification (SET clause)
    """
    if not is_neo4j_available():
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Build dynamic SET clause
    set_clauses = []
    params = {"id": expert_id}
    
    update_dict = update.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        set_clauses.append(f"p.{key} = ${key}")
        params[key] = value
    
    if not set_clauses:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    query = f"""
    MATCH (p:Person {{id: $id}})
    SET {', '.join(set_clauses)}
    RETURN p.id as id, p.name as name, p.email as email,
           p.department as department, p.role as role, p.location as location,
           p.hire_date as hire_date, p.experience_years as experience_years,
           p.expertise_level as expertise_level
    """
    
    result = db.run(query, params)
    record = result.single()
    
    if not record:
        raise HTTPException(status_code=404, detail="Expert not found")
    
    return dict(record)


@router.post("", response_model=Person)
async def create_expert(
    payload: PersonCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Create a new expert.
    """
    if not is_neo4j_available():
        raise HTTPException(status_code=503, detail="Database not available")
    
    expert_id = str(uuid4())
    query = """
    CREATE (p:Person {
        id: $id,
        name: $name,
        email: $email,
        department: $department,
        role: $role,
        location: $location,
        experience_years: $experience_years,
        expertise_level: $expertise_level,
        hire_date: $hire_date,
        created_at: $created_at
    })
    RETURN p.id as id, p.name as name, p.email as email,
           p.department as department, p.role as role, p.location as location,
           p.hire_date as hire_date, p.experience_years as experience_years,
           p.expertise_level as expertise_level
    """
    from datetime import datetime
    params = payload.model_dump()
    params["id"] = expert_id
    params["hire_date"] = datetime.now().date().isoformat()
    params["created_at"] = datetime.now().isoformat()
    
    result = db.run(query, params)
    record = result.single()
    return dict(record)



@router.get("/locations/list")
async def get_locations(db=Depends(get_db)):
    """Get all unique locations for filter dropdown."""
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        employees = fallback_data.get_employees()
        locations = list(set(e.get("location") for e in employees if e.get("location")))
        return sorted(locations)
    
    query = """
    MATCH (p:Person)
    RETURN DISTINCT p.location as location
    ORDER BY location
    """
    result = db.run(query)
    return [record["location"] for record in result if record["location"]]


@router.get("/departments/list")
async def get_departments(db=Depends(get_db)):
    """Get all unique departments for filter dropdown."""
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        employees = fallback_data.get_employees()
        departments = list(set(e.get("department") for e in employees if e.get("department")))
        return sorted(departments)
    
    query = """
    MATCH (p:Person)
    RETURN DISTINCT p.department as department
    ORDER BY department
    """
    result = db.run(query)
    return [record["department"] for record in result if record["department"]]


@router.delete("/{expert_id}", status_code=204)
async def delete_expert(
    expert_id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Delete an expert.
    """
    if not is_neo4j_available():
        raise HTTPException(status_code=503, detail="Database not available")
    
    query = """
    MATCH (p:Person {id: $id})
    DETACH DELETE p
    """
    result = db.run(query, {"id": expert_id})
    return None
