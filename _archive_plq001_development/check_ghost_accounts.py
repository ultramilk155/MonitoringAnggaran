
import oracledb
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from app import create_app

def check_ghost_accounts():
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
            
            # Accounts from PLQ that were NOT in my extraction (My extraction had ...0103...)
            # PLQ had ...1203..., ...1303..., ...1403...
            ghost_accts = [
                'APL192640120311F104',
                'APL192640130311F104',
                'APL192640140311F104'
            ]
            
            print("Checking existence of Ghost Accounts in MSF900...")
            
            cursor = connection.cursor()
            
            for acct in ghost_accts:
                q = "SELECT count(*) FROM msf900 WHERE ACCOUNT_CODE = :ac"
                cursor.execute(q, ac=acct)
                cnt = cursor.fetchone()[0]
                print(f"Account {acct}: {cnt} rows total in MSF900")
                
                if cnt > 0:
                    # Check if linked to our transaction
                    q2 = "SELECT count(*) FROM msf900 WHERE ACCOUNT_CODE = :ac AND TRANSACTION_NO = '30891360000'"
                    cursor.execute(q2, ac=acct)
                    cnt2 = cursor.fetchone()[0]
                    print(f"  -> Linked to Trx 30891360000? {cnt2}")
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_ghost_accounts()
