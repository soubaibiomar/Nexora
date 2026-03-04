from app.database import get_db

def test_fixed_query():
    """Test the fixed query"""
    db_gen = get_db()
    db = next(db_gen)
    try:
        print("=== Testing Fixed Query ===\n")
        
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
               coalesce(p.expertise_level, 1) as expertise_level,
               coalesce(p.created_at, p.hire_date, '2020-01-01') as sort_date
        ORDER BY sort_date DESC, expertise_level DESC
        SKIP 0 LIMIT 20
        """
        
        result = db.run(query)
        experts = [dict(record) for record in result]
        print(f"✓ Query SUCCESS! Returned {len(experts)} experts")
        
        if experts:
            print(f"\nTop 3 experts:")
            for i, expert in enumerate(experts[:3], 1):
                print(f"  {i}. {expert['name']} ({expert['department']}) - {expert['sort_date']}")
        
    except Exception as e:
        print(f"✗ Query failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pass

if __name__ == "__main__":
    test_fixed_query()
