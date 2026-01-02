import sqlite3

def migrate_db():
    db_path = 'instance/budget.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns exist
        cursor.execute("PRAGMA table_info(job_detail)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'terkontrak_rp' not in columns:
            print("Adding terkontrak_rp column...")
            cursor.execute("ALTER TABLE job_detail ADD COLUMN terkontrak_rp FLOAT DEFAULT 0")
            
        if 'terbayar_rp' not in columns:
            print("Adding terbayar_rp column...")
            cursor.execute("ALTER TABLE job_detail ADD COLUMN terbayar_rp FLOAT DEFAULT 0")
            
        conn.commit()
        print("Migration successful.")
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
