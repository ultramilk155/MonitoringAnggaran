
import oracledb
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from app import create_app

def fast_search():
    app = create_app()
    with app.app_context():
        dsn = oracledb.makedsn(
            app.config['ORACLE_HOST'], 
            app.config['ORACLE_PORT'], 
            sid=app.config['ORACLE_SID']
        )
        
        try:
            connection = oracledb.connect(
                user=app.config['ORACLE_USER'],
                password=app.config['ORACLE_PASS'],
                dsn=dsn
            )
            
            target_id = '30891360000'
            print(f"Fast Searching for {target_id} in MSF9% tables...")
            
            cursor = connection.cursor()
            
            # Get MSF9% tables with TRANSACTION_NO
            query_tabs = """
                SELECT TABLE_NAME
                FROM ALL_TAB_COLUMNS 
                WHERE COLUMN_NAME = 'TRANSACTION_NO'
                  AND TABLE_NAME LIKE 'MSF9%'
                ORDER BY TABLE_NAME
            """
            cursor.execute(query_tabs)
            tables = [r[0] for r in cursor.fetchall()]
            
            print(f"Checking {len(tables)} tables: {tables}")
            
            results = []
            for table in tables:
                try:
                    # Fast existence check
                    q = f"SELECT 1 FROM {table} WHERE TRANSACTION_NO = :tid AND ROWNUM = 1"
                    cursor.execute(q, tid=target_id)
                    if cursor.fetchone():
                        # Get count
                        q_count = f"SELECT count(*) FROM {table} WHERE TRANSACTION_NO = :tid"
                        cursor.execute(q_count, tid=target_id)
                        cnt = cursor.fetchone()[0]
                        print(f"-> FOUND in {table}: {cnt} rows")
                        results.append((table, cnt))
                        
                        # Peek
                        q_peek = f"SELECT * FROM {table} WHERE TRANSACTION_NO = :tid AND ROWNUM <= 5"
                        cursor.execute(q_peek, tid=target_id)
                        cols = [col[0] for col in cursor.description]
                        rows = cursor.fetchall()
                        df = pd.DataFrame(rows, columns=cols)
                        print(df.to_string(index=False))
                        print("-" * 20)
                        
                except Exception as e:
                    print(f"Error checking {table}: {e}")
            
            # Also check MSF8% (Employee/Payroll sometimes related?)
            # Or MSF6% (Project?)
            # But PLQ001 looks like GL Journal.
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    fast_search()
