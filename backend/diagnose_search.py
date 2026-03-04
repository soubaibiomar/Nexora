from app.database import get_db

def diagnose_expert_search():
    """Diagnose the expert search issue"""
    db_gen = get_db()
    db = next(db_gen)
    try:
        print("=== DIAGNOSTIC: Expert Search ===\n")
        
        # Test 1: Basic count
        res = db.run("MATCH (p:Person) RETURN count(p) as total")
        total = res.single()['total']
        print(f"✓ Total experts in database: {total}")
        
        # Test 2: Check created_at field
        res = db.run("""
            MATCH (p:Person)
            WHERE p.created_at IS NOT NULL
            RETURN count(p) as with_timestamp
        """)
        with_ts = res.single()['with_timestamp']
        print(f"✓ Experts with created_at: {with_ts}")
        
        # Test 3: Try the actual search query
        print("\n--- Testing actual search query ---")
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
        ORDER BY coalesce(hire_date, created_at, '2020-01-01') DESC, expertise_level DESC
        SKIP 0 LIMIT 20
        """
        
        try:
            result = db.run(query)
            experts = [dict(record) for record in result]
            print(f"✓ Query returned {len(experts)} experts")
            if experts:
                print(f"  First expert: {experts[0]['name']}")
        except Exception as e:
            print(f"✗ Query failed: {e}")
            
            # Try simpler query
            print("\n--- Testing simplified query ---")
            simple_query = """
            MATCH (p:Person)
            RETURN p.id, p.name, p.hire_date, p.created_at
            ORDER BY p.created_at DESC
            LIMIT 5
            """
            result = db.run(simple_query)
            for r in result:
                print(f"  {r[1]}: hire_date={r[2]}, created_at={r[3]}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pass

if __name__ == "__main__":
    diagnose_expert_search()
