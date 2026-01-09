
import oracledb
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from app import create_app

def replicate_with_aggregation():
    """
    Use GROUP BY to aggregate amounts per TGK+ACCT
    """
    app = create_app()
    with app.app_context():
        dsn = oracledb.makedsn(
            app.config['ORACLE_HOST'], 
            app.config['ORACLE_PORT'], 
            sid=app.config['ORACLE_SID']
        )
        
        try:
            # Load PLQ001
            file_orig = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
            print("Loading PLQ001...")
            df_orig = pd.read_excel(file_orig, header=None, skiprows=8)
            
            df_orig['TGK'] = df_orig[2].astype(str).str.strip()
            df_orig['ACCT'] = df_orig[3].astype(str).str.strip()
            df_orig['AMT'] = pd.to_numeric(df_orig[9], errors='coerce')
            
            # Get unique TGK+ACCT combos (removing duplicates from PLQ001)
            unique_pairs = df_orig[['TGK', 'ACCT']].drop_duplicates()
            pairs = list(zip(unique_pairs['TGK'], unique_pairs['ACCT']))
            
            print(f"Found {len(pairs)} unique TGK+ACCT pairs")
            print(f"PLQ001 has {len(df_orig)} total rows")
            
            # Also get expected amounts per TGK+ACCT from PLQ001
            expected_amounts = df_orig.groupby(['TGK', 'ACCT'])['AMT'].sum().reset_index()
            expected_dict = {(row['TGK'], row['ACCT']): row['AMT'] for _, row in expected_amounts.iterrows()}
            
            # Connect
            connection = oracledb.connect(
                user=app.config['ORACLE_USER'],
                password=app.config['ORACLE_PASS'],
                dsn=dsn
            )
            
            # Query with aggregation
            query = """
SELECT
    a.TRAN_GROUP_KEY,
    TRIM(a.ACCOUNT_CODE) as ACCOUNT_CODE,
    a.DSTRCT_CODE,
    a.FULL_PERIOD,
    MAX(a.JOURNAL_DESC) as GL_DESC,
    MAX(a.MIMS_SL_KEY) as SUBLEDGER,
    substr(MAX(a.ACCOUNT_CODE), 16, 4) as EXPENSE_ELEMENT,
    substr(MAX(a.ACCOUNT_CODE), 6, 3) as SEGMENT_ACTIVITY_MT_TYPE,
    MAX(CASE a.TRAN_TYPE 
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
    END) as DESC_TRAN_TYPE,
    SUM(a.TRAN_AMOUNT) as TRAN_AMOUNT,
    MAX(a.CHEQUE_NO) as CHEQUE_NO,
    MAX(NVL(a.TRNDTE_REVSD, a.PROCESS_DATE)) as TRANSACTION_DATE,
    MAX(a.CREATION_DATE) as CREATION_DATE,
    MAX(a.CREATION_USER) as CREATION_USER,
    MAX(a.MANJNL_VCHR) as MANJNL_VCHR,
    MAX(a.PROJECT_NO) as PROJECT_NO,
    MAX((SELECT p.PROJ_DESC FROM msf660 p 
         WHERE p.DSTRCT_CODE = a.DSTRCT_CODE 
         AND p.PROJECT_NO = a.PROJECT_NO 
         AND ROWNUM = 1)) as PROJECT_DESC,
    MAX(CASE 
        WHEN a.INV_ITEM_DESC IS NOT NULL AND TRIM(a.INV_ITEM_DESC) <> ' ' THEN a.INV_ITEM_DESC
        WHEN a.JOURNAL_DESC IS NOT NULL AND TRIM(a.JOURNAL_DESC) <> ' ' THEN a.JOURNAL_DESC
        WHEN a.FA_TRAN_DESC IS NOT NULL AND TRIM(a.FA_TRAN_DESC) <> ' ' THEN a.FA_TRAN_DESC
        WHEN a.DESCRIPTION IS NOT NULL AND TRIM(a.DESCRIPTION) <> ' ' THEN a.DESCRIPTION
        WHEN a.RLOC_DESC IS NOT NULL AND TRIM(a.RLOC_DESC) <> ' ' THEN a.RLOC_DESC
        ELSE a.DESC_LINE
    END) as DESCRIPTION_FINAL,
    MAX(a.RECEIPT_REF) as RECEIPT_REF,
    MAX(a.RECEIPT_NUM) as RECEIPT_NUM,
    MAX(a.POSTED_STATUS) as POSTED_STATUS,
    MAX(a.REPORT_STATUS) as REPORT_STATUS,
    MAX(a.DOCUMENT_REF) as DOCUMENT_REF,
    MAX(a.AR_INV_NO) as AR_INV_NO,
    MAX(a.AR_INV_TYPE) as AR_INV_TYPE,
    MAX(a.REVENUE_CODE) as REVENUE_CODE,
    MAX(a.PRICING_CODE) as PRICING_CODE,
    MAX(a.ASSET_TY) as ASSET_TY,
    MAX(a.EQUIP_NO) as EQUIP_NO,
    MAX(a.SUB_ASSET_NO) as SUB_ASSET_NO,
    MAX(a.ASSET_NO) as NOMOR_ASSET,
    NULL as Column1,
    NULL as Column2,
    NULL as Column3
FROM msf900 a
WHERE a.DSTRCT_CODE = 'UPPL'
  AND a.TRAN_GROUP_KEY = :tgk
  AND TRIM(a.ACCOUNT_CODE) = :acct
GROUP BY a.TRAN_GROUP_KEY, TRIM(a.ACCOUNT_CODE), a.DSTRCT_CODE, a.FULL_PERIOD
"""
            
            cursor = connection.cursor()
            all_rows = []
            columns = None
            amt_idx = None
            mismatches = []
            
            print(f"Querying with GROUP BY aggregation...")
            
            for i, (tgk, acct) in enumerate(pairs):
                cursor.execute(query, tgk=tgk, acct=acct)
                if columns is None:
                    columns = [col[0] for col in cursor.description]
                    # Find TRAN_AMOUNT index
                    amt_idx = columns.index('TRAN_AMOUNT')
                    print(f"TRAN_AMOUNT is at column index {amt_idx}")
                    
                rows = cursor.fetchall()
                
                if rows:
                    all_rows.extend(rows)
                    
                    # Check amount match
                    db_amt = float(rows[0][amt_idx]) if rows[0][amt_idx] is not None else 0.0
                    expected_amt = float(expected_dict.get((tgk, acct), 0))
                    
                    if abs(db_amt - expected_amt) > 0.01:  # Allow tiny floating point diff
                        mismatches.append({
                            'TGK': tgk,
                            'ACCT': acct,
                            'Expected': expected_amt,
                            'DB': db_amt,
                            'Diff': db_amt - expected_amt
                        })
                
                if (i + 1) % 500 == 0:
                    print(f"Processed {i+1}/{len(pairs)} pairs, found {len(all_rows)} rows...")
            
            print(f"\nTotal rows: {len(all_rows)}")
            
            if all_rows:
                final_df = pd.DataFrame(all_rows, columns=columns)
                output_file = "replicated_plq001_final.xlsx"
                final_df.to_excel(output_file, index=False)
                
                total_amt = pd.to_numeric(final_df['TRAN_AMOUNT'], errors='coerce').sum()
                expected_total = df_orig['AMT'].sum()
                
                print(f"\n{'='*60}")
                print(f"FINAL RESULTS:")
                print(f"{'='*60}")
                print(f"Row Count: {len(final_df)}")
                print(f"Expected: {len(df_orig)}")
                print(f"Match: {'✓ YES!' if len(final_df) == len(df_orig) else '✗ NO'}")
                
                print(f"\nTotal Amount: Rp {total_amt:,.2f}")
                print(f"Expected: Rp {expected_total:,.2f}")
                print(f"Difference: Rp {abs(total_amt - expected_total):,.2f}")
                print(f"Match: {'✓ YES!' if abs(total_amt - expected_total) < 1.0 else '✗ NO'}")
                
                if mismatches:
                    print(f"\nAmount mismatches: {len(mismatches)}")
                    print("Sample mismatches:")
                    for m in mismatches[:5]:
                        print(f"  {m['TGK'][:30]}... | Expected: {m['Expected']:,.2f} | DB: {m['DB']:,.2f}")
                
                print(f"\nExported to: {output_file}")
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    replicate_with_aggregation()
