"""
Pydantic models for AI/ML endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ── Expert Recommendation ──────────────────────────────────────────

class RecommendExpertsRequest(BaseModel):
    query: str = Field(..., description="Free-text query (e.g. 'python developer', 'data scientist')")
    top_k: int = Field(10, ge=1, le=50, description="Number of results to return")


class RecommendedExpert(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    experience_years: int = 0
    expertise_level: int = 1
    similarity_score: float = 0.0
    skills: List[str] = []


class RecommendExpertsResponse(BaseModel):
    query: str
    results: List[RecommendedExpert]
    total_results: int
    model: str = "TF-IDF + Cosine Similarity"


# ── Document Classification ────────────────────────────────────────

class ClassifyDocumentRequest(BaseModel):
    title: str = Field(..., description="Document title")
    content: str = Field("", description="Document content/body text")


class PredictionDetail(BaseModel):
    topic: str
    confidence: float


class ClassifyDocumentResponse(BaseModel):
    predicted_topic: str
    confidence: float
    all_predictions: List[PredictionDetail]
    model: str = "TF-IDF + Logistic Regression"


# ── Skill Gap Analysis ─────────────────────────────────────────────

class SkillGapItem(BaseModel):
    skill: str
    category: str = "General"
    relevance_score: float = 0.0
    reason: str = ""


class SkillGapResponse(BaseModel):
    expert_id: str
    expert_name: str = "Unknown"
    current_skills: List[str] = []
    recommended_skills: List[SkillGapItem] = []
    num_similar_experts_analyzed: int = 0


# ── Skill Trends ───────────────────────────────────────────────────

class SkillTrendItem(BaseModel):
    skill: str
    expert_count: int
    adoption_rate: float
    average_level: float


class SkillTrendsResponse(BaseModel):
    total_experts: int
    total_unique_skills: int
    top_skills: List[SkillTrendItem]
    department_breakdown: Dict[str, Any] = {}


# ── Chatbot ────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message/question")
    conversation_id: Optional[str] = Field(None, description="Unique conversation/session ID for memory isolation")


class ChatResponse(BaseModel):
    message: str
    intent: str = ""
    keywords: List[str] = []
    data: Optional[Any] = None
    type: Optional[str] = None
    suggestions: List[str] = []


# ── Model Stats ────────────────────────────────────────────────────

class ModelStatsResponse(BaseModel):
    recommender: Dict[str, Any] = {}
    classifier: Dict[str, Any] = {}
    skill_predictor: Dict[str, Any] = {}
    embedding_engine: Dict[str, Any] = {}


# ── Similarity ─────────────────────────────────────────────────────

class SimilarityRequest(BaseModel):
    text1: str
    text2: str


class SimilarityResponse(BaseModel):
    text1: str
    text2: str
    similarity: float
    interpretation: str
