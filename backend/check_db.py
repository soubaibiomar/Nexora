from app.database import get_db
import sys

def check_data():
    db_gen = get_db()
    db = next(db_gen)
    try:
        # Check Persons
        res = db.run("MATCH (p:Person) RETURN count(p) as c")
        print(f"Total Persons: {res.single()['c']}")
        
        # Check some persons
        res = db.run("MATCH (p:Person) RETURN p.id, p.name, p.hire_date LIMIT 3")
        for r in res:
            print(f"ID: {r[0]}, Name: {r[1]}, HireDate: {r[2]}")
            
        # Check Documents
        res = db.run("MATCH (d:Document) RETURN count(d) as c")
        print(f"Total Documents: {res.single()['c']}")
    finally:
        # We don't have a way to easily trigger the generator's finally block here 
        # but the script exiting will be fine for local testing
        pass

if __name__ == "__main__":
    check_data()
