from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional
from ..database import get_db, is_neo4j_available
from ..models.entities import Document, DocumentWithDetails, DocumentCreate, DocumentUpdate
from ..auth_utils import get_current_user
from .. import fallback_data
from uuid import uuid4

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("/search", response_model=List[Document])
async def search_documents(
    q: Optional[str] = Query(None, description="Full-text search query"),
    type: Optional[str] = Query(None, description="Filter by document type"),
    topic: Optional[str] = Query(None, description="Filter by topic"),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    limit: int = Query(20, le=100),
    skip: int = Query(0),
    db=Depends(get_db)
):
    """
    Search documents with full-text and filters.
    Uses: Requête Filter (WHERE with CONTAINS for text search)
    """
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        return fallback_data.search_documents(
            q=q, doc_type=type, topic=topic, 
            min_rating=min_rating, limit=limit, skip=skip
        )
    
    conditions = []
    params = {"limit": limit, "skip": skip}
    
    query = "MATCH (d:Document)"
    
    if q:
        conditions.append("(toLower(d.title) CONTAINS toLower($q) OR toLower(d.topic) CONTAINS toLower($q))")
        params["q"] = q
    if type:
        conditions.append("d.type = $type")
        params["type"] = type
    if topic:
        conditions.append("toLower(d.topic) CONTAINS toLower($topic)")
        params["topic"] = topic
    if min_rating:
        conditions.append("d.rating >= $min_rating")
        params["min_rating"] = min_rating
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += """
    RETURN d.id as id, 
           coalesce(d.title, 'Untitled') as title, 
           coalesce(d.type, 'Document') as type, 
           coalesce(d.topic, 'General') as topic,
           coalesce(d.author, 'Unknown') as author, 
           d.date as date, 
           coalesce(d.views, 0) as views, 
           coalesce(d.rating, 0.0) as rating,
           coalesce(d.created_at, d.date, '2020-01-01') as sort_date
    ORDER BY sort_date DESC, rating DESC
    SKIP $skip LIMIT $limit
    """
    
    result = db.run(query, params)
    return [dict(record) for record in result]


