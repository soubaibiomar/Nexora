"""
ExpertLink Data Import Script
Imports JSONL data into Neo4j database with relationships.
"""

import json
import os
import random
from dotenv import load_dotenv
from neo4j import GraphDatabase
from pathlib import Path

# Load backend environment variables from backend/.env
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# Neo4j connection settings
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "Expertlink123")

# Data directory (relative to script location)
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


def load_jsonl(filename):
    """Load JSONL file and return list of records."""
    filepath = DATA_DIR / filename
    records = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def create_indexes(session):
    """Create indexes for better query performance."""
    indexes = [
        "CREATE INDEX person_id IF NOT EXISTS FOR (p:Person) ON (p.id)",
        "CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name)",
        "CREATE INDEX person_location IF NOT EXISTS FOR (p:Person) ON (p.location)",
        "CREATE INDEX skill_id IF NOT EXISTS FOR (s:Skill) ON (s.id)",
        "CREATE INDEX skill_name IF NOT EXISTS FOR (s:Skill) ON (s.name)",
        "CREATE INDEX project_id IF NOT EXISTS FOR (p:Project) ON (p.id)",
        "CREATE INDEX document_id IF NOT EXISTS FOR (d:Document) ON (d.id)",
        "CREATE INDEX technology_id IF NOT EXISTS FOR (t:Technology) ON (t.id)",
    ]
    for index in indexes:
        session.run(index)
    print("Indexes created.")


def import_persons(session, records):
    """Import Person nodes."""
    query = """
    UNWIND $records AS record
    MERGE (p:Person {id: record.id})
    SET p.name = record.name,
        p.email = record.email,
        p.department = record.department,
        p.role = record.role,
        p.location = record.location,
        p.hire_date = record.hire_date,
        p.experience_years = record.experience_years,
        p.expertise_level = record.expertise_level
    """
    # Import in batches of 1000
    batch_size = 1000
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        session.run(query, {"records": batch})
        print(f"  Imported persons {i+1} to {min(i+batch_size, len(records))}")
    print(f"Total {len(records)} persons imported.")


def import_skills(session, records):
    """Import Skill nodes."""
    query = """
    UNWIND $records AS record
    MERGE (s:Skill {id: record.id})
    SET s.name = record.name,
        s.category = record.category,
        s.level = record.level,
        s.demand = record.demand
    """
    session.run(query, {"records": records})
    print(f"Total {len(records)} skills imported.")


def import_projects(session, records):
    """Import Project nodes."""
    query = """
    UNWIND $records AS record
    MERGE (p:Project {id: record.id})
    SET p.name = record.name,
        p.domain = record.domain,
        p.tech_stack = record.tech_stack,
        p.date = record.date,
        p.status = record.status,
        p.budget = record.budget,
        p.priority = record.priority
    """
    batch_size = 1000
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        session.run(query, {"records": batch})
        print(f"  Imported projects {i+1} to {min(i+batch_size, len(records))}")
    print(f"Total {len(records)} projects imported.")


def import_documents(session, records):
    """Import Document nodes."""
    query = """
    UNWIND $records AS record
    MERGE (d:Document {id: record.id})
    SET d.title = record.title,
        d.type = record.type,
        d.topic = record.topic,
        d.author = record.author,
        d.date = record.date,
        d.views = record.views,
        d.rating = record.rating
    """
    batch_size = 1000
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        session.run(query, {"records": batch})
        print(f"  Imported documents {i+1} to {min(i+batch_size, len(records))}")
    print(f"Total {len(records)} documents imported.")


def import_technologies(session, records):
    """Import Technology nodes."""
    query = """
    UNWIND $records AS record
    MERGE (t:Technology {id: record.id})
    SET t.uri = record.uri,
        t.name = record.name,
        t.description = record.description,
        t.category = record.category
    """
    batch_size = 1000
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        session.run(query, {"records": batch})
        print(f"  Imported technologies {i+1} to {min(i+batch_size, len(records))}")
    print(f"Total {len(records)} technologies imported.")


