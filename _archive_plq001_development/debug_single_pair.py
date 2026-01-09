
import oracledb
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from app import create_app

def debug_single_pair():
    """Debug dengan 1 TGK+ACCT pair dari PLQ001"""
    app = create_app()
    with app.app_context():
        dsn = oracledb.makedsn(
            app.config['ORACLE_HOST'], 
            app.config['ORACLE_PORT'], 
            sid=app.config['ORACLE_SID']
        )
        
        try:
            # Load PLQ001 dan ambil 1 contoh
            file_orig = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
            df_orig = pd.read_excel(file_orig, header=None, skiprows=8, nrows=1)
            
            tgk_sample = str(df_orig.iloc[0, 2]).strip()
            acct_sample = str(df_orig.iloc[0, 3]).strip()
            amt_sample = df_orig.iloc[0, 9]
            
            print(f"Sample from PLQ001:")
            print(f"TGK: '{tgk_sample}'")
            print(f"ACCT: '{acct_sample}'")
            print(f"AMT: {amt_sample}")
            
            # Test query di database
            connection = oracledb.connect(
                user=app.config['ORACLE_USER'],
                password=app.config['ORACLE_PASS'],
                dsn=dsn
            )
            
            cursor = connection.cursor()
            
            # Test 1: Query dengan exact match
            print(f"\nTest 1: Exact TGK + ACCT match")
            q1 = """
SELECT count(*), sum(TRAN_AMOUNT)
FROM msf900 
WHERE DSTRCT_CODE = 'UPPL'
  AND TRAN_GROUP_KEY = :tgk
  AND ACCOUNT_CODE = :acct
"""
            cursor.execute(q1, tgk=tgk_sample, acct=acct_sample)
            result = cursor.fetchone()
            print(f"Found: {result[0]} rows, Total: {result[1]}")
            
            # Test 2: Query hanya TGK
            print(f"\nTest 2: Only TGK match")
            q2 = """
SELECT count(*), sum(TRAN_AMOUNT)
FROM msf900 
WHERE DSTRCT_CODE = 'UPPL'
  AND TRAN_GROUP_KEY = :tgk
"""
            cursor.execute(q2, tgk=tgk_sample)
            result = cursor.fetchone()
            print(f"Found: {result[0]} rows,Total: {result[1]}")
            
            # Test 3: Lihat actual ACCOUNT_CODE untuk TGK ini
            print(f"\nTest 3: Actual ACCOUNT_CODEs for this TGK")
            q3 = """
SELECT ACCOUNT_CODE, TRAN_AMOUNT
FROM msf900 
WHERE DSTRCT_CODE = 'UPPL'
  AND TRAN_GROUP_KEY = :tgk
"""
            cursor.execute(q3, tgk=tgk_sample)
            rows = cursor.fetchall()
            print(f"Found {len(rows)} rows:")
            for r in rows:
                print(f"  ACCT: '{r[0]}', AMT: {r[1]}")
                if r[0] == acct_sample:
                    print(f"    ^^^ MATCHES SAMPLE!")
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_single_pair()
