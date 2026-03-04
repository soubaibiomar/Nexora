from app.database import get_db

def create_indices():
    db_gen = get_db()
    db = next(db_gen)
    try:
        print("Creating index for Document(date)...")
        db.run("CREATE INDEX document_date IF NOT EXISTS FOR (d:Document) ON (d.date)")
        print("Creating index for Person(hire_date)...")
        db.run("CREATE INDEX person_hire_date IF NOT EXISTS FOR (p:Person) ON (p.hire_date)")
        print("Indices created or already exist.")
    finally:
        pass

if __name__ == "__main__":
    create_indices()
