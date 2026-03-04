"""
AI/ML API Router
Provides endpoints for expert recommendation, document classification,
skill gap analysis, chatbot, and model statistics.
"""

from fastapi import APIRouter, Query
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

router = APIRouter(prefix="/api/ai", tags=["ai"])


# ── Expert Recommendation ──────────────────────────────────────────

@router.post("/recommend-experts", response_model=RecommendExpertsResponse)
async def recommend_experts(request: RecommendExpertsRequest):
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
async def classify_document(request: ClassifyDocumentRequest):
    """
    Auto-classify a document by topic using TF-IDF + Logistic Regression.
    Returns predicted topic with confidence scores.
    """
    result = classifier.classify_document(request.title, request.content)
    return ClassifyDocumentResponse(**result)


@router.get("/classification-report")
async def get_classification_report():
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
async def get_skill_trends():
    """
    Analyze skill trends across the organization.
    Returns adoption rates, average levels, and department breakdown.
    """
    return skill_predictor.get_skill_trends()


# ── Veda: Intelligent AI Chatbot ───────────────────────────────────

from ..ml.graph_rag import graph_rag
import json as _json
from collections import Counter

# Conversation memory store (session-based, keyed by a simple counter)
_conversation_histories: dict = {}
_MAX_HISTORY = 20  # Max messages to keep per conversation


def _build_organization_context() -> str:
    """Build a rich context summary of the organization's data for GPT."""
    chatbot._ensure_loaded()

    # Employees summary
    total_employees = len(chatbot._employees)
    departments = Counter(e.get("department", "Unknown") for e in chatbot._employees)
    locations = Counter(e.get("location", "Unknown") for e in chatbot._employees)
    roles = Counter(e.get("role", "Unknown") for e in chatbot._employees)
    exp_years = [e.get("experience_years", 0) for e in chatbot._employees]
    avg_exp = round(sum(exp_years) / len(exp_years), 1) if exp_years else 0

    # Build employee directory (compact format for GPT)
    employee_entries = []
    for emp in chatbot._employees[:100]:  # Top 100 for context window
        skills_str = ", ".join(emp.get("skills", [])[:5]) if emp.get("skills") else "N/A"
        employee_entries.append(
            f"- {emp.get('name', 'N/A')} | {emp.get('role', 'N/A')} | {emp.get('department', 'N/A')} | "
            f"{emp.get('location', 'N/A')} | {emp.get('experience_years', 0)}yr exp | Skills: {skills_str}"
        )

    # Skills summary
    skill_names = [s.get("name", "") for s in chatbot._skills]
    skill_categories = Counter(s.get("category", "Other") for s in chatbot._skills)
    top_skills = sorted(chatbot._skills, key=lambda s: s.get("demand", 0), reverse=True)[:15]
    top_skills_str = ", ".join(f"{s.get('name', '')} (demand: {s.get('demand', 0)})" for s in top_skills)

    # Documents summary
    doc_topics = Counter(d.get("topic", "General") for d in chatbot._documents)
    top_docs = sorted(chatbot._documents, key=lambda d: d.get("rating", 0), reverse=True)[:10]
    doc_entries = []
    for doc in top_docs:
        doc_entries.append(f"- \"{doc.get('title', 'N/A')}\" (topic: {doc.get('topic', 'N/A')}, rating: {doc.get('rating', 0)})")

    # Projects summary
    project_entries = []
    for proj in chatbot._projects[:20]:
        members_str = ", ".join(proj.get("members", [])[:3]) if proj.get("members") else "N/A"
        tech_str = ", ".join(proj.get("technologies", [])[:5]) if proj.get("technologies") else "N/A"
        project_entries.append(
            f"- {proj.get('name', 'N/A')} ({proj.get('status', 'N/A')}) | Tech: {tech_str} | "
            f"Members: {members_str}"
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

EMPLOYEE DIRECTORY:
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
_org_context_cache = {"data": None, "timestamp": 0}


def _get_org_context() -> str:
    """Get cached organization context."""
    import time
    now = time.time()
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
    """Use GPT with full organization context to answer any question."""
    import os
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        # Get or create conversation history
        if conversation_id not in _conversation_histories:
            _conversation_histories[conversation_id] = []
        history = _conversation_histories[conversation_id]

        # Build messages with system prompt + conversation history
        org_context = _get_org_context()
        system_prompt = _build_system_prompt(org_context)

        messages = [{"role": "system", "content": system_prompt}]
        # Add conversation history (last N messages)
        messages.extend(history[-_MAX_HISTORY:])
        # Add current user message
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
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
            _conversation_histories[conversation_id] = history[-_MAX_HISTORY:]

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
        for emp in chatbot._employees:
            if emp.get("name", "").lower() in answer.lower():
                mentioned_employees.append({
                    "id": emp.get("id"),
                    "name": emp.get("name"),
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
        print(f"Veda GPT error: {e}")
        import traceback
        traceback.print_exc()
        return None


@router.post("/chatbot", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Veda — Intelligent AI Assistant for Nexora.
    GPT-first architecture with full organization data context.
    Falls back to rule-based engine when GPT is unavailable.
    """
    import os
    conversation_id = getattr(request, 'conversation_id', 'default') or 'default'

    # ── Primary: Veda AI (GPT with org context) ────────────────────
    if os.environ.get("OPENAI_API_KEY"):
        result = await _ask_veda(request.message, conversation_id)
        if result:
            return ChatResponse(**result)

    # ── Fallback: Rule-based engine ────────────────────────────────
    result = chatbot.chat(request.message)
    return ChatResponse(**result)


# ── Similarity ─────────────────────────────────────────────────────

@router.post("/text-similarity")
async def compute_text_similarity(request: SimilarityRequest):
    """Compute cosine similarity between two text strings."""
    return embedding_engine.compute_similarity(request.text1, request.text2)


# ── Model Stats ────────────────────────────────────────────────────

@router.get("/model-stats", response_model=ModelStatsResponse)
async def get_model_stats():
    """Get performance metrics and status for all ML models."""
    return ModelStatsResponse(
        recommender=recommender.get_model_info(),
        classifier=classifier.get_classification_report(),
        skill_predictor=skill_predictor.get_model_info(),
        embedding_engine=embedding_engine.get_model_info(),
    )


@router.post("/train-all")
async def train_all_models():
    """Train/retrain all ML models. Use after data updates."""
    results = {
        "recommender": recommender.train(),
        "classifier": classifier.train(),
        "skill_predictor": skill_predictor.train(),
        "embedding_engine": embedding_engine.train(),
    }
    return {"status": "completed", "results": results}
