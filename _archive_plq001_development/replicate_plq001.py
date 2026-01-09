
import oracledb
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from app import create_app

def replicate_plq001():
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
            
            print("Replicating PLQ001 Query for UPPL 2025...")
            
            # Target Expense Elements (from user's filter)
            ee_filter = "('E201', 'E202', 'E203', 'E204', 'F101', 'F104', 'F106', 'F107')"
            
            # Build query matching PLQ001 columns
            query = f"""
SELECT
    a.DSTRCT_CODE,
    a.FULL_PERIOD,
    a.TRAN_GROUP_KEY,
    a.ACCOUNT_CODE,
    
    -- GL_DESC: Description from account lookup (simplified - using JOURNAL_DESC as proxy)
    a.JOURNAL_DESC as GL_DESC,
    
    -- SUBLEDGER: Derived from MIMS_SL_KEY or similar
    a.MIMS_SL_KEY as SUBLEDGER,
    
    -- EXPENSE_ELEMENT: Digit 16-19 of ACCOUNT_CODE
    substr(a.ACCOUNT_CODE, 16, 4) as EXPENSE_ELEMENT,
    
    -- SEGMENT_ACTIVITY_MT_TYPE: Custom - using segment 4 (Activity code)
    substr(a.ACCOUNT_CODE, 6, 3) as SEGMENT_ACTIVITY_MT_TYPE,
    
    -- DESC_TRAN_TYPE: Description of transaction type
    CASE a.TRAN_TYPE 
        WHEN 'ISS' THEN 'Issue'
        WHEN 'PRD' THEN 'Purchase Requisition Direct'
        WHEN 'SVR' THEN 'Service Receipt'
        WHEN 'SRD' THEN 'Stock Receipt Direct'
        WHEN 'CHG' THEN 'Cheque Charge'
        WHEN 'MPJ' THEN 'Manual Journal Voucher - Primary'
        ELSE a.TRAN_TYPE
    END as DESC_TRAN_TYPE,
    
    a.TRAN_AMOUNT,
    a.CHEQUE_NO,
    
    -- TRANSACTION_DATE: Using TRNDTE_REVSD or PROCESS_DATE
    NVL(a.TRNDTE_REVSD, a.PROCESS_DATE) as TRANSACTION_DATE,
    
    a.CREATION_DATE,
    a.CREATION_USER,
    a.MANJNL_VCHR,
    a.PROJECT_NO,
    
    -- PROJECT_DESC: Join to MSF660
    (SELECT p.PROJ_DESC FROM msf660 p 
     WHERE p.DSTRCT_CODE = a.DSTRCT_CODE 
     AND p.PROJECT_NO = a.PROJECT_NO 
     AND ROWNUM = 1) as PROJECT_DESC,
    
    -- DESCRIPTION_FINAL: Combine multiple description fields
    CASE 
        WHEN a.INV_ITEM_DESC IS NOT NULL AND TRIM(a.INV_ITEM_DESC) <> ' ' THEN a.INV_ITEM_DESC
        WHEN a.JOURNAL_DESC IS NOT NULL AND TRIM(a.JOURNAL_DESC) <> ' ' THEN a.JOURNAL_DESC
        WHEN a.FA_TRAN_DESC IS NOT NULL AND TRIM(a.FA_TRAN_DESC) <> ' ' THEN a.FA_TRAN_DESC
        WHEN a.DESCRIPTION IS NOT NULL AND TRIM(a.DESCRIPTION) <> ' ' THEN a.DESCRIPTION
        WHEN a.RLOC_DESC IS NOT NULL AND TRIM(a.RLOC_DESC) <> ' ' THEN a.RLOC_DESC
        ELSE a.DESC_LINE
    END as DESCRIPTION_FINAL,
    
    a.RECEIPT_REF,
    a.RECEIPT_NUM,
    a.POSTED_STATUS,
    a.REPORT_STATUS,
    a.DOCUMENT_REF,
    a.AR_INV_NO,
    a.AR_INV_TYPE,
    a.REVENUE_CODE,
    a.PRICING_CODE,
    a.ASSET_TY,
    a.EQUIP_NO,
    a.SUB_ASSET_NO,
    
    -- NOMOR_ASSET: Alias for ASSET_NO
    a.ASSET_NO as NOMOR_ASSET,
    
    -- Column1, Column2, Column3: Placeholder (NULL)
    NULL as Column1,
    NULL as Column2,
    NULL as Column3

FROM msf900 a
WHERE a.DSTRCT_CODE = 'UPPL'
  AND a.PROCESS_DATE >= '20250101'
  AND a.PROCESS_DATE <= '20251231'
  AND substr(a.ACCOUNT_CODE, 16, 4) IN {ee_filter}
ORDER BY a.CREATION_DATE DESC
            """
            
            cursor = connection.cursor()
            print("Executing query...")
            cursor.execute(query)
            
            # Fetch columns
            columns = [col[0] for col in cursor.description]
            
            # Fetch in chunks
            chunk_size = 500
            dfs = []
            total = 0
            
            while True:
                rows = cursor.fetchmany(chunk_size)
                if not rows:
                    break
                dfs.append(pd.DataFrame(rows, columns=columns))
                total += len(rows)
                print(f"Fetched {total} rows...")
            
            if dfs:
                final_df = pd.concat(dfs, ignore_index=True)
                output_file = "replicated_plq001_uppl_2025.xlsx"
                final_df.to_excel(output_file, index=False)
                print(f"\nTotal Rows: {total}")
                print(f"Exported to: {output_file}")
                
                # Calculate total amount for comparison
                total_amt = pd.to_numeric(final_df['TRAN_AMOUNT'], errors='coerce').sum()
                print(f"Total TRAN_AMOUNT: Rp {total_amt:,.2f}")
            else:
                print("No data found.")
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    replicate_plq001()
