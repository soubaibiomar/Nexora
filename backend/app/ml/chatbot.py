"""
AI Chatbot Engine — Veda (Rule-Based Fallback)
Keyword-matching + skill-aware chatbot that answers questions
about experts, skills, projects, and documents from the JSONL dataset.
Serves as fallback when no LLM API key is configured.
No external API keys required.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import random

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"

# ---------------------------------------------------------------------------
# Common bigrams that should be kept together during keyword extraction
# ---------------------------------------------------------------------------
_BIGRAMS = {
    "machine learning", "deep learning", "data science", "data engineering",
    "artificial intelligence", "natural language", "computer vision",
    "cloud computing", "web development", "mobile development",
    "cyber security", "project management", "full stack", "front end",
    "back end", "devops engineer", "quality assurance", "google cloud",
    "real time", "big data",
}


class Chatbot:
    """Rule-based AI chatbot for Nexora knowledge queries."""

    def __init__(self):
        self._employees: List[Dict[str, Any]] = []
        self._skills: List[Dict[str, Any]] = []
        self._documents: List[Dict[str, Any]] = []
        self._projects: List[Dict[str, Any]] = []
        self._loaded = False
        # Pre-built index: skill_name_lower -> list of employee dicts
        self._skill_to_employees: Dict[str, List[Dict[str, Any]]] = {}

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

        # Build skill -> employees index for fast lookups
        self._skill_to_employees.clear()
        for emp in self._employees:
            for skill_entry in emp.get("skills", []):
                skill_name = skill_entry.get("name", "") if isinstance(skill_entry, dict) else str(skill_entry)
                key = skill_name.lower()
                if key:
                    self._skill_to_employees.setdefault(key, []).append(emp)

        self._loaded = True

    # ------------------------------------------------------------------
    # Intent Detection
    # ------------------------------------------------------------------

    def _detect_intent(self, message: str) -> Tuple[str, List[str]]:
        """Detect user intent and extract keywords."""
        msg = message.lower().strip()

        # Expert-related (EN + FR)
        expert_patterns = [
            r"who (?:knows|has|is|can|works)",
            r"find (?:me |an? )?expert",
            r"find (?:me |a )?collaborat",
            r"(?:expert|person|people|employee|developer|engineer).*(?:with|in|for|knows?)",
            r"(?:recommend|suggest).*(?:expert|collaborat|colleague)",
            r"(?:help|aide).*(?:find|trouver).*(?:collaborat|collègue|expert|colleague)",
            r"list all experts",
            # French patterns
            r"(?:qui|quel).*(?:expert|connait|maîtrise|compétence)",
            r"(?:trouver|chercher).*(?:expert|développeur|ingénieur|collaborat)",
        ]
        for pattern in expert_patterns:
            if re.search(pattern, msg):
                keywords = self._extract_keywords(msg)
                return "find_expert", keywords

        # Project-related (EN + FR)
        # NOTE: Checked AFTER expert so "find a collaborator for my project" -> expert
        project_patterns = [
            r"(?:show|find|list|get).*(?:projects?)",
            r"(?:projects?).*(?:about|related|using|with)",
            r"(?:montre|affiche|liste).*(?:projets?)",
            r"(?:projets?).*(?:liés?|sur|utilisant)",
        ]
        for pattern in project_patterns:
            if re.search(pattern, msg):
                return "find_project", self._extract_keywords(msg)

        # Skill-related (EN + FR)
        skill_patterns = [
            r"(?:what|which|list|show).*skills?",
            r"(?:top|popular|trending|most).*skills?",
            r"skill.*(?:gap|missing|need|learn)",
            r"(?:comp[eé]tences?|skills?).*(?:demand[eé]es?|populaires?|tendance)",
            r"(?:quelles?).*comp[eé]tences?",
        ]
        for pattern in skill_patterns:
            if re.search(pattern, msg):
                return "skill_info", self._extract_keywords(msg)

        # Document-related (EN + FR)
        doc_patterns = [
            r"(?:find|search|get|show).*(?:document|doc|article|paper|resource)",
            r"(?:document|resource|article).*(?:about|on|for)",
            r"(?:trouver|chercher|afficher).*(?:document|article|ressource)",
        ]
        for pattern in doc_patterns:
            if re.search(pattern, msg):
                return "find_document", self._extract_keywords(msg)

        # Statistics (EN + FR)
        stat_patterns = [
            r"how many",
            r"(?:total|count|number)",
            r"(?:stats?|statistics|overview|summary)",
            r"(?:combien|statistiques?|aperçu|résumé)",
        ]
        for pattern in stat_patterns:
            if re.search(pattern, msg):
                return "statistics", self._extract_keywords(msg)

        # Department-related (EN + FR)
        dept_patterns = [
            r"(?:department|team|group)",
            r"(?:département|équipe|service)",
        ]
        for pattern in dept_patterns:
            if re.search(pattern, msg):
                return "department_info", self._extract_keywords(msg)

        # Greeting (EN + FR)
        greet_patterns = [
            r"^(?:hi|hello|hey|bonjour|salut|bonsoir)",
            r"^good (?:morning|afternoon|evening)",
        ]
        for pattern in greet_patterns:
            if re.search(pattern, msg):
                return "greeting", []

        # Help
        if re.search(r"^(?:help|\?|what can you|aide|comment)", msg):
            return "help", []

        # Default: try to find relevant data
        return "general_search", self._extract_keywords(msg)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from user message, preserving bigrams."""
        stop_words = {
            "who", "what", "where", "when", "how", "which", "can", "does",
            "do", "is", "are", "the", "a", "an", "and", "or", "but", "in",
            "on", "at", "to", "for", "of", "with", "by", "from", "has",
            "have", "had", "not", "no", "find", "me", "show", "get", "list",
            "tell", "about", "know", "knows", "that", "this", "any",
            "expert", "experts", "person", "people", "employee", "employees",
            "document", "documents", "skill", "skills", "please", "i", "want",
            "need", "looking", "search", "recommend", "suggest", "all", "top",
            "project", "projects",
            # French stop words
            "qui", "que", "quel", "quelle", "quels", "quelles", "est", "sont",
            "les", "des", "une", "un", "le", "la", "dans", "pour", "avec",
            "sur", "par", "mon", "mes", "ce", "cette", "ces", "du", "au",
            "je", "tu", "il", "nous", "vous", "ils", "trouver", "chercher",
            "montrer", "afficher", "aide", "aider", "moi",
        }

        lower = text.lower()
        result = []

        # First, extract bigrams
        for bigram in _BIGRAMS:
            if bigram in lower:
                result.append(bigram)
                # Remove the bigram from the text to avoid double-counting
                lower = lower.replace(bigram, " ")

        # Then extract remaining single words
        words = re.findall(r"[a-zàâäéèêëïîôùûüÿç]+", lower)
        for w in words:
            if w not in stop_words and len(w) > 1 and w not in " ".join(result):
                result.append(w)

        return result

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
            "find_project": self._handle_find_project,
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
            "message": "👋 Hello! I'm Veda, your AI assistant. I can help you find experts, discover skills, search documents, explore projects, and answer questions about the organization. What would you like to know?",
            "data": None,
            "suggestions": [
                "Who knows Python?",
                "Show me top skills",
                "Show me projects related to data science",
            ],
        }

    def _handle_help(self, keywords: List[str]) -> Dict[str, Any]:
        return {
            "message": "🤖 Hi, I'm Veda! Here's what I can help with:\n\n"
                       "• Find Experts: 'Who knows Python?', 'Find me a data scientist'\n"
                       "• Skill Info: 'What are the top skills?', 'Trending skills'\n"
                       "• Projects: 'Show projects about data science', 'Projects using React'\n"
                       "• Documents: 'Find documents about AI', 'Resources on React'\n"
                       "• Statistics: 'How many experts?', 'Give me an overview'\n"
                       "• Departments: 'Show departments', 'Who is in Engineering?'",
            "data": None,
            "suggestions": [
                "Who knows Machine Learning?",
                "What are the most popular skills?",
                "Show me projects related to AI",
                "Find documents about data science",
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

        matches = []
        for emp in self._employees:
            score = 0

            # --- Direct text match in employee metadata ---
            emp_text = " ".join([
                emp.get("name", ""),
                emp.get("role", ""),
                emp.get("department", ""),
                emp.get("location", ""),
            ]).lower()

            for kw in keywords:
                if kw in emp_text:
                    score += 3

            # --- Skill-based matching (the key improvement) ---
            emp_skills = emp.get("skills", [])
            emp_skill_names = []
            for s in emp_skills:
                if isinstance(s, dict):
                    emp_skill_names.append(s.get("name", "").lower())
                else:
                    emp_skill_names.append(str(s).lower())

            for kw in keywords:
                for skill_name in emp_skill_names:
                    if kw in skill_name:
                        # Bonus based on skill level
                        skill_level = 1
                        for s in emp_skills:
                            if isinstance(s, dict) and s.get("name", "").lower() == skill_name:
                                skill_level = s.get("level", 1)
                                break
                        score += 2 + skill_level  # Higher level = higher score
                        break  # One match per keyword is enough

            # Bonus for experienced employees
            exp = emp.get("experience_years", 0)
            if score > 0 and exp > 8:
                score += 2
            elif score > 0 and exp > 5:
                score += 1

            if score > 0:
                matches.append((score, emp))

        matches.sort(key=lambda x: (-x[0], -x[1].get("experience_years", 0)))
        top = matches[:5]

        # If we have keywords but found 0 matches, fallback to general experts
        # e.g., the keyword was "collaborator" which no one has in their profile
        if not top:
            return self._handle_find_expert([])

        experts = []
        for _, emp in top:
            # Include matched skills in the response
            emp_skills = emp.get("skills", [])
            skill_list = []
            for s in emp_skills:
                if isinstance(s, dict):
                    skill_list.append(s.get("name", ""))
                else:
                    skill_list.append(str(s))

            experts.append({
                "id": emp.get("id"),
                "name": emp.get("name"),
                "role": emp.get("role"),
                "department": emp.get("department"),
                "location": emp.get("location", ""),
                "experience_years": emp.get("experience_years", 0),
                "skills": skill_list[:8],  # Top 8 skills for context
            })

        keyword_str = ", ".join(keywords)
        return {
            "message": f"🔍 Found {len(experts)} experts matching '{keyword_str}':",
            "data": experts,
            "type": "experts",
            "suggestions": [
                f"What skills are trending?",
                f"Show me projects related to {keywords[0]}" if keywords else "Show projects",
                "Show me statistics",
            ],
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
            "suggestions": [
                f"Who knows {top[0].get('name', '')}?" if top else "Show statistics",
                "Show me emerging skills",
                "How many experts do we have?",
            ],
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
                "suggestions": ["Find documents about Python", "Resources on AI", "Show statistics"],
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
                "suggestions": ["Show all documents", "Find experts instead", "Show top skills"],
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
            "suggestions": [
                f"Who knows {keywords[0]}?" if keywords else "Show experts",
                "Show top skills",
                "Show statistics",
            ],
        }

    def _handle_find_project(self, keywords: List[str]) -> Dict[str, Any]:
        """Search projects by keyword matching on name, domain, tech stack, and skills."""
        if not keywords:
            # Show recent/active projects
            active = [p for p in self._projects if p.get("status", "").lower() in ("active", "in progress", "planning")]
            if not active:
                active = self._projects
            sample = active[:5]
            projects = [
                {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "domain": p.get("domain", ""),
                    "status": p.get("status", ""),
                    "tech_stack": p.get("tech_stack", ""),
                    "team_size": p.get("team_size", 0),
                }
                for p in sample
            ]
            return {
                "message": f"📁 Here are {len(projects)} current projects:",
                "data": projects,
                "type": "projects",
                "suggestions": ["Show projects about AI", "Find experts", "Show statistics"],
            }

        matches = []
        for proj in self._projects:
            proj_text = " ".join([
                proj.get("name", ""),
                proj.get("domain", ""),
                proj.get("tech_stack", ""),
                " ".join(proj.get("required_skills", [])),
            ]).lower()
            score = sum(1 for kw in keywords if kw in proj_text)
            if score > 0:
                matches.append((score, proj))

        matches.sort(key=lambda x: -x[0])
        top = matches[:5]

        if not top:
            return {
                "message": f"No projects found matching '{' '.join(keywords)}'.",
                "data": [],
                "suggestions": ["Show all projects", "Find experts instead", "Show top skills"],
            }

        projects = [
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "domain": p.get("domain", ""),
                "status": p.get("status", ""),
                "tech_stack": p.get("tech_stack", ""),
                "team_size": p.get("team_size", 0),
                "required_skills": p.get("required_skills", []),
            }
            for _, p in top
        ]
        keyword_str = ", ".join(keywords)
        return {
            "message": f"📁 Found {len(projects)} projects related to '{keyword_str}':",
            "data": projects,
            "type": "projects",
            "suggestions": [
                f"Who knows {keywords[0]}?" if keywords else "Find experts",
                "Show top skills",
                "Show statistics",
            ],
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
            "suggestions": ["Show top skills", "Find experts in Engineering", "Show statistics"],
        }

    def _handle_general_search(self, keywords: List[str]) -> Dict[str, Any]:
        if not keywords:
            return self._handle_help([])

        # Try to match across all entities
        results = {"experts": [], "skills": [], "documents": [], "projects": []}

        for emp in self._employees[:100]:
            emp_text = f"{emp.get('name', '')} {emp.get('role', '')} {emp.get('department', '')}".lower()
            # Also check skills
            emp_skill_text = " ".join(
                s.get("name", "") if isinstance(s, dict) else str(s)
                for s in emp.get("skills", [])
            ).lower()
            combined = f"{emp_text} {emp_skill_text}"
            if any(kw in combined for kw in keywords):
                results["experts"].append({"name": emp.get("name"), "role": emp.get("role")})
                if len(results["experts"]) >= 3:
                    break

        for skill in self._skills:
            skill_text = f"{skill.get('name', '')} {skill.get('category', '')}".lower()
            if any(kw in skill_text for kw in keywords):
                results["skills"].append({"name": skill.get("name"), "category": skill.get("category")})
                if len(results["skills"]) >= 3:
                    break

        for doc in self._documents[:100]:
            doc_text = f"{doc.get('title', '')} {doc.get('topic', '')}".lower()
            if any(kw in doc_text for kw in keywords):
                results["documents"].append({"title": doc.get("title"), "topic": doc.get("topic")})
                if len(results["documents"]) >= 3:
                    break

        for proj in self._projects[:50]:
            proj_text = f"{proj.get('name', '')} {proj.get('domain', '')} {proj.get('tech_stack', '')}".lower()
            if any(kw in proj_text for kw in keywords):
                results["projects"].append({"name": proj.get("name"), "domain": proj.get("domain", "")})
                if len(results["projects"]) >= 3:
                    break

        parts = []
        if results["experts"]:
            parts.append(f"{len(results['experts'])} experts")
        if results["skills"]:
            parts.append(f"{len(results['skills'])} skills")
        if results["documents"]:
            parts.append(f"{len(results['documents'])} documents")
        if results["projects"]:
            parts.append(f"{len(results['projects'])} projects")

        if parts:
            msg = f"🔍 Found {', '.join(parts)} matching '{' '.join(keywords)}':"
        else:
            msg = f"I couldn't find results for '{' '.join(keywords)}'. Try rephrasing your question."

        return {
            "message": msg,
            "data": results,
            "type": "mixed",
            "suggestions": [
                "Try: Who knows Python?",
                "Try: Show me projects about AI",
                "Try: Show me statistics",
            ],
        }


# Singleton
chatbot = Chatbot()
