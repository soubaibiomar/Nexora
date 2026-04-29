"""
Graph Visualization API Router
Provides user-scoped network graph: only shows the current user's direct connections.
To see connections of connections (2nd degree), users must send a request and wait for approval.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from ..database import get_db, is_neo4j_available
from .. import fallback_data
from .network import _init_network, _connections, _load_employees
import uuid
import random
from datetime import datetime, timedelta
from ..auth_guards import require_auth

router = APIRouter(prefix="/api/graph", tags=["graph"])


# ── View Requests Store ────────────────────────────────────────────
# Stores requests to view 2nd-degree connections (connections of connections)
_view_requests: List[dict] = []
_approved_views: dict = {}  # connection_id -> list of their connection ids you can see


class ViewRequest(BaseModel):
    connection_id: str  # Whose connections you want to see


# ── My Network Graph ───────────────────────────────────────────────
@router.get("/my-network")
async def get_my_network_graph(_user: dict = Depends(require_auth)):
    """
    Get the graph showing ONLY the current user's direct connections.
    The user is the center node, with edges to each of their connections.
    """
    _init_network()
    connections = list(_connections.values())

    # The current user is the center node
    user_node = {
        "id": "current_user",
        "label": "You",
        "type": "User",
        "properties": {"role": "Current User", "department": ""},
    }

    nodes = [user_node]
    links = []

    for conn in connections:
        nodes.append({
            "id": conn["id"],
            "label": conn["name"],
            "type": "Connection",
            "properties": {
                "role": conn.get("role", ""),
                "department": conn.get("department", ""),
                "location": conn.get("location", ""),
                "connected_at": conn.get("connected_at", ""),
            },
        })
        links.append({
            "source": "current_user",
            "target": conn["id"],
            "type": "CONNECTED_TO",
        })

    # Add approved 2nd-degree connections
    for conn_id, second_degree_ids in _approved_views.items():
        for sd_id in second_degree_ids:
            # Make sure the second-degree node exists
            if not any(n["id"] == sd_id for n in nodes):
                employees = _load_employees()
                emp = next((e for e in employees if e.get("id") == sd_id), None)
                if emp:
                    nodes.append({
                        "id": sd_id,
                        "label": emp.get("name", "Unknown"),
                        "type": "SecondDegree",
                        "properties": {
                            "role": emp.get("role", ""),
                            "department": emp.get("department", ""),
                            "via": conn_id,
                        },
                    })
            links.append({
                "source": conn_id,
                "target": sd_id,
                "type": "KNOWS",
            })

    return {
        "nodes": nodes,
        "links": links,
        "total_connections": len(connections),
        "pending_requests": len([r for r in _view_requests if r["status"] == "pending"]),
        "approved_expansions": len(_approved_views),
    }


# ── Request to View Connections of a Connection ────────────────────
@router.post("/view-request")
async def request_view_connections(req: ViewRequest, _user: dict = Depends(require_auth)):
    """
    Send a request to view the connections of one of your connections.
    The connection must approve it before you can see their network.
    """
    _init_network()

    # Verify the target is actually your connection
    if req.connection_id not in _connections:
        raise HTTPException(status_code=400, detail="This person is not in your connections")

    # Check if already requested
    existing = next(
        (r for r in _view_requests if r["connection_id"] == req.connection_id and r["status"] in ("pending", "approved")),
        None
    )
    if existing:
        return {
            "message": f"Request already {existing['status']}",
            "request": existing,
        }

    connection = _connections[req.connection_id]
    request_obj = {
        "id": str(uuid.uuid4()),
        "connection_id": req.connection_id,
        "connection_name": connection["name"],
        "connection_role": connection.get("role", ""),
        "status": "pending",
        "requested_at": datetime.utcnow().isoformat(),
        "responded_at": None,
    }
    _view_requests.append(request_obj)

    return {
        "message": f"Request sent to {connection['name']}. You'll be notified when they respond.",
        "request": request_obj,
    }


# ── Get All View Requests ──────────────────────────────────────────
@router.get("/view-requests")
async def get_view_requests(_user: dict = Depends(require_auth)):
    """Get all view requests and their statuses."""
    _init_network()
    return {
        "requests": _view_requests,
        "pending": len([r for r in _view_requests if r["status"] == "pending"]),
        "approved": len([r for r in _view_requests if r["status"] == "approved"]),
        "denied": len([r for r in _view_requests if r["status"] == "denied"]),
    }


# ── Simulate Approval (for demo: auto-approve after request) ──────
@router.post("/view-request/{request_id}/simulate-response")
async def simulate_view_response(request_id: str, approve: bool = True, _user: dict = Depends(require_auth)):
    """
    Simulate the connection responding to a view request.
    In production, the connection would approve/deny via their own interface.
    """
    _init_network()

    req = next((r for r in _view_requests if r["id"] == request_id), None)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    if req["status"] != "pending":
        return {"message": f"Request already {req['status']}"}

    if approve:
        req["status"] = "approved"
        req["responded_at"] = datetime.utcnow().isoformat()

        # Generate some 2nd-degree connections for this person
        employees = _load_employees()
        connected_ids = set(_connections.keys())
        second_degree = []
        for emp in employees:
            eid = emp.get("id")
            if eid and eid != req["connection_id"] and eid not in connected_ids and len(second_degree) < 5:
                second_degree.append(eid)

        _approved_views[req["connection_id"]] = second_degree

        return {
            "message": f"{req['connection_name']} approved your request! You can now see their connections.",
            "request": req,
            "new_connections_visible": len(second_degree),
        }
    else:
        req["status"] = "denied"
        req["responded_at"] = datetime.utcnow().isoformat()
        return {
            "message": f"{req['connection_name']} denied your request.",
            "request": req,
        }


# ── Original Endpoints (kept for backward compatibility) ───────────

@router.get("/nodes")
async def get_graph_nodes(
    node_type: Optional[str] = Query(None, description="Filter by node type"),
    q: Optional[str] = Query(None, description="Search nodes by name/title"),
    limit: int = Query(200, le=500),
    db=Depends(get_db)
):
    """
    Get nodes and links for 3D graph visualization with filters.
    """
    if not is_neo4j_available():
        graph_data = fallback_data.get_graph_data(
            node_type=node_type, search=q, limit=limit
        )
        return graph_data

    conditions = []
    params = {"limit": limit}

    label_node = f":{node_type}" if node_type else ""
    query_base = f"MATCH (n{label_node})"

    if not node_type:
        conditions.append("(n:Person OR n:Skill OR n:Project OR n:Document)")

    if q:
        conditions.append("(toLower(n.name) CONTAINS toLower($q) OR toLower(n.title) CONTAINS toLower($q))")
        params["q"] = q

    query = query_base
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += """
    RETURN n.id as id, 
           COALESCE(n.name, n.title) as label,
           labels(n)[0] as type,
           properties(n) as properties
    LIMIT $limit
    """

    result = db.run(query, params)
    nodes = [dict(record) for record in result]
    return {"nodes": nodes}


@router.get("/expand/{node_id}")
async def expand_node(
    node_id: str,
    hops: int = Query(1, ge=1, le=3),
    db=Depends(get_db)
):
    """
    Expand node connections for visualization.
    Uses: Requête Chemin (variable length path)
    """
    if not is_neo4j_available():
        return fallback_data.get_graph_data()

    query = """
    MATCH (center {id: $id})
    MATCH (center)-[r*1..""" + str(hops) + """]-(connected)
    WHERE connected:Person OR connected:Skill OR connected:Project OR connected:Document
    WITH center, connected, r
    RETURN DISTINCT 
        collect(DISTINCT {
            id: connected.id,
            label: COALESCE(connected.name, connected.title),
            type: labels(connected)[0]
        }) as nodes,
        [{
            id: center.id,
            label: COALESCE(center.name, center.title),
            type: labels(center)[0]
        }] as center_node
    """

    result = db.run(query, {"id": node_id})
    record = result.single()

    if not record:
        return {"nodes": [], "links": []}

    link_query = """
    MATCH (center {id: $id})-[r]-(connected)
    WHERE connected:Person OR connected:Skill OR connected:Project OR connected:Document
    RETURN DISTINCT center.id as source, connected.id as target, type(r) as type
    """

    link_result = db.run(link_query, {"id": node_id})
    links = [dict(r) for r in link_result]

    all_nodes = record["center_node"] + record["nodes"]
    return {"nodes": all_nodes, "links": links}


@router.get("/path")
async def find_path(
    from_id: str = Query(..., description="Source node ID"),
    to_id: str = Query(..., description="Target node ID"),
    db=Depends(get_db)
):
    """
    Find shortest path between two nodes.
    Uses: Requête Chemin (shortestPath)
    """
    if not is_neo4j_available():
        raise HTTPException(status_code=503, detail="Path finding requires Neo4j database")

    query = """
    MATCH (start {id: $from_id}), (end {id: $to_id})
    MATCH path = shortestPath((start)-[*..6]-(end))
    WITH nodes(path) as pathNodes, relationships(path) as pathRels
    RETURN 
        [n IN pathNodes | {
            id: n.id,
            label: COALESCE(n.name, n.title),
            type: labels(n)[0]
        }] as nodes,
        [r IN pathRels | {
            source: startNode(r).id,
            target: endNode(r).id,
            type: type(r)
        }] as links,
        length(path) as path_length
    """

    result = db.run(query, {"from_id": from_id, "to_id": to_id})
    record = result.single()

    if not record:
        raise HTTPException(status_code=404, detail="No path found between nodes")

    return dict(record)


@router.get("/stats")
async def get_graph_stats(db=Depends(get_db), _user: dict = Depends(require_auth)):
    """
    Get graph statistics.
    Uses: Requête Aggregation (count)
    """
    if not is_neo4j_available():
        stats = fallback_data.get_dashboard_stats()
        return {
            "nodes": [
                {"type": "Person", "count": stats["total_experts"]},
                {"type": "Document", "count": stats["total_documents"]},
                {"type": "Skill", "count": stats["total_skills"]},
                {"type": "Project", "count": stats["total_projects"]}
            ],
            "relationships": []
        }

    query = """
    MATCH (n)
    WITH labels(n)[0] as type, count(*) as count
    RETURN collect({type: type, count: count}) as node_counts
    """

    result = db.run(query, {})
    record = result.single()

    rel_query = """
    MATCH ()-[r]->()
    WITH type(r) as type, count(*) as count
    RETURN collect({type: type, count: count}) as rel_counts
    """

    rel_result = db.run(rel_query, {})
    rel_record = rel_result.single()

    return {
        "nodes": record["node_counts"] if record else [],
        "relationships": rel_record["rel_counts"] if rel_record else []
    }
