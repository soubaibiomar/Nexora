"""
Generate Spark output files using pure Python (no Java/Spark needed).
Produces the same JSON output that the PySpark jobs would generate.
"""
import json
from pathlib import Path
from collections import Counter, defaultdict
import re

DATA_DIR = Path(__file__).parent.parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_jsonl(filename):
    """Load a JSONL file into a list of dicts."""
    filepath = DATA_DIR / filename
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records

# ─────────────────────────────────────────────────────────────────
# 1. SKILL ANALYTICS
# ─────────────────────────────────────────────────────────────────
def generate_skill_analytics():
    print("▶ Generating skill analytics...")
    employees = load_jsonl("employees.jsonl")
    
    skill_freq = Counter()
    skill_levels = defaultdict(list)
    dept_skills = defaultdict(lambda: defaultdict(lambda: {"count": 0, "levels": []}))
    co_occur = Counter()
    expert_data = []
    
    for emp in employees:
        emp_skills = emp.get("skills", [])
        skill_names = []
        total_level = 0
        
        for s in emp_skills:
            name = s.get("name", "")
            level = s.get("level", 0)
            skill_freq[name] += 1
            skill_levels[name].append(level)
            dept = emp.get("department", "Unknown")
            dept_skills[dept][name]["count"] += 1
            dept_skills[dept][name]["levels"].append(level)
            skill_names.append(name)
            total_level += level
        
        # Co-occurrence pairs
        for i in range(len(skill_names)):
            for j in range(i+1, len(skill_names)):
                pair = tuple(sorted([skill_names[i], skill_names[j]]))
                co_occur[pair] += 1
        
        # Expert scoring
        if emp_skills:
            avg_level = total_level / len(emp_skills)
            expert_data.append({
                "employee_id": emp.get("id"),
                "employee_name": emp.get("name"),
                "department": emp.get("department"),
                "num_skills": len(emp_skills),
                "avg_skill_level": round(avg_level, 2),
                "expert_score": round(len(emp_skills) * avg_level, 2),
            })
    
    results = {
        "skill_frequency": sorted(
            [{"skill_name": k, "expert_count": v, "avg_level": round(sum(skill_levels[k])/len(skill_levels[k]), 2)} 
             for k, v in skill_freq.items()],
            key=lambda x: -x["expert_count"]
        ),
        "department_skills": sorted(
            [{"department": dept, "skill_name": skill, "count": d["count"], "avg_level": round(sum(d["levels"])/len(d["levels"]), 2)}
             for dept, skills in dept_skills.items() for skill, d in skills.items()],
            key=lambda x: (x["department"], -x["count"])
        )[:100],
        "skill_co_occurrence": sorted(
            [{"skill_1": p[0], "skill_2": p[1], "co_occurrence": c} for p, c in co_occur.items()],
            key=lambda x: -x["co_occurrence"]
        )[:50],
        "expert_scores": sorted(expert_data, key=lambda x: -x["expert_score"])[:50],
        "total_records_processed": len(employees),
    }
    
    with open(OUTPUT_DIR / "skill_analytics_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"  ✓ Saved skill_analytics_results.json ({len(results['skill_frequency'])} skills)")

# ─────────────────────────────────────────────────────────────────
# 2. DOCUMENT PROCESSING
# ─────────────────────────────────────────────────────────────────
STOP_WORDS = {"the","a","an","in","on","at","to","for","of","and","is","are","was","were","be","been","has","have","had","do","does","did","will","would","could","should","may","might","can","with","from","by","as","or","not","this","that","these","those","it","its","no","but","if","so","than","too","very","just","about","into","over","after","before","between","out","up","down","off","through","during","each","few","more","most","other","some","such","only","own","same","all","both","any","how","what","which","who","whom","when","where","why","new","using","based","data","best","learning"}

def generate_document_processing():
    print("▶ Generating document processing...")
    documents = load_jsonl("documents.jsonl")
    
    # Documents by type
    type_counts = Counter(d.get("type", "unknown") for d in documents)
    docs_by_type = sorted(
        [{"type": t, "count": c} for t, c in type_counts.items()],
        key=lambda x: -x["count"]
    )
    
    # Documents by topic
    topic_data = defaultdict(lambda: {"count": 0, "ratings": [], "views": []})
    for d in documents:
        t = d.get("topic", "unknown")
        topic_data[t]["count"] += 1
        if d.get("rating"): topic_data[t]["ratings"].append(d["rating"])
        if d.get("views"): topic_data[t]["views"].append(d["views"])
    
    docs_by_topic = sorted(
        [{"topic": t, "count": v["count"],
          "avg_rating": round(sum(v["ratings"])/len(v["ratings"]), 2) if v["ratings"] else 0,
          "avg_views": round(sum(v["views"])/len(v["views"]), 2) if v["views"] else 0}
         for t, v in topic_data.items()],
        key=lambda x: -x["count"]
    )
    
    # Word frequency
    word_freq = Counter()
    topic_word_freq = defaultdict(Counter)
    for d in documents:
        title = (d.get("title") or "").lower()
        words = re.findall(r'[a-z]+', title)
        words = [w for w in words if len(w) > 2 and w not in STOP_WORDS]
        word_freq.update(words)
        topic = d.get("topic", "unknown")
        topic_word_freq[topic].update(words)
    
    top_words = [{"word": w, "frequency": c} for w, c in word_freq.most_common(50)]
    
    # Topic keywords
    topic_keywords = []
    for topic, wf in topic_word_freq.items():
        for word, freq in wf.most_common(10):
            topic_keywords.append({"topic": topic, "word": word, "frequency": freq})
    
    # Rating distribution
    rating_categories = Counter()
    for d in documents:
        r = d.get("rating", 0)
        if r >= 4.5: cat = "Excellent"
        elif r >= 3.5: cat = "Good"
        elif r >= 2.5: cat = "Average"
        else: cat = "Below Average"
        rating_categories[cat] += 1
    
    results = {
        "total_documents": len(documents),
        "documents_by_type": docs_by_type,
        "documents_by_topic": docs_by_topic,
        "top_words": top_words,
        "topic_keywords": topic_keywords,
        "rating_distribution": [{"rating_category": k, "count": v} for k, v in rating_categories.most_common()],
    }
    
    with open(OUTPUT_DIR / "document_processing_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"  ✓ Saved document_processing_results.json ({len(documents)} documents)")

# ─────────────────────────────────────────────────────────────────
# 3. EXPERT SCORING
# ─────────────────────────────────────────────────────────────────
def generate_expert_scoring():
    print("▶ Generating expert scoring...")
    employees = load_jsonl("employees.jsonl")
    documents = load_jsonl("documents.jsonl")
    
    # Document contributions per author
    doc_counts = defaultdict(lambda: {"num_documents": 0, "ratings": [], "total_views": 0})
    for d in documents:
        author = d.get("author")
        if author:
            doc_counts[author]["num_documents"] += 1
            if d.get("rating"): doc_counts[author]["ratings"].append(d["rating"])
            doc_counts[author]["total_views"] += d.get("views", 0)
    
    rankings = []
    for emp in employees:
        skills = emp.get("skills", [])
        num_skills = len(skills)
        avg_skill = sum(s.get("level", 0) for s in skills) / num_skills if num_skills else 0
        exp_years = emp.get("experience_years", 0) or 0
        
        author_id = emp.get("id")
        dc = doc_counts.get(author_id, {"num_documents": 0, "ratings": [], "total_views": 0})
        num_docs = dc["num_documents"]
        avg_doc_rating = sum(dc["ratings"]) / len(dc["ratings"]) if dc["ratings"] else 0
        
        score = round(
            (num_skills * 0.25) + (avg_skill * 0.25) + (exp_years / 10 * 0.15) +
            (num_docs * 0.2) + (avg_doc_rating * 0.15), 4
        )
        
        if score >= 3.0: tier = "🏆 Expert Leader"
        elif score >= 2.0: tier = "⭐ Senior Expert"
        elif score >= 1.0: tier = "📈 Rising Expert"
        else: tier = "🌱 Developing Expert"
        
        rankings.append({
            "employee_id": emp.get("id"),
            "employee_name": emp.get("name"),
            "department": emp.get("department"),
            "role": emp.get("role"),
            "experience_years": exp_years,
            "expertise_level": emp.get("expertise_level"),
            "num_skills": num_skills,
            "avg_skill_level": round(avg_skill, 2),
            "num_documents": num_docs,
            "avg_doc_rating": round(avg_doc_rating, 2),
            "total_views": dc["total_views"],
            "influence_score": score,
            "tier": tier,
        })
    
    rankings.sort(key=lambda x: -x["influence_score"])
    
    # Tier distribution
    tier_dist = Counter(r["tier"] for r in rankings)
    tier_distribution = [{"tier": t, "count": c} for t, c in tier_dist.most_common()]
    
    # Department rankings
    dept_data = defaultdict(lambda: {"scores": [], "count": 0})
    for r in rankings:
        dept_data[r["department"]]["scores"].append(r["influence_score"])
        dept_data[r["department"]]["count"] += 1
    
    dept_rankings = sorted(
        [{"department": d, "num_experts": v["count"], "avg_score": round(sum(v["scores"])/len(v["scores"]), 4)}
         for d, v in dept_data.items()],
        key=lambda x: -x["avg_score"]
    )
    
    results = {
        "expert_rankings": rankings[:50],
        "tier_distribution": tier_distribution,
        "department_rankings": dept_rankings,
        "total_experts_scored": len(employees),
    }
    
    with open(OUTPUT_DIR / "expert_scoring_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"  ✓ Saved expert_scoring_results.json ({len(employees)} experts)")

# ─────────────────────────────────────────────────────────────────
# 4. COMPANY ANALYTICS
# ─────────────────────────────────────────────────────────────────
def generate_company_analytics():
    print("▶ Generating company analytics...")
    companies = load_jsonl("companies.jsonl")
    employees = load_jsonl("employees.jsonl")
    
    # Industry stats
    industry_data = defaultdict(lambda: {"count": 0, "ratings": [], "open_roles": 0, "employees": 0})
    for c in companies:
        ind = c.get("industry", "Unknown")
        industry_data[ind]["count"] += 1
        if c.get("rating"): industry_data[ind]["ratings"].append(c["rating"])
        industry_data[ind]["open_roles"] += c.get("open_roles", 0)
        industry_data[ind]["employees"] += c.get("employees", 0)
    
    industry_stats = sorted(
        [{"industry": i, "company_count": v["count"],
          "avg_rating": round(sum(v["ratings"])/len(v["ratings"]), 2) if v["ratings"] else 0,
          "total_open_roles": v["open_roles"], "total_employees": v["employees"],
          "avg_company_size": round(v["employees"]/v["count"]) if v["count"] else 0}
         for i, v in industry_data.items()],
        key=lambda x: -x["company_count"]
    )
    
    # Size distribution
    size_data = defaultdict(lambda: {"count": 0, "ratings": [], "employees": []})
    for c in companies:
        s = c.get("size", "Unknown")
        size_data[s]["count"] += 1
        if c.get("rating"): size_data[s]["ratings"].append(c["rating"])
        if c.get("employees"): size_data[s]["employees"].append(c["employees"])
    
    size_distribution = sorted(
        [{"size": s, "count": v["count"],
          "avg_rating": round(sum(v["ratings"])/len(v["ratings"]), 2) if v["ratings"] else 0,
          "avg_employees": round(sum(v["employees"])/len(v["employees"])) if v["employees"] else 0}
         for s, v in size_data.items()],
        key=lambda x: -x["count"]
    )
    
    # Tech stack frequency
    tech_freq = Counter()
    tech_by_industry = defaultdict(Counter)
    for c in companies:
        for tech in c.get("tech_stack", []):
            tech_freq[tech] += 1
            tech_by_industry[c.get("industry", "Unknown")][tech] += 1
    
    tech_stack_frequency = [{"technology": t, "company_count": c} for t, c in tech_freq.most_common(30)]
    
    # Top 5 tech per industry
    tech_industry_list = []
    for ind, techs in tech_by_industry.items():
        for tech, cnt in techs.most_common(5):
            tech_industry_list.append({"industry": ind, "technology": tech, "count": cnt})
    
    # Geographic distribution
    geo = defaultdict(lambda: {"count": 0, "employees": 0, "open_roles": 0})
    for c in companies:
        loc = c.get("location", "Unknown")
        geo[loc]["count"] += 1
        geo[loc]["employees"] += c.get("employees", 0)
        geo[loc]["open_roles"] += c.get("open_roles", 0)
    
    geo_dist = sorted(
        [{"location": l, "company_count": v["count"], "total_employees": v["employees"], "total_open_roles": v["open_roles"]}
         for l, v in geo.items()],
        key=lambda x: -x["company_count"]
    )
    
    # Company rankings
    company_rankings = []
    for c in companies:
        tech_div = len(c.get("tech_stack", []))
        spec_count = len(c.get("specialties", []))
        open_r = c.get("open_roles", 0)
        bonus = 15 if open_r > 30 else (10 if open_r > 15 else 5)
        score = round(c.get("rating", 0) * 20 + tech_div * 2 + bonus + spec_count * 3, 2)
        company_rankings.append({
            "id": c.get("id"), "name": c.get("name"), "industry": c.get("industry"),
            "rating": c.get("rating"), "employees": c.get("employees"),
            "open_roles": open_r, "location": c.get("location"),
            "tech_diversity": tech_div, "specialty_count": spec_count,
            "attractiveness_score": score,
        })
    company_rankings.sort(key=lambda x: -x["attractiveness_score"])
    
    total_open = sum(c.get("open_roles", 0) for c in companies)
    
    results = {
        "total_companies": len(companies),
        "total_open_roles": total_open,
        "industry_stats": industry_stats,
        "size_distribution": size_distribution,
        "tech_stack_frequency": tech_stack_frequency,
        "tech_by_industry": tech_industry_list,
        "geographic_distribution": geo_dist,
        "company_rankings": company_rankings[:50],
        "skill_match_samples": [],
    }
    
    with open(OUTPUT_DIR / "company_analytics_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    # Also save company catalog
    with open(OUTPUT_DIR / "companies_catalog.json", "w", encoding="utf-8") as f:
        json.dump(companies, f, indent=2)
    
    print(f"  ✓ Saved company_analytics_results.json ({len(companies)} companies)")
    print(f"  ✓ Saved companies_catalog.json")

# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Nexora Analytics Pipeline (Python)")
    print("=" * 60)
    generate_skill_analytics()
    generate_document_processing()
    generate_expert_scoring()
    generate_company_analytics()
    print("=" * 60)
    print("  ✅ All pipeline jobs completed!")
    print(f"  Output directory: {OUTPUT_DIR}")
    print("=" * 60)
