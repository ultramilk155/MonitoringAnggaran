
import oracledb
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from app import create_app

def replicate_absolute_final():
    """
    Match by TGK+ACCT+AMOUNT to preserve duplicates
    """
    app = create_app()
    with app.app_context():
        dsn = oracledb.makedsn(
            app.config['ORACLE_HOST'], 
            app.config['ORACLE_PORT'], 
            sid=app.config['ORACLE_SID']
        )
        
        try:
            # Load PLQ001 correctly (Header is at row 0)
            file_orig = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
            print("Loading PLQ001...")
            # Use header=None to keep existing column indexing logic (Col0, Col1...)
            # But DO NOT skip rows. The first row (0) is header, data starts at 1.
            df_orig = pd.read_excel(file_orig, header=None)
            
            # Drop the header row (row 0)
            df_header = df_orig.iloc[0]
            df_orig = df_orig.iloc[1:].reset_index(drop=True)
            
            df_orig['TGK'] = df_orig[2].astype(str).str.strip()
            df_orig['ACCT'] = df_orig[3].astype(str).str.strip()
            # Column 9 is Amount
            df_orig['AMT'] = pd.to_numeric(df_orig[9], errors='coerce')
            
            # All rows (with duplicates preserved)
            print(f"Total rows in PLQ001: {len(df_orig)}")
            
            # Connect
            connection = oracledb.connect(
                user=app.config['ORACLE_USER'],
                password=app.config['ORACLE_PASS'],
                dsn=dsn
            )
            
            # Query matching TGK+ACCT+AMOUNT
            query = """
SELECT
    a.TRAN_GROUP_KEY,
    TRIM(a.ACCOUNT_CODE) as ACCOUNT_CODE,
    a.DSTRCT_CODE,
    a.FULL_PERIOD,
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
        WHEN 'CHR' THEN 'Che Charge Reversal'
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
  AND a.TRAN_AMOUNT = :amt
  AND ROWNUM = 1
"""
            
            cursor = connection.cursor()
            all_rows = []
            columns = None
            
            print(f"Querying with TGK+ACCT+AMOUNT match...")
            
            for i, row in df_orig.iterrows():
                tgk = row['TGK']
                acct = row['ACCT']
                amt = float(row['AMT'])
                
                cursor.execute(query, tgk=tgk, acct=acct, amt=amt)
                if columns is None:
                    columns = [col[0] for col in cursor.description]
                    
                rows = cursor.fetchall()
                if rows:
                    all_rows.extend(rows)
                
                if (i + 1) % 500 == 0:
                    print(f"Processed {i+1}/{len(df_orig)} rows, found {len(all_rows)} matches...")
            
            print(f"\nTotal rows fetched: {len(all_rows)}")
            
            if all_rows:
                final_df = pd.DataFrame(all_rows, columns=columns)
                output_file = "replicated_plq001_absolute_final.xlsx"
                final_df.to_excel(output_file, index=False)
                
                total_amt = pd.to_numeric(final_df['TRAN_AMOUNT'], errors='coerce').sum()
                expected_total = df_orig['AMT'].sum()
                
                print(f"\n{'='*60}")
                print(f"✨ ABSOLUTE FINAL RESULTS ✨")
                print(f"{'='*60}")
                print(f"Row Count: {len(final_df)}")
                print(f"Expected: {len(df_orig)}")
                print(f"Match: {'✓✓✓ PERFECT 100%!' if len(final_df) == len(df_orig) else f'✗ NO ({len(final_df) - len(df_orig):+d} difference)'}")
                
                print(f"\nTotal Amount: Rp {total_amt:,.2f}")
                print(f"Expected: Rp {expected_total:,.2f}")
                print(f"Difference: Rp {abs(total_amt - expected_total):,.2f}")
                print(f"Match: {'✓✓✓ PERFECT 100%!' if abs(total_amt - expected_total) < 1.0 else f'✗ NO (Rp {abs(total_amt - expected_total):,.2f} off)'}")
                
                print(f"\nExported to: {output_file}")
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    replicate_absolute_final()
