from app.database import get_db
from datetime import datetime

def add_timestamps_to_existing():
    """Add created_at timestamps to existing records for proper sorting"""
    db_gen = get_db()
    db = next(db_gen)
    try:
        # Add created_at to existing documents (use their date as created_at)
        print("Adding created_at to existing documents...")
        res = db.run("""
            MATCH (d:Document)
            WHERE d.created_at IS NULL
            SET d.created_at = coalesce(d.date, '2020-01-01')
            RETURN count(d) as c
        """)
        doc_count = res.single()['c']
        print(f"Updated {doc_count} documents")
        
        # Add created_at to existing persons (use their hire_date as created_at)
        print("Adding created_at to existing persons...")
        res = db.run("""
            MATCH (p:Person)
            WHERE p.created_at IS NULL
            SET p.created_at = coalesce(p.hire_date, '2020-01-01')
            RETURN count(p) as c
        """)
        person_count = res.single()['c']
        print(f"Updated {person_count} persons")
        
        # Create indices for better performance
        print("Creating performance indices...")
        db.run("CREATE INDEX document_created_at IF NOT EXISTS FOR (d:Document) ON (d.created_at)")
        db.run("CREATE INDEX person_created_at IF NOT EXISTS FOR (p:Person) ON (p.created_at)")
        print("Indices created successfully")
        
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pass

if __name__ == "__main__":
    add_timestamps_to_existing()
