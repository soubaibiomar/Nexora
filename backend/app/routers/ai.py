"""
AI/ML API Router
Provides endpoints for expert recommendation, document classification,
skill gap analysis, chatbot, and model statistics.
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional

from ..ml.recommender import recommender
from ..ml.classifier import classifier
from ..ml.skill_predictor import skill_predictor
from ..ml.chatbot import chatbot
from ..ml.embeddings import embedding_engine
from ..models.ai import (
    RecommendExpertsRequest, RecommendExpertsResponse,
    ClassifyDocumentRequest, ClassifyDocumentResponse,
    ChatRequest, ChatResponse,
    ModelStatsResponse,
    SimilarityRequest, SimilarityResponse,
)
from ..auth_guards import require_auth, require_admin

router = APIRouter(prefix="/api/ai", tags=["ai"])


# ── Expert Recommendation ──────────────────────────────────────────

@router.post("/recommend-experts", response_model=RecommendExpertsResponse)
async def recommend_experts(request: RecommendExpertsRequest, _user: dict = Depends(require_auth)):
    """
    ML-based expert recommendation using TF-IDF + Cosine Similarity.
    Returns ranked experts matching the free-text query.
    """
    results = recommender.recommend_experts(request.query, request.top_k)
    return RecommendExpertsResponse(
        query=request.query,
        results=results,
        total_results=len(results),
    )


@router.get("/similar-experts/{expert_id}")
async def find_similar_experts(
    expert_id: str,
    top_k: int = Query(5, ge=1, le=20),
):
    """Find experts similar to the given expert using collaborative profile analysis."""
    results = recommender.find_similar_experts(expert_id, top_k)
    return {
        "expert_id": expert_id,
        "similar_experts": results,
        "total": len(results),
        "model": "TF-IDF + Cosine Similarity",
    }


# ── Document Classification ────────────────────────────────────────

@router.post("/classify-document", response_model=ClassifyDocumentResponse)
async def classify_document(request: ClassifyDocumentRequest, _user: dict = Depends(require_auth)):
    """
    Auto-classify a document by topic using TF-IDF + Logistic Regression.
    Returns predicted topic with confidence scores.
    """
    result = classifier.classify_document(request.title, request.content)
    return ClassifyDocumentResponse(**result)


@router.get("/classification-report")
async def get_classification_report(_user: dict = Depends(require_auth)):
    """Get document classifier performance metrics."""
    return classifier.get_classification_report()


# ── Skill Gap Analysis ─────────────────────────────────────────────

@router.get("/skill-gaps/{expert_id}")
async def predict_skill_gaps(
    expert_id: str,
    top_k: int = Query(8, ge=1, le=20),
):
    """
    Predict skill gaps for an expert using collaborative filtering.
    Analyzes similar experts' skill profiles to recommend new skills.
    """
    return skill_predictor.predict_skill_gaps(expert_id, top_k)


@router.get("/skill-trends")
async def get_skill_trends(_user: dict = Depends(require_auth)):
    """
    Analyze skill trends across the organization.
    Returns adoption rates, average levels, and department breakdown.
    """
    return skill_predictor.get_skill_trends()


# ── Emerging & Predictive Skills ───────────────────────────────────

from ..ml.pagerank import expert_pagerank


@router.get("/emerging-skills")
async def get_emerging_skills(_user: dict = Depends(require_auth)):
    """
    Identify skills with the highest adoption growth rate.
    Compares skill adoption between recent hires vs older cohorts.
    """
    return skill_predictor.get_emerging_skills()


@router.get("/future-skills")
async def get_future_skills(
    months: int = Query(12, ge=3, le=24),
):
    """
    Predict which skills will be most in-demand in N months.
    Combines project demand trends with emerging-skill growth rates.
    """
    return skill_predictor.predict_future_skills(months)


@router.get("/expert-rank")
async def get_expert_rankings(
    q: Optional[str] = Query(None, description="Skill or role query to boost relevance"),
    department: Optional[str] = Query(None, description="Filter by department"),
    top_k: int = Query(20, ge=1, le=100),
):
    """
    PageRank-based expert influence scoring.
    Ranks experts by skill diversity, depth, project participation,
    document contributions, and graph connectivity.
    """
    return expert_pagerank.rank_experts(query=q, department=department, top_k=top_k)


@router.get("/cross-department-suggestions")
async def get_cross_department_suggestions(_user: dict = Depends(require_auth)):
    """
    Find departments with complementary skill profiles for collaboration.
    Identifies potential cross-team projects and mentoring opportunities.
    """
    return skill_predictor.get_cross_department_suggestions()


@router.get("/personalized-recommendations/{user_id}")
async def get_personalized_recommendations(
    user_id: str,
    top_k: int = Query(8, ge=1, le=20),
):
    """
    Personalized skill recommendations for a specific user.
    Factors in role, department affinity, and current skill level.
    """
    gaps = skill_predictor.predict_skill_gaps(user_id, top_k)
    trends = skill_predictor.get_skill_trends()

    # Cross-reference with trending skills
    trending_names = {s["skill"] for s in trends.get("top_skills", [])[:10]}
    for rec in gaps.get("recommended_skills", []):
        rec["is_trending"] = rec["skill"] in trending_names

    return gaps



from ..ml.graph_rag import graph_rag
import json as _json
from collections import Counter
import time as _time
import uuid as _uuid

# ---------------------------------------------------------------------------
# Conversation memory store (keyed by conversation_id)
# ---------------------------------------------------------------------------
_conversation_histories: dict = {}
_MAX_HISTORY = 20  # Max messages to keep per conversation
_MAX_CONVERSATIONS = 200  # Limit total stored conversations to prevent memory leak


def _cleanup_old_conversations():
    """Remove oldest conversations if we exceed the maximum."""
    if len(_conversation_histories) > _MAX_CONVERSATIONS:
        # Sort by last activity and keep only the most recent
        sorted_ids = sorted(
            _conversation_histories.keys(),
            key=lambda k: _conversation_histories[k].get("_last_active", 0),
        )
        for cid in sorted_ids[: len(sorted_ids) - _MAX_CONVERSATIONS]:
            del _conversation_histories[cid]


def _build_organization_context() -> str:
    """Build a rich context summary of the organization's data for the LLM."""
    chatbot._ensure_loaded()

    # Employees summary
    total_employees = len(chatbot._employees)
    departments = Counter(e.get("department", "Unknown") for e in chatbot._employees)
    locations = Counter(e.get("location", "Unknown") for e in chatbot._employees)
    exp_years = [e.get("experience_years", 0) for e in chatbot._employees]
    avg_exp = round(sum(exp_years) / len(exp_years), 1) if exp_years else 0

    # Build employee directory (compact format — cap at 50 to stay within token limits)
    employee_entries = []
    for emp in chatbot._employees[:50]:
        skills_raw = emp.get("skills", [])
        if skills_raw and isinstance(skills_raw[0], dict):
            skills_str = ", ".join(s.get("name", "") for s in skills_raw[:6])
        else:
            skills_str = ", ".join(str(s) for s in skills_raw[:6])
        employee_entries.append(
            f"- {emp.get('name', 'N/A')} | {emp.get('role', 'N/A')} | {emp.get('department', 'N/A')} | "
            f"{emp.get('location', 'N/A')} | {emp.get('experience_years', 0)}yr | Skills: {skills_str}"
        )

    # Skills summary
    skill_categories = Counter(s.get("category", "Other") for s in chatbot._skills)
    top_skills = sorted(chatbot._skills, key=lambda s: s.get("demand", 0), reverse=True)[:15]
    top_skills_str = ", ".join(f"{s.get('name', '')} (demand: {s.get('demand', 0)})" for s in top_skills)

    # Documents summary
    doc_topics = Counter(d.get("topic", "General") for d in chatbot._documents)
    top_docs = sorted(chatbot._documents, key=lambda d: d.get("rating", 0), reverse=True)[:10]
    doc_entries = [
        f"- \"{d.get('title', 'N/A')}\" (topic: {d.get('topic', 'N/A')}, rating: {d.get('rating', 0)})"
        for d in top_docs
    ]

    # Projects summary
    project_entries = []
    for proj in chatbot._projects[:15]:
        tech_str = proj.get("tech_stack", "N/A")
        members = proj.get("team_members", [])
        project_entries.append(
            f"- {proj.get('name', 'N/A')} ({proj.get('status', 'N/A')}) | Tech: {tech_str} | "
            f"Team size: {proj.get('team_size', len(members))}"
        )

    context = f"""=== NEXORA ORGANIZATION DATA ===

OVERVIEW:
- {total_employees} employees across {len(departments)} departments and {len(locations)} locations
- Average experience: {avg_exp} years
- {len(chatbot._skills)} skills tracked across {len(skill_categories)} categories
- {len(chatbot._documents)} documents in the knowledge base
- {len(chatbot._projects)} projects

DEPARTMENTS (with member counts):
{chr(10).join(f'- {dept}: {count} members' for dept, count in departments.most_common(15))}

TOP IN-DEMAND SKILLS:
{top_skills_str}

SKILL CATEGORIES:
{', '.join(f'{cat} ({count})' for cat, count in skill_categories.most_common())}

EMPLOYEE DIRECTORY (sample of {len(employee_entries)}):
{chr(10).join(employee_entries)}

TOP-RATED DOCUMENTS:
{chr(10).join(doc_entries)}

DOCUMENT TOPICS:
{', '.join(f'{topic} ({count})' for topic, count in doc_topics.most_common(10))}

PROJECTS:
{chr(10).join(project_entries)}
"""
    return context


