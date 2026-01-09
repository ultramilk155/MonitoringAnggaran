
import oracledb
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from app import create_app

def verify_columns():
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
            
            # User provided list
            user_cols = [
                'DSTRCT_CODE', 'FULL_PERIOD', 'TRAN_GROUP_KEY', 'ACCOUNT_CODE', 
                'GL_DESC', 'SUBLEDGER', 'EXPENSE_ELEMENT', 'SEGMENT_ACTIVITY_MT_TYPE', 
                'DESC_TRAN_TYPE', 'TRAN_AMOUNT', 'CHEQUE_NO', 'TRANSACTION_DATE', 
                'CREATION_DATE', 'CREATION_USER', 'MANJNL_VCHR', 'PROJECT_NO', 
                'PROJECT_DESC', 'DESCRIPTION_FINAL', 'RECEIPT_REF', 'RECEIPT_NUM', 
                'POSTED_STATUS', 'REPORT_STATUS', 'DOCUMENT_REF', 'AR_INV_NO', 
                'AR_INV_TYPE', 'REVENUE_CODE', 'PRICING_CODE', 'ASSET_TY', 
                'EQUIP_NO', 'SUB_ASSET_NO', 'NOMOR_ASSET', 'Column1', 'Column2', 'Column3'
            ]
            
            print("Fetching MSF900 columns...")
            cursor = connection.cursor()
            cursor.execute("SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = 'MSF900'")
            db_cols = set([r[0].upper() for r in cursor.fetchall()])
            
            print(f"\nAnalysis of {len(user_cols)} User Columns:")
            print("-" * 40)
            
            found = []
            missing = []
            
            for col in user_cols:
                # Handle potential mapping (e.g. NOMOR_ASSET might be ASSET_NO)
                uname = col.upper().strip()
                if uname in db_cols:
                    found.append(col)
                else:
                    missing.append(col)
            
            print(f"DIRECT MATCHES IN MSF900 ({len(found)}):")
            print(", ".join(found))
            
            print(f"\nNOT IN MSF900 (Derived/Joined/Renamed) ({len(missing)}):")
            for m in missing:
                # Guess origin
                guess = "?"
                if m == "GL_DESC": guess = "Derived (MSF960?)"
                if m == "SUBLEDGER": guess = "Derived (Account Code segments)"
                if m == "EXPENSE_ELEMENT": guess = "Derived (Substr Account Code)"
                if m == "PROJECT_DESC": guess = "Joined (MSF660)"
                if m == "NOMOR_ASSET": guess = "Alias (ASSET_NO?)"
                if "Column" in m: guess = "Excel Placeholder"
                print(f"- {m} ({guess})")

            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    verify_columns()
