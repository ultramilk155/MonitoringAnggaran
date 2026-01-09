
import oracledb
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from app import create_app

def verify_transaction():
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
            
            print("Verifying Transaction 30891360000...")
            
            # Check if it exists and show key columns
            query = """
SELECT 
    DSTRCT_CODE,
    TRANSACTION_NO,
    ACCOUNT_CODE,
    PROCESS_DATE,
    CREATION_DATE,
    TRAN_AMOUNT
FROM msf900
WHERE TRANSACTION_NO = '30891360000'
            """
            
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            columns = [col[0] for col in cursor.description]
            
            if rows:
                print("Transaction FOUND in MSF900:")
                df = pd.DataFrame(rows, columns=columns)
                print(df.to_string())
                
                # Check why it might have been filtered
                # 1. DSTRCT_CODE = UPPL?
                # 2. PROCESS_DATE in 2025?
                # 3. ACCOUNT_CODE pattern? E.g. substr(2,2)='PL'? substr(16,4) in list?
                
                acct = df.iloc[0]['ACCOUNT_CODE']
                date = str(df.iloc[0]['PROCESS_DATE'])
                
                print(f"\nAnalysis:")
                print(f"Substr(AC, 2, 2): '{acct[1:3]}'")
                print(f"Substr(AC, 16, 4): '{acct[15:19]}'")
                print(f"Process Date: {date}")
                
            else:
                print("Transaction 30891360000 NOT FOUND in MSF900.")

            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    verify_transaction()