# Cache the organization context (rebuild every 5 minutes)
_org_context_cache: dict = {"data": None, "timestamp": 0}


def _get_org_context() -> str:
    """Get cached organization context."""
    now = _time.time()
    if _org_context_cache["data"] is None or now - _org_context_cache["timestamp"] > 300:
        _org_context_cache["data"] = _build_organization_context()
        _org_context_cache["timestamp"] = now
    return _org_context_cache["data"]


def _build_system_prompt(org_context: str) -> str:
    """Build Veda's system prompt with organization context."""
    return f"""You are Veda — an intelligent, professional AI assistant for the Nexora platform (a Knowledge Cartography & Expert Discovery system).

You have deep knowledge of the organization's employees, skills, documents, and projects. You can also answer general knowledge questions about companies, technologies, industries, and more.

{org_context}

=== YOUR CAPABILITIES ===
1. FIND EXPERTS: Search employees by name, skill, department, role, location, or experience
2. SKILL ANALYSIS: Identify top skills, skill gaps, trending skills, skill distribution
3. DOCUMENT SEARCH: Find documents by topic, title, or content area
4. PROJECT INFO: Provide details about active projects, team compositions, technologies used
5. STATISTICS: Organization overview, department breakdowns, experience distributions
6. CROSS-REFERENCE: Connect experts to projects, skills to departments, etc.
7. GENERAL KNOWLEDGE: Answer questions about companies, technologies, industries, concepts
8. RECOMMENDATIONS: Suggest experts for projects, learning paths, team compositions

=== RESPONSE FORMAT ===
- Be concise but thorough (3-6 sentences for general answers, more for data-heavy queries)
- Use emojis sparingly for visual clarity (📊 for stats, 🔍 for search, 👤 for experts, etc.)
- When listing experts, include: name, role, department, experience years
- When listing skills, include: name, category, demand level
- When listing documents, include: title, topic, rating
- Be conversational and helpful — you're a knowledgeable colleague, not a search engine

=== IMPORTANT ===
- ALWAYS search the employee directory data above before saying you can't find someone
- If asked about a skill, check which employees have it and which projects use it
- If a question is ambiguous, provide the most helpful interpretation
- You can make connections and insights the user didn't explicitly ask for
- For general knowledge questions, provide accurate, factual information

IMPORTANT: At the end of EVERY response, add a line with exactly this format:
SUGGESTIONS: ["suggestion 1", "suggestion 2", "suggestion 3"]
These must be 3 short, relevant follow-up questions. Make them specific to the conversation context.
For internal queries, suggest related internal searches. For general knowledge, suggest related topics."""


