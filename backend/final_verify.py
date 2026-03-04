from app.database import get_db

def final_verify():
    db_gen = get_db()
    db = next(db_gen)
    try:
        query = "MATCH (d:Document) RETURN d.title, d.date ORDER BY d.date DESC LIMIT 5"
        res = db.run(query)
        print("Final Top 5 Documents:")
        for r in res:
            print(f"Title: {r[0]}, Date: {r[1]}")
    finally:
        pass

if __name__ == "__main__":
    final_verify()