def create_relationships(session, persons, skills, projects, documents):
    """Create relationships between nodes."""
    print("\nCreating relationships...")
    
    skill_ids = [s["id"] for s in skills]
    project_ids = [p["id"] for p in projects]
    
    # HAS_SKILL: Person -> Skill (random 3-8 skills per person)
    print("Creating HAS_SKILL relationships...")
    for i, person in enumerate(persons):
        person_skills = random.sample(skill_ids, min(random.randint(3, 8), len(skill_ids)))
        query = """
        MATCH (p:Person {id: $person_id})
        UNWIND $skill_ids AS skill_id
        MATCH (s:Skill {id: skill_id})
        MERGE (p)-[:HAS_SKILL]->(s)
        """
        session.run(query, {"person_id": person["id"], "skill_ids": person_skills})
        if (i + 1) % 5000 == 0:
            print(f"  Processed {i+1} persons for HAS_SKILL")
    
    # WORKS_ON: Person -> Project (random 1-3 projects per person)
    print("Creating WORKS_ON relationships...")
    for i, person in enumerate(persons):
        person_projects = random.sample(project_ids, min(random.randint(1, 3), len(project_ids)))
        query = """
        MATCH (p:Person {id: $person_id})
        UNWIND $project_ids AS project_id
        MATCH (proj:Project {id: project_id})
        MERGE (p)-[:WORKS_ON]->(proj)
        """
        session.run(query, {"person_id": person["id"], "project_ids": person_projects})
        if (i + 1) % 5000 == 0:
            print(f"  Processed {i+1} persons for WORKS_ON")
    
    # AUTHORED: Person -> Document (match author field)
    print("Creating AUTHORED relationships...")
    query = """
    MATCH (d:Document)
    WHERE d.author IS NOT NULL
    MATCH (p:Person {id: d.author})
    MERGE (p)-[:AUTHORED]->(d)
    """
    session.run(query, {})
    
    # COVERS_TOPIC: Document -> Skill (random 1-3 skills per document)
    print("Creating COVERS_TOPIC relationships...")
    for i, doc in enumerate(documents):
        doc_skills = random.sample(skill_ids, min(random.randint(1, 3), len(skill_ids)))
        query = """
        MATCH (d:Document {id: $doc_id})
        UNWIND $skill_ids AS skill_id
        MATCH (s:Skill {id: skill_id})
        MERGE (d)-[:COVERS_TOPIC]->(s)
        """
        session.run(query, {"doc_id": doc["id"], "skill_ids": doc_skills})
        if (i + 1) % 2000 == 0:
            print(f"  Processed {i+1} documents for COVERS_TOPIC")
    
    # RELATED_TO: Skill -> Skill (skills in same category)
    print("Creating RELATED_TO relationships...")
    query = """
    MATCH (s1:Skill), (s2:Skill)
    WHERE s1.category = s2.category AND s1.id < s2.id
    WITH s1, s2, rand() as r
    WHERE r < 0.3
    MERGE (s1)-[:RELATED_TO]->(s2)
    """
    session.run(query, {})
    
    print("Relationships created successfully!")


def get_stats(session):
    """Get database statistics."""
    query = """
    MATCH (n) 
    WITH labels(n)[0] as type, count(*) as count
    RETURN type, count
    ORDER BY count DESC
    """
    result = session.run(query, {})
    print("\n=== Database Statistics ===")
    total = 0
    for record in result:
        print(f"  {record['type']}: {record['count']}")
        total += record['count']
    print(f"  Total Nodes: {total}")
    
    rel_query = """
    MATCH ()-[r]->()
    WITH type(r) as type, count(*) as count
    RETURN type, count
    ORDER BY count DESC
    """
    rel_result = session.run(rel_query, {})
    print("\n  Relationships:")
    rel_total = 0
    for record in rel_result:
        print(f"    {record['type']}: {record['count']}")
        rel_total += record['count']
    print(f"  Total Relationships: {rel_total}")


def main():
    print("=" * 50)
    print("ExpertLink Data Import")
    print("=" * 50)
    print(f"Data directory: {DATA_DIR}")
    print(f"Neo4j URI: {NEO4J_URI}")
    
    # Connect to Neo4j
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        with driver.session() as session:
            # Create indexes
            print("\n1. Creating indexes...")
            create_indexes(session)
            
            # Load data
            print("\n2. Loading data files...")
            persons = load_jsonl("employees.jsonl")
            skills = load_jsonl("skills.jsonl")
            projects = load_jsonl("projects.jsonl")
            documents = load_jsonl("documents.jsonl")
            technologies = load_jsonl("technologies.jsonl")
            
            print(f"  Loaded {len(persons)} employees")
            print(f"  Loaded {len(skills)} skills")
            print(f"  Loaded {len(projects)} projects")
            print(f"  Loaded {len(documents)} documents")
            print(f"  Loaded {len(technologies)} technologies")
            
            # Import nodes
            print("\n3. Importing nodes...")
            import_persons(session, persons)
            import_skills(session, skills)
            import_projects(session, projects)
            import_documents(session, documents)
            import_technologies(session, technologies)
            
            # Create relationships
            print("\n4. Creating relationships...")
            create_relationships(session, persons, skills, projects, documents)
            
            # Get stats
            get_stats(session)
            
            print("\n" + "=" * 50)
            print("Import completed successfully!")
            print("=" * 50)
            
    finally:
        driver.close()


if __name__ == "__main__":
    main()
