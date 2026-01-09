
import oracledb
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from app import create_app

def check_blank_project_no():
    """
    Check why 430 rows have blank PROJECT_NO in replication
    """
    app = create_app()
    with app.app_context():
        dsn = oracledb.makedsn(
            app.config['ORACLE_HOST'], 
            app.config['ORACLE_PORT'], 
            sid=app.config['ORACLE_SID']
        )
        
        try:
            # Load mismatch report
            mismatches = pd.read_excel("project_no_mismatches.xlsx")
            
            # Take first 5 cases to investigate
            sample = mismatches.head(5)
            
            connection = oracledb.connect(
                user=app.config['ORACLE_USER'],
                password=app.config['ORACLE_PASS'],
                dsn=dsn
            )
            
            cursor = connection.cursor()
            
            for idx, row in sample.iterrows():
                tgk = row['TGK']
                acct = row['ACCT']
                amt = float(row['AMT'])
                expected_proj = row['PROJECT_NO_ORIG']
                
                print(f"\n{'='*60}")
                print(f"Case {idx+1}:")
                print(f"TGK: {tgk}")
                print(f"ACCT: {acct}")
                print(f"AMT: {amt}")
                print(f"Expected PROJECT_NO: '{expected_proj}'")
                
                # Query database
                q = """
SELECT PROJECT_NO, TRAN_AMOUNT, ACCOUNT_CODE, 
       DESCRIPTION, INV_ITEM_DESC, JOURNAL_DESC
FROM msf900
WHERE DSTRCT_CODE = 'UPPL'
  AND TRAN_GROUP_KEY = :tgk
  AND TRIM(ACCOUNT_CODE) = :acct
  AND TRAN_AMOUNT = :amt
"""
                
                cursor.execute(q, tgk=tgk, acct=acct, amt=amt)
                results = cursor.fetchall()
                
                print(f"\nFound {len(results)} rows in MSF900:")
                for r in results:
                    proj = str(r[0]).strip() if r[0] else '[NULL]'
                    desc = str(r[3])[:40] if r[3] else '[NULL]'
                    print(f"  PROJECT_NO: '{proj}'")
                    print(f"  DESCRIPTION: {desc}")
                
                # Check if PROJECT_NO exists elsewhere for this TGK
                q2 = """
SELECT DISTINCT PROJECT_NO
FROM msf900
WHERE DSTRCT_CODE = 'UPPL'
  AND TRAN_GROUP_KEY = :tgk
  AND PROJECT_NO IS NOT NULL
"""
                cursor.execute(q2, tgk=tgk)
                all_projs = cursor.fetchall()
                
                if all_projs:
                    print(f"\n  Other PROJECT_NOs for this TGK:")
                    for p in all_projs:
                        print(f"    - {p[0]}")
            
            cursor.close()
            connection.close()
            
            print(f"\n{'='*60}")
            print("CONCLUSION:")
            print("If PROJECT_NO is NULL in DB but populated in PLQ001,")
            print("PLQ001 might be using a different logic/source.")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_blank_project_no()
