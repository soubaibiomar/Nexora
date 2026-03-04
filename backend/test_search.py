from app.database import get_db
import sys

def test_search():
    db_gen = get_db()
    db = next(db_gen)
    try:
        query = """
        MATCH (p:Person) 
        RETURN DISTINCT p.id as id, 
               coalesce(p.name, 'Unnamed Expert') as name, 
               coalesce(p.email, '') as email,
               coalesce(p.department, 'N/A') as department, 
               coalesce(p.role, 'Expert') as role, 
               coalesce(p.location, 'Unknown') as location,
               p.hire_date as hire_date, 
               coalesce(p.experience_years, 0) as experience_years,
               coalesce(p.expertise_level, 1) as expertise_level
        ORDER BY hire_date DESC, expertise_level DESC
        SKIP 0 LIMIT 20
        """
        result = db.run(query)
        experts = [dict(record) for record in result]
        print(f"Found {len(experts)} experts")
        if experts:
            print(f"First expert: {experts[0]['name']}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pass

if __name__ == "__main__":
    test_search()