@router.get("/{doc_id}", response_model=DocumentWithDetails)
async def get_document(doc_id: str, db=Depends(get_db)):
    """
    Get document with author and related information.
    Uses: Requête Simple (basic retrieval with optional matches)
    """
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        doc = fallback_data.get_document_by_id(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc
    
    query = """
    MATCH (d:Document {id: $id})
    OPTIONAL MATCH (author:Person {id: d.author})
    OPTIONAL MATCH (d)-[:COVERS_TOPIC]->(s:Skill)
    WITH d, author,
         collect(DISTINCT {id: s.id, name: s.name}) as related_skills
    RETURN d.id as id, d.title as title, d.type as type, d.topic as topic,
           d.author as author, d.date as date, d.views as views, d.rating as rating,
           d.content as content,
           CASE WHEN author IS NOT NULL 
                THEN {id: author.id, name: author.name, department: author.department}
                ELSE null END as author_details,
           related_skills
    """
    
    result = db.run(query, {"id": doc_id})
    record = result.single()
    
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return dict(record)


@router.get("/{doc_id}/download")
async def download_document(doc_id: str, db=Depends(get_db)):
    """Download a simple text representation of the document metadata as a file attachment."""
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        doc = fallback_data.get_document_by_id(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        record = doc
    else:
        query = """
        MATCH (d:Document {id: $id})
        RETURN d.id as id, d.title as title, d.type as type, d.topic as topic,
               d.author as author, d.date as date, d.views as views, d.rating as rating
        """
        result = db.run(query, {"id": doc_id})
        record = result.single()
        if not record:
            raise HTTPException(status_code=404, detail="Document not found")
        record = dict(record)

    title = record.get("title") or "document"
    lines = [
        f"Title: {record.get('title')}",
        f"Type: {record.get('type')}",
        f"Topic: {record.get('topic')}",
        f"Author: {record.get('author')}",
        f"Date: {record.get('date')}",
        f"Views: {record.get('views')}",
        f"Rating: {record.get('rating')}",
    ]
    content = "\n".join(lines) + "\n"

    filename = f"{title.replace(' ', '_')}.txt"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    return StreamingResponse(
        iter([content]),
        media_type="text/plain; charset=utf-8",
        headers=headers,
    )


@router.get("/similar/{doc_id}")
async def get_similar_documents(
    doc_id: str,
    limit: int = Query(5, le=20),
    db=Depends(get_db)
):
    """
    Get similar documents based on shared topics/skills.
    Uses: Requête Chemin (path through shared concepts)
    """
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        doc = fallback_data.get_document_by_id(doc_id)
        if not doc:
            return []
        # Find documents with same topic
        all_docs = fallback_data.get_documents()
        similar = [d for d in all_docs if d.get("topic") == doc.get("topic") and d.get("id") != doc_id]
        return similar[:limit]
    
    query = """
    MATCH (d:Document {id: $id})
    MATCH (d)-[:COVERS_TOPIC]->(s:Skill)<-[:COVERS_TOPIC]-(similar:Document)
    WHERE similar.id <> d.id
    WITH similar, count(s) as shared_topics
    ORDER BY shared_topics DESC, similar.rating DESC
    LIMIT $limit
    RETURN similar.id as id, similar.title as title, similar.type as type,
           similar.rating as rating, shared_topics
    """
    
    result = db.run(query, {"id": doc_id, "limit": limit})
    return [dict(record) for record in result]


@router.get("/types/list")
async def get_document_types(db=Depends(get_db)):
    """Get all unique document types."""
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        docs = fallback_data.get_documents()
        types = list(set(d.get("type") for d in docs if d.get("type")))
        return sorted(types)
    
    query = """
    MATCH (d:Document)
    RETURN DISTINCT d.type as type
    ORDER BY type
    """
    result = db.run(query)
    return [record["type"] for record in result if record["type"]]


@router.get("/experts/{doc_id}")
async def get_document_experts(doc_id: str, db=Depends(get_db)):
    """
    Get experts related to a document's topic.
    Uses: Requête Chemin (document -> topic -> experts with that skill)
    """
    # Use fallback data if Neo4j is not available
    if not is_neo4j_available():
        doc = fallback_data.get_document_by_id(doc_id)
        if not doc:
            return []
        # Return top experts
        experts = fallback_data.search_experts(limit=10)
        return experts
    
    query = """
    MATCH (d:Document {id: $id})
    MATCH (d)-[:COVERS_TOPIC]->(s:Skill)<-[:HAS_SKILL]-(p:Person)
    WHERE p.expertise_level >= 3
    RETURN DISTINCT p.id as id, p.name as name, p.department as department,
           p.expertise_level as expertise_level, s.name as skill
    ORDER BY p.expertise_level DESC
    LIMIT 10
    """
    
    result = db.run(query, {"id": doc_id})
    return [dict(record) for record in result]


from ..ml.summarizer import summarizer
@router.post("", response_model=Document)
async def create_document(
    payload: DocumentCreate, 
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not is_neo4j_available():
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Auto-generate summary
    auto_summary = summarizer.summarize(payload.content)
    final_content = f"### AI Summary\n{auto_summary}\n\n---\n\n{payload.content}"

    doc_id = str(uuid4())
    query = (
        """
        CREATE (d:Document {
            id: $id, title: $title, type: $type, topic: $topic,
            author: $author, date: $date, views: $views, rating: $rating,
            content: $content, created_at: $created_at
        })
        WITH d
        OPTIONAL MATCH (s:Skill {name: $topic})
        FOREACH (_ IN CASE WHEN s IS NULL THEN [] ELSE [1] END |
          MERGE (d)-[:COVERS_TOPIC]->(s)
        )
        RETURN d.id as id, d.title as title, d.type as type, d.topic as topic,
               d.author as author, d.date as date, d.views as views, d.rating as rating,
               d.content as content
        """
    )
    from datetime import date, datetime
    params = {
        "id": doc_id,
        "title": payload.title,
        "type": payload.type,
        "topic": payload.topic,
        "author": payload.author,
        "date": payload.date or date.today().isoformat(),
        "created_at": datetime.now().isoformat(),
        "views": payload.views,
        "rating": payload.rating,
        "content": final_content,
    }
    result = db.run(query, params)
    record = result.single()
    return dict(record)


@router.put("/{doc_id}", response_model=Document)
async def update_document(
    doc_id: str, 
    payload: DocumentUpdate, 
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not is_neo4j_available():
        raise HTTPException(status_code=503, detail="Database not available")
    
    updates = {k: v for k, v in payload.dict().items() if v is not None}
    if not updates:
        # Nothing to update; return current document if exists
        get_query = (
            """
            MATCH (d:Document {id: $id})
            RETURN d.id as id, d.title as title, d.type as type, d.topic as topic,
                   d.author as author, d.date as date, d.views as views, d.rating as rating,
                   d.content as content
            """
        )
        res = db.run(get_query, {"id": doc_id})
        record = res.single()
        if not record:
            raise HTTPException(status_code=404, detail="Document not found")
        return dict(record)

    query = (
        """
        MATCH (d:Document {id: $id})
        SET d += $updates
        RETURN d.id as id, d.title as title, d.type as type, d.topic as topic,
               d.author as author, d.date as date, d.views as views, d.rating as rating,
               d.content as content
        """
    )
    params = {"id": doc_id, "updates": updates}
    result = db.run(query, params)
    record = result.single()
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    return dict(record)


@router.post("/backfill/content")
async def backfill_document_content(
    limit: int = Query(1000, le=10000), 
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Populate basic placeholder content for documents missing content.
    Returns the number of documents updated. Limited to avoid huge transactions.
    """
    if not is_neo4j_available():
        raise HTTPException(status_code=503, detail="Database not available")
    
    query = (
        """
        MATCH (d:Document)
        WHERE d.content IS NULL OR d.content = ""
        WITH d LIMIT $limit
        SET d.content = 'This document "' + coalesce(d.title,'Untitled') + '" covers ' + coalesce(d.topic,'General') + '.'
        RETURN count(d) AS updated
        """
    )
    res = db.run(query, {"limit": limit})
    rec = res.single()
    return {"updated": rec["updated"] if rec else 0}


@router.delete("/{doc_id}", status_code=204)
async def delete_document(
    doc_id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Delete a document.
    """
    if not is_neo4j_available():
        raise HTTPException(status_code=503, detail="Database not available")
    
    query = """
    MATCH (d:Document {id: $id})
    DETACH DELETE d
    """
    db.run(query, {"id": doc_id})
    return None
