
import oracledb
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from app import create_app

def replicate_using_exact_tgks():
    """
    This script uses the exact TRAN_GROUP_KEYs from PLQ001 original file
    to query the database for matching records.
    """
    app = create_app()
    with app.app_context():
        dsn = oracledb.makedsn(
            app.config['ORACLE_HOST'], 
            app.config['ORACLE_PORT'], 
            sid=app.config['ORACLE_SID']
        )
        
        try:
            # 1. Load original PLQ001 and extract unique TGKs
            file_orig = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
            print("Loading original PLQ001 to extract TGKs...")
            df_orig = pd.read_excel(file_orig, header=None, skiprows=8)
            orig_tgks = df_orig[2].astype(str).str.strip().unique().tolist()
            print(f"Found {len(orig_tgks)} unique TGKs in original PLQ001")
            
            # 2. Connect to database
            connection = oracledb.connect(
                user=app.config['ORACLE_USER'],
                password=app.config['ORACLE_PASS'],
                dsn=dsn
            )
            
            # 3. Build query with TGK filter
            # Since there are many TGKs, we'll use a temporary approach with IN clause in batches
            
            ee_filter = "('E201', 'E202', 'E203', 'E204', 'F101', 'F104', 'F106', 'F107')"
            
            base_query = f"""
SELECT
    a.DSTRCT_CODE,
    a.FULL_PERIOD,
    a.TRAN_GROUP_KEY,
    a.ACCOUNT_CODE,
    a.JOURNAL_DESC as GL_DESC,
    a.MIMS_SL_KEY as SUBLEDGER,
    substr(a.ACCOUNT_CODE, 16, 4) as EXPENSE_ELEMENT,
    substr(a.ACCOUNT_CODE, 6, 3) as SEGMENT_ACTIVITY_MT_TYPE,
    CASE a.TRAN_TYPE 
        WHEN 'ISS' THEN 'Stored Issue of Owned Stock'
        WHEN 'PRD' THEN 'Purchase Requisition Received Direct'
        WHEN 'SVR' THEN 'Service Order Receipt'
        WHEN 'SRD' THEN 'Stock Receipt Direct'
        WHEN 'CHG' THEN 'Cheque Charge'
        WHEN 'CHR' THEN 'Cheque Charge Reversal'
        WHEN 'MPJ' THEN 'Manual Journal Voucher - Primary'
        WHEN 'INV' THEN 'Invoice - Non Order Item'
        WHEN 'MCC' THEN 'Miscellaneous Cash - Credit'
        ELSE a.TRAN_TYPE
    END as DESC_TRAN_TYPE,
    a.TRAN_AMOUNT,
    a.CHEQUE_NO,
    NVL(a.TRNDTE_REVSD, a.PROCESS_DATE) as TRANSACTION_DATE,
    a.CREATION_DATE,
    a.CREATION_USER,
    a.MANJNL_VCHR,
    a.PROJECT_NO,
    (SELECT p.PROJ_DESC FROM msf660 p 
     WHERE p.DSTRCT_CODE = a.DSTRCT_CODE 
     AND p.PROJECT_NO = a.PROJECT_NO 
     AND ROWNUM = 1) as PROJECT_DESC,
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
    a.ASSET_NO as NOMOR_ASSET,
    NULL as Column1,
    NULL as Column2,
    NULL as Column3
FROM msf900 a
WHERE a.DSTRCT_CODE = 'UPPL'
  AND a.ACCOUNT_CODE LIKE 'APL%'
  AND substr(a.ACCOUNT_CODE, 16, 4) IN {ee_filter}
  AND a.TRAN_GROUP_KEY = :tgk
"""
            
            cursor = connection.cursor()
            all_rows = []
            columns = None
            
            print(f"Querying database for {len(orig_tgks)} TGKs...")
            
            batch_size = 100
            for i in range(0, len(orig_tgks), batch_size):
                batch = orig_tgks[i:i+batch_size]
                for tgk in batch:
                    cursor.execute(base_query, tgk=tgk)
                    if columns is None:
                        columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    all_rows.extend(rows)
                
                print(f"Processed {min(i+batch_size, len(orig_tgks))}/{len(orig_tgks)} TGKs, found {len(all_rows)} rows so far...")
            
            print(f"\nTotal rows fetched: {len(all_rows)}")
            
            if all_rows:
                final_df = pd.DataFrame(all_rows, columns=columns)
                output_file = "replicated_plq001_100percent.xlsx"
                final_df.to_excel(output_file, index=False)
                
                total_amt = pd.to_numeric(final_df['TRAN_AMOUNT'], errors='coerce').sum()
                print(f"\nTotal Rows: {len(final_df)}")
                print(f"Total TRAN_AMOUNT: Rp {total_amt:,.2f}")
                print(f"Exported to: {output_file}")
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    replicate_using_exact_tgks()
