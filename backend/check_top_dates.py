from app.database import get_db

def check_dates():
    db_gen = get_db()
    db = next(db_gen)
    try:
        res = db.run("MATCH (d:Document) RETURN d.title, d.date ORDER BY d.date DESC LIMIT 5")
        print("Top 5 Documents by Date:")
        for r in res:
            print(f"Title: {r[0]}, Date: {r[1]}")
            
        res = db.run("MATCH (p:Person) RETURN p.name, p.hire_date ORDER BY p.hire_date DESC LIMIT 5")
        print("\nTop 5 Persons by Hire Date:")
        for r in res:
            print(f"Name: {r[0]}, Hire Date: {r[1]}")
    finally:
        pass

if __name__ == "__main__":
    check_dates()
