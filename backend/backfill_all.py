from app.database import get_db

def backfill_all():
    db_gen = get_db()
    db = next(db_gen)
    try:
        res = db.run("""
            MATCH (d:Document)
            WHERE d.content IS NULL OR d.content = ""
            WITH d LIMIT 10000
            SET d.content = 'This document "' + coalesce(d.title, 'Untitled') + '" covers ' + coalesce(d.topic, 'General') + '. ExpertLink provides this resource for your continuous learning and professional development.'
            RETURN count(d) as c
        """)
        print(f"Backfilled {res.single()['c']} more documents.")
    finally:
        pass

if __name__ == "__main__":
    backfill_all()