async def _ask_veda(message: str, conversation_id: str = "default") -> dict:
    """Use Groq LLM with full organization context to answer any question."""
    import os
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None

    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        # Get or create conversation history (isolated by conversation_id)
        if conversation_id not in _conversation_histories:
            _conversation_histories[conversation_id] = {"messages": [], "_last_active": _time.time()}
            _cleanup_old_conversations()

        conv = _conversation_histories[conversation_id]
        conv["_last_active"] = _time.time()
        history = conv["messages"]

        # Build messages with system prompt + conversation history
        org_context = _get_org_context()
        system_prompt = _build_system_prompt(org_context)

        messages = [{"role": "system", "content": system_prompt}]
        # Add conversation history (last N messages)
        messages.extend(history[-_MAX_HISTORY:])
        # Add current user message
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=800,
            temperature=0.7,
        )
        raw = response.choices[0].message.content.strip()

        # Save to conversation history
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": raw})
        # Trim history if too long
        if len(history) > _MAX_HISTORY * 2:
            conv["messages"] = history[-_MAX_HISTORY:]

        # Parse suggestions from the response
        suggestions = []
        answer = raw
        if "SUGGESTIONS:" in raw:
            parts = raw.split("SUGGESTIONS:", 1)
            answer = parts[0].strip()
            try:
                suggestions = _json.loads(parts[1].strip())
            except Exception:
                suggestions = []

        if not suggestions:
            suggestions = [
                "Who are the top experts?",
                "What skills are most in demand?",
                "Show me organization statistics"
            ]

        # Try to detect if the response contains structured data (experts, skills, etc.)
        data = None
        intent = "veda_ai"

        # Check if response mentions specific employees from our data
        mentioned_employees = []
        answer_lower = answer.lower()
        for emp in chatbot._employees:
            emp_name = emp.get("name", "")
            if emp_name and emp_name.lower() in answer_lower:
                mentioned_employees.append({
                    "id": emp.get("id"),
                    "name": emp_name,
                    "role": emp.get("role"),
                    "department": emp.get("department"),
                    "location": emp.get("location", ""),
                    "experience_years": emp.get("experience_years", 0),
                })
        if mentioned_employees:
            data = mentioned_employees
            intent = "veda_experts"

        return {
            "message": answer,
            "data": data,
            "intent": intent,
            "keywords": [],
            "suggestions": suggestions[:3],
        }
    except Exception as e:
        print(f"Veda Groq error: {e}")
        import traceback
        traceback.print_exc()
        return None


