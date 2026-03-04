"""
AI Chatbot Engine
Rule-based + keyword-matching chatbot that answers questions
about experts, skills, and documents from the JSONL dataset.
No external API keys required.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import random

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


class Chatbot:
    """Rule-based AI chatbot for ExpertLink knowledge queries."""

    def __init__(self):
        self._employees: List[Dict[str, Any]] = []
        self._skills: List[Dict[str, Any]] = []
        self._documents: List[Dict[str, Any]] = []
        self._projects: List[Dict[str, Any]] = []
        self._loaded = False

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _ensure_loaded(self):
        if self._loaded:
            return
        for fname, attr in [
            ("employees.jsonl", "_employees"),
            ("skills.jsonl", "_skills"),
            ("documents.jsonl", "_documents"),
            ("projects.jsonl", "_projects"),
        ]:
            filepath = DATA_DIR / fname
            records: List[Dict[str, Any]] = []
            if filepath.exists():
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            records.append(json.loads(line))
            setattr(self, attr, records)
        self._loaded = True

    # ------------------------------------------------------------------
    # Intent Detection
    # ------------------------------------------------------------------

    def _detect_intent(self, message: str) -> Tuple[str, List[str]]:
        """Detect user intent and extract keywords."""
        msg = message.lower().strip()

        # Expert-related
        expert_patterns = [
            r"who (?:knows|has|is|can|works)",
            r"find (?:me |an? )?expert",
            r"(?:expert|person|people|employee|developer|engineer).*(?:with|in|for|knows?)",
            r"(?:recommend|suggest).*expert",
            r"list all experts",
        ]
        for pattern in expert_patterns:
            if re.search(pattern, msg):
                keywords = self._extract_keywords(msg)
                return "find_expert", keywords

        # Skill-related
        skill_patterns = [
            r"(?:what|which|list|show).*skills?",
            r"(?:top|popular|trending|most).*skills?",
            r"skill.*(?:gap|missing|need|learn)",
        ]
        for pattern in skill_patterns:
            if re.search(pattern, msg):
                return "skill_info", self._extract_keywords(msg)

        # Document-related
        doc_patterns = [
            r"(?:find|search|get|show).*(?:document|doc|article|paper|resource)",
            r"(?:document|resource|article).*(?:about|on|for)",
        ]
        for pattern in doc_patterns:
            if re.search(pattern, msg):
                return "find_document", self._extract_keywords(msg)

        # Statistics
        stat_patterns = [
            r"how many",
            r"(?:total|count|number)",
            r"(?:stats?|statistics|overview|summary)",
        ]
        for pattern in stat_patterns:
            if re.search(pattern, msg):
                return "statistics", self._extract_keywords(msg)

        # Department-related
        dept_patterns = [
            r"(?:department|team|group)",
        ]
        for pattern in dept_patterns:
            if re.search(pattern, msg):
                return "department_info", self._extract_keywords(msg)

        # Greeting
        greet_patterns = [r"^(?:hi|hello|hey|bonjour|salut)", r"^good (?:morning|afternoon|evening)"]
        for pattern in greet_patterns:
            if re.search(pattern, msg):
                return "greeting", []

        # Help
        if re.search(r"^(?:help|\?|what can you)", msg):
            return "help", []

        # Default: try to find relevant data
        return "general_search", self._extract_keywords(msg)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from user message."""
        stop_words = {
            "who", "what", "where", "when", "how", "which", "can", "does",
            "do", "is", "are", "the", "a", "an", "and", "or", "but", "in",
            "on", "at", "to", "for", "of", "with", "by", "from", "has",
            "have", "had", "not", "no", "find", "me", "show", "get", "list",
            "tell", "about", "know", "knows", "that", "this", "any",
            "expert", "experts", "person", "people", "employee", "employees",
            "document", "documents", "skill", "skills", "please", "i", "want",
            "need", "looking", "search", "recommend", "suggest", "all", "top",
        }
        words = re.findall(r"[a-z]+", text.lower())
        return [w for w in words if w not in stop_words and len(w) > 1]

    # ------------------------------------------------------------------
    # Response Generation
    # ------------------------------------------------------------------

    def chat(self, message: str) -> Dict[str, Any]:
        """Process a user message and return an AI response."""
        self._ensure_loaded()
        intent, keywords = self._detect_intent(message)

        handlers = {
            "find_expert": self._handle_find_expert,
            "skill_info": self._handle_skill_info,
            "find_document": self._handle_find_document,
            "statistics": self._handle_statistics,
            "department_info": self._handle_department_info,
            "greeting": self._handle_greeting,
            "help": self._handle_help,
            "general_search": self._handle_general_search,
        }

        handler = handlers.get(intent, self._handle_general_search)
        response = handler(keywords)
        response["intent"] = intent
        response["keywords"] = keywords
        return response

    def _handle_greeting(self, keywords: List[str]) -> Dict[str, Any]:
        return {
            "message": "👋 Hello! I'm Veda, your AI assistant. I can help you find experts, discover skills, search documents, answer general knowledge questions, and explore your organization's knowledge graph. What would you like to know?",
            "data": None,
            "suggestions": [
                "Who knows Python?",
                "Show me top skills",
                "How many experts do we have?",
                "Find documents about machine learning",
            ],
        }

    def _handle_help(self, keywords: List[str]) -> Dict[str, Any]:
        return {
            "message": "🤖 Hi, I'm Veda! Here's what I can help with:\n\n"
                       "• Find Experts: 'Who knows Python?', 'Find me a data scientist'\n"
                       "• Skill Info: 'What are the top skills?', 'Trending skills'\n"
                       "• Documents: 'Find documents about AI', 'Resources on React'\n"
                       "• Statistics: 'How many experts?', 'Give me an overview'\n"
                       "• Departments: 'Show departments', 'Who is in Engineering?'",
            "data": None,
            "suggestions": [
                "Who knows Python?",
                "What are the most popular skills?",
                "Find documents about data science",
                "Show me statistics",
            ],
        }

    def _handle_find_expert(self, keywords: List[str]) -> Dict[str, Any]:
        if not keywords:
            # List some random experts
            sample = self._employees[:10]
            experts = []
            for emp in sample:
                experts.append({
                    "id": emp.get("id"),
                    "name": emp.get("name"),
                    "role": emp.get("role"),
                    "department": emp.get("department"),
                    "location": emp.get("location", ""),
                    "experience_years": emp.get("experience_years", 0),
                })
            return {
                "message": f"👥 Here are {len(experts)} experts in the organization:",
                "data": experts,
                "type": "experts",
                "suggestions": ["Who knows Python?", "Find React developers", "Show departments"],
            }

        # Build a skill name lookup for keyword matching
        skill_names = {s.get("name", "").lower(): s for s in self._skills}

        # Map skill categories to likely department/role keywords
        # Actual categories: Cloud Platforms, Data & AI, DevOps & Tools, Frameworks, Programming Languages, Security
        # Actual depts: AI Research, Architecture, Cloud Infrastructure, Data Science, DevOps, Engineering,
        #   Machine Learning, Mobile Development, Platform Engineering, Product Development, Quality Assurance,
        #   Security, Web Development
        category_to_dept_keywords = {
            "programming languages": ["engineering", "web development", "mobile", "developer", "backend",
                                       "frontend", "full stack", "lead", "senior", "staff", "architect"],
            "frameworks": ["web development", "mobile development", "frontend", "backend", "full stack",
                          "developer", "engineering", "product"],
            "data & ai": ["data science", "ai research", "machine learning", "data scientist",
                          "ml engineer", "research scientist", "analytics"],
            "devops & tools": ["devops", "platform engineering", "sre", "cloud infrastructure",
                               "devops engineer", "platform engineer"],
            "cloud platforms": ["cloud infrastructure", "cloud architect", "platform engineering",
                               "devops", "architecture", "solutions architect"],
            "security": ["security", "security engineer"],
        }

        # Check if any keyword matches a known skill
        matched_skill_cats = set()
        for kw in keywords:
            for sname, sdata in skill_names.items():
                if kw in sname:
                    cat = sdata.get("category", "")
                    if cat:
                        matched_skill_cats.add(cat.lower())

        matches = []
        for emp in self._employees:
            score = 0
            emp_text = " ".join([
                emp.get("name", ""),
                emp.get("role", ""),
                emp.get("department", ""),
                emp.get("location", ""),
            ]).lower()

            # Direct text match in employee metadata
            for kw in keywords:
                if kw in emp_text:
                    score += 3

            # Skill-category-to-department correlation
            if matched_skill_cats:
                for cat in matched_skill_cats:
                    dept_keywords = category_to_dept_keywords.get(cat, [])
                    for dk in dept_keywords:
                        if dk in emp_text:
                            score += 1
                            break  # One match per category is enough

                # Bonus for experienced employees when matching by skill
                exp = emp.get("experience_years", 0)
                if score > 0 and exp > 5:
                    score += 1

            if score > 0:
                matches.append((score, emp))

        matches.sort(key=lambda x: (-x[0], -x[1].get("experience_years", 0)))
        top = matches[:5]

        if not top:
            return {
                "message": f"I couldn't find any experts matching '{' '.join(keywords)}'. Try different keywords or browse departments.",
                "data": [],
                "suggestions": ["List all experts", "Show departments", "Show top skills"],
            }

        experts = []
        for _, emp in top:
            experts.append({
                "id": emp.get("id"),
                "name": emp.get("name"),
                "role": emp.get("role"),
                "department": emp.get("department"),
                "location": emp.get("location", ""),
                "experience_years": emp.get("experience_years", 0),
            })

        return {
            "message": f"🔍 Found {len(experts)} experts matching your query:",
            "data": experts,
            "type": "experts",
            "suggestions": [f"Tell me more about {experts[0]['name']}" if experts else "Show top skills"],
        }

    def _handle_skill_info(self, keywords: List[str]) -> Dict[str, Any]:
        # Use the skills catalog directly
        skills_list = self._skills

        if keywords:
            filtered = [
                s for s in skills_list
                if any(kw in s.get("name", "").lower() or kw in s.get("category", "").lower() for kw in keywords)
            ]
            if filtered:
                skills_list = filtered

        # Sort by demand (popularity)
        skills_list = sorted(skills_list, key=lambda s: s.get("demand", 0), reverse=True)
        top = skills_list[:10]

        skills_data = [
            {
                "skill": s.get("name", ""),
                "category": s.get("category", ""),
                "level": s.get("level", ""),
                "demand": s.get("demand", 0),
            }
            for s in top
        ]

        if not skills_data:
            return {
                "message": "No skills found matching your criteria.",
                "data": [],
                "type": "skills",
                "suggestions": ["Show all skills", "Show statistics"],
            }

        return {
            "message": f"📊 Top {len(skills_data)} skills in the organization (sorted by demand):",
            "data": skills_data,
            "type": "skills",
            "suggestions": [f"Who knows {top[0].get('name', '')}?" if top else "Show statistics"],
        }

    def _handle_find_document(self, keywords: List[str]) -> Dict[str, Any]:
        if not keywords:
            # Show top-rated recent documents
            recent = sorted(self._documents, key=lambda d: d.get("rating", 0), reverse=True)[:5]
            docs = [
                {
                    "id": d.get("id"),
                    "title": d.get("title"),
                    "topic": d.get("topic"),
                    "rating": d.get("rating"),
                    "views": d.get("views", 0),
                }
                for d in recent
            ]
            return {
                "message": "📄 Here are the top-rated documents:",
                "data": docs,
                "type": "documents",
                "suggestions": ["Find documents about Python", "Resources on AI"],
            }

        matches = []
        for doc in self._documents:
            doc_text = " ".join([
                doc.get("title", ""),
                doc.get("topic", ""),
                doc.get("abstract", ""),
                doc.get("content", "")[:200],
            ]).lower()
            score = sum(1 for kw in keywords if kw in doc_text)
            if score > 0:
                matches.append((score, doc))

        matches.sort(key=lambda x: (-x[0], -x[1].get("rating", 0)))
        top = matches[:5]

        if not top:
            return {
                "message": f"No documents found for '{' '.join(keywords)}'.",
                "data": [],
                "suggestions": ["Show all documents", "Find experts instead"],
            }

        docs = [
            {
                "id": d.get("id"),
                "title": d.get("title"),
                "topic": d.get("topic"),
                "rating": d.get("rating"),
                "views": d.get("views", 0),
            }
            for _, d in top
        ]
        return {
            "message": f"📄 Found {len(docs)} documents matching your query:",
            "data": docs,
            "type": "documents",
            "suggestions": [],
        }

    def _handle_statistics(self, keywords: List[str]) -> Dict[str, Any]:
        dept_counts = Counter(emp.get("department", "Unknown") for emp in self._employees)

        # Skill categories from the skills catalog
        skill_categories = Counter(s.get("category", "Other") for s in self._skills)
        top_skill = max(self._skills, key=lambda s: s.get("demand", 0)) if self._skills else None

        # Location distribution
        location_counts = Counter(emp.get("location", "Unknown") for emp in self._employees)

        # Average experience
        exp_years = [emp.get("experience_years", 0) for emp in self._employees]
        avg_exp = round(sum(exp_years) / len(exp_years), 1) if exp_years else 0

        stats = {
            "total_experts": len(self._employees),
            "total_documents": len(self._documents),
            "total_skills": len(self._skills),
            "total_projects": len(self._projects),
            "departments": len(dept_counts),
            "locations": len(location_counts),
            "avg_experience_years": avg_exp,
            "top_department": dept_counts.most_common(1)[0] if dept_counts else None,
            "top_skill": {"name": top_skill.get("name"), "demand": top_skill.get("demand")} if top_skill else None,
            "skill_categories": dict(skill_categories),
        }

        top_dept_name = stats["top_department"][0] if stats["top_department"] else "N/A"
        top_dept_count = stats["top_department"][1] if stats["top_department"] else 0
        top_skill_name = stats["top_skill"]["name"] if stats["top_skill"] else "N/A"

        msg = (
            f"📊 Organization Overview:\n\n"
            f"• {stats['total_experts']} Experts (avg {avg_exp} years experience)\n"
            f"• {stats['total_documents']} Documents\n"
            f"• {stats['total_skills']} Skills tracked across {len(skill_categories)} categories\n"
            f"• {stats['total_projects']} Projects\n"
            f"• {stats['departments']} Departments (largest: {top_dept_name} with {top_dept_count} members)\n"
            f"• {stats['locations']} Locations worldwide\n"
            f"• Most in-demand skill: {top_skill_name}"
        )

        return {
            "message": msg,
            "data": stats,
            "type": "statistics",
            "suggestions": ["Show top skills", "List departments", "Find experts"],
        }

    def _handle_department_info(self, keywords: List[str]) -> Dict[str, Any]:
        dept_data: Dict[str, List[Dict]] = {}
        for emp in self._employees:
            dept = emp.get("department", "Unknown")
            if dept not in dept_data:
                dept_data[dept] = []
            dept_data[dept].append({
                "name": emp.get("name"),
                "role": emp.get("role"),
                "experience_years": emp.get("experience_years", 0),
            })

        if keywords:
            filtered = {k: v for k, v in dept_data.items() if any(kw in k.lower() for kw in keywords)}
            if filtered:
                dept_data = filtered

        depts = [
            {"department": dept, "member_count": len(members), "members": members[:3]}
            for dept, members in dept_data.items()
        ]
        depts.sort(key=lambda x: x["member_count"], reverse=True)

        return {
            "message": f"🏢 Found {len(depts)} departments:",
            "data": depts[:10],
            "type": "departments",
            "suggestions": [],
        }

    def _handle_general_search(self, keywords: List[str]) -> Dict[str, Any]:
        if not keywords:
            return self._handle_help([])

        # Try to match across all entities
        results = {"experts": [], "skills": [], "documents": []}

        for emp in self._employees[:50]:
            emp_text = f"{emp.get('name', '')} {emp.get('role', '')} {emp.get('department', '')}".lower()
            if any(kw in emp_text for kw in keywords):
                results["experts"].append({"name": emp.get("name"), "role": emp.get("role")})
                if len(results["experts"]) >= 3:
                    break

        for skill in self._skills:
            skill_text = f"{skill.get('name', '')} {skill.get('category', '')}".lower()
            if any(kw in skill_text for kw in keywords):
                results["skills"].append({"name": skill.get("name"), "category": skill.get("category")})
                if len(results["skills"]) >= 3:
                    break

        for doc in self._documents[:50]:
            doc_text = f"{doc.get('title', '')} {doc.get('topic', '')}".lower()
            if any(kw in doc_text for kw in keywords):
                results["documents"].append({"title": doc.get("title"), "topic": doc.get("topic")})
                if len(results["documents"]) >= 3:
                    break

        parts = []
        if results["experts"]:
            parts.append(f"{len(results['experts'])} experts")
        if results["skills"]:
            parts.append(f"{len(results['skills'])} skills")
        if results["documents"]:
            parts.append(f"{len(results['documents'])} documents")

        if parts:
            msg = f"🔍 Found {', '.join(parts)} matching '{' '.join(keywords)}':"
        else:
            msg = f"I couldn't find results for '{' '.join(keywords)}'. Try rephrasing your question."

        return {
            "message": msg,
            "data": results,
            "type": "mixed",
            "suggestions": ["Try: Who knows Python?", "Try: Show me statistics"],
        }


# Singleton
chatbot = Chatbot()
