from app.database import get_db

def inspect_best():
    db_gen = get_db()
    db = next(db_gen)
    try:
        # Find the document named 'best'
        res = db.run("MATCH (d:Document) WHERE toLower(d.title) CONTAINS 'best' RETURN d.id, d.title, d.date, d.content")
        for r in res:
            print(f"ID: {r[0]}, Title: {r[1]}, Date: {r[2]}, Content Snippet: {str(r[3])[:50]}")
            
        # Check indices
        print("\nChecking indices:")
        res = db.run("SHOW INDEXES")
        for r in res:
            print(f"Index: {r['name']}, State: {r['state']}, Labels: {r['labelsOrTypes']}, Properties: {r['properties']}")

    finally:
        pass

if __name__ == "__main__":
    inspect_best()
