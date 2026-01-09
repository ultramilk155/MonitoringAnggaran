
import oracledb
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from app import create_app

def replicate_perfect_match():
    """
    Perfect match using exact TGK+ACCT combinations from PLQ001 original
    """
    app = create_app()
    with app.app_context():
        dsn = oracledb.makedsn(
            app.config['ORACLE_HOST'], 
            app.config['ORACLE_PORT'], 
            sid=app.config['ORACLE_SID']
        )
        
        try:
            # 1. Load original PLQ001 and extract TGK+ACCT pairs
            file_orig = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
            print("Loading PLQ001 to extract exact TGK+ACCT pairs...")
            df_orig = pd.read_excel(file_orig, header=None, skiprows=8)
            
            df_orig['TGK'] = df_orig[2].astype(str).str.strip()
            df_orig['ACCT'] = df_orig[3].astype(str).str.strip()
            
            # Get list of TGK+ACCT pairs (keeping duplicates!)
            pairs = list(zip(df_orig['TGK'], df_orig['ACCT']))
            print(f"Found {len(pairs)} TGK+ACCT pairs (including duplicates)")
            
            # 2. Connect to database
            connection = oracledb.connect(
                user=app.config['ORACLE_USER'],
                password=app.config['ORACLE_PASS'],
                dsn=dsn
            )
            
            # 3. Query for each exact pair
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
  AND a.TRAN_GROUP_KEY = :tgk
  AND TRIM(a.ACCOUNT_CODE) = :acct
  AND ROWNUM = 1
"""
            
            cursor = connection.cursor()
            all_rows = []
            columns = None
            
            print(f"Querying for {len(pairs)} exact TGK+ACCT pairs...")
            
            batch_size = 100
            for i in range(0, len(pairs), batch_size):
                batch = pairs[i:i+batch_size]
                for tgk, acct in batch:
                    cursor.execute(base_query, tgk=tgk, acct=acct)
                    if columns is None:
                        columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    all_rows.extend(rows)
                
                if (i + batch_size) % 500 == 0:
                    print(f"Processed {min(i+batch_size, len(pairs))}/{len(pairs)} pairs, found {len(all_rows)} rows...")
            
            print(f"\nTotal rows fetched: {len(all_rows)}")
            
            if all_rows:
                final_df = pd.DataFrame(all_rows, columns=columns)
                output_file = "replicated_plq001_perfect.xlsx"
                final_df.to_excel(output_file, index=False)
                
                total_amt = pd.to_numeric(final_df['TRAN_AMOUNT'], errors='coerce').sum()
                
                print(f"\n{'='*60}")
                print(f"PERFECT MATCH RESULTS:")
                print(f"{'='*60}")
                print(f"Total Rows: {len(final_df)}")
                print(f"Expected: 2079")
                print(f"Match: {'✓ YES!' if len(final_df) == 2079 else '✗ NO'}")
                print(f"\nTotal TRAN_AMOUNT: Rp {total_amt:,.2f}")
                print(f"Expected: Rp 107,911,763,533.14")
                print(f"Difference: Rp {abs(total_amt - 107911763533.14):,.2f}")
                print(f"\nExported to: {output_file}")
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    replicate_perfect_match()
