
import oracledb
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from app import create_app

def find_transaction_source():
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
            print(f"Searching for keys relating to Transaction {target_id} in MSF% tables...")
            
            cursor = connection.cursor()
            
            # 1. Find tables with TRANSACTION_NO column
            print("Finding tables with 'TRANSACTION_NO' or similar column...")
            query_tabs = """
                SELECT TABLE_NAME, COLUMN_NAME 
                FROM ALL_TAB_COLUMNS 
                WHERE (COLUMN_NAME = 'TRANSACTION_NO' OR COLUMN_NAME LIKE '%DOC_NO%' OR COLUMN_NAME LIKE '%JNL%NO%')
                  AND TABLE_NAME LIKE 'MSF%'
                  AND OWNER = USER
                ORDER BY TABLE_NAME
            """
            # Note: OWNER=USER might be too restrictive if they use synonyms. Using no owner filter but checking accessibility.
            # Adjusted query to be broader but safe
            query_tabs = """
                SELECT TABLE_NAME, COLUMN_NAME 
                FROM ALL_TAB_COLUMNS 
                WHERE COLUMN_NAME = 'TRANSACTION_NO'
                  AND TABLE_NAME LIKE 'MSF%'
            """
            
            cursor.execute(query_tabs)
            candidates = cursor.fetchall()
            
            tables_to_check = set([c[0] for c in candidates])
            print(f"Found {len(tables_to_check)} candidate tables with TRANSACTION_NO.")
            
            # 2. Check each table for the record
            results = []
            
            for table in sorted(tables_to_check):
                try:
                    # Check row count for this transaction ID
                    # We also want to check DSTRCT_CODE if possible, but not all tables have it.
                    # First just check existence of ID.
                    q = f"SELECT count(*) FROM {table} WHERE TRANSACTION_NO = :tid"
                    cursor.execute(q, tid=target_id)
                    count = cursor.fetchone()[0]
                    
                    if count > 0:
                        print(f"[MATCH] {table}: {count} rows")
                        results.append((table, count))
                        
                        # Peek at the data if match found
                        if count > 0:
                            q_peek = f"SELECT * FROM {table} WHERE TRANSACTION_NO = :tid AND ROWNUM <= 5"
                            cursor.execute(q_peek, tid=target_id)
                            cols = [col[0] for col in cursor.description]
                            rows = cursor.fetchall()
                            df = pd.DataFrame(rows, columns=cols)
                            # Check if 'UPPL' is in any column to confirm district relevance
                            print(df.to_string(index=False))
                            print("-" * 30)
                            
                except Exception as e:
                    # Ignore permissions errors or missing tables
                    # print(f"Skipping {table}: {e}")
                    pass
            
            if not results:
                print("No matching records found in any MSF table with TRANSACTION_NO.")
                
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    find_transaction_source()
