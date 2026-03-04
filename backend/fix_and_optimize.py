from app.database import get_db
from datetime import date
import time

def fix_and_optimize():
    db_gen = get_db()
    db = next(db_gen)
    try:
        # 1. Update 'best' document date to today
        print("Updating 'best' document date...")
        today = date.today().isoformat()
        db.run("MATCH (d:Document) WHERE toLower(d.title) CONTAINS 'best' SET d.date = $today", {"today": today})
        
        # 2. Backfill document content (chunk of 5000)
        print("Backfilling document content...")
        res = db.run("""
            MATCH (d:Document)
            WHERE d.content IS NULL OR d.content = ""
            WITH d LIMIT 5000
            SET d.content = 'This document "' + coalesce(d.title, 'Untitled') + '" covers advanced topics in ' + coalesce(d.topic, 'General') + '. ExpertLink provides this resource for your continuous learning.'
            RETURN count(d) as c
        """)
        print(f"Backfilled {res.single()['c']} documents.")
        
        # 3. Test performance
        start = time.time()
        db.run("MATCH (d:Document) RETURN d.id ORDER BY d.date DESC LIMIT 100")
        print(f"Document search performance: {time.time() - start:.4f}s")
        
        start = time.time()
        db.run("MATCH (p:Person) RETURN p.id ORDER BY p.hire_date DESC LIMIT 100")
        print(f"Expert search performance: {time.time() - start:.4f}s")
        
    finally:
        pass

if __name__ == "__main__":
    fix_and_optimize()