@router.post("/chatbot", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest, _user: dict = Depends(require_auth)):
    """
    Veda — Intelligent AI Assistant for Nexora.
    Groq LLM-first architecture with full organization data context.
    Falls back to rule-based engine when Groq is unavailable.
    """
    import os

    # Use provided conversation_id, or generate a new one
    conversation_id = request.conversation_id or str(_uuid.uuid4())

    # ── Primary: Veda AI (Groq LLM with org context) ───────────────
    if os.environ.get("GROQ_API_KEY"):
        result = await _ask_veda(request.message, conversation_id)
        if result:
            return ChatResponse(**result)

    # ── Fallback: Rule-based engine ────────────────────────────────
    result = chatbot.chat(request.message)
    return ChatResponse(**result)


# ── Similarity ─────────────────────────────────────────────────────

@router.post("/text-similarity")
async def compute_text_similarity(request: SimilarityRequest, _user: dict = Depends(require_auth)):
    """Compute cosine similarity between two text strings."""
    return embedding_engine.compute_similarity(request.text1, request.text2)


# ── Model Stats ────────────────────────────────────────────────────

@router.get("/model-stats", response_model=ModelStatsResponse)
async def get_model_stats(_user: dict = Depends(require_auth)):
    """Get performance metrics and status for all ML models."""
    return ModelStatsResponse(
        recommender=recommender.get_model_info(),
        classifier=classifier.get_classification_report(),
        skill_predictor=skill_predictor.get_model_info(),
        embedding_engine=embedding_engine.get_model_info(),
    )


@router.post("/train-all")
async def train_all_models(_user: dict = Depends(require_auth)):
    """Train/retrain all ML models. Use after data updates."""
    results = {
        "recommender": recommender.train(),
        "classifier": classifier.train(),
        "skill_predictor": skill_predictor.train(),
        "embedding_engine": embedding_engine.train(),
    }
    return {"status": "completed", "results": results}
