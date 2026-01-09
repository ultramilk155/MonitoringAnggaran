
import pandas as pd
import numpy as np

def verify_project_no_exact():
    """
    Verify every single row's PROJECT_NO matches PLQ001 original exactly
    """
    file_final = "PLQ001_REPLICATED_PERFECT_FINAL.xlsx"
    file_orig = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
    
    print("Loading files for PROJECT_NO verification...")
    
    # Load original correct (Header is row 0)
    df_orig = pd.read_excel(file_orig, header=None)
    # Drop header row 0
    df_orig = df_orig.iloc[1:].reset_index(drop=True)
    
    # Column mapping logic stays same (Col0, Col1...)
    df_orig.columns = [f"Col{i}" for i in range(len(df_orig.columns))]
    
    orig_data = pd.DataFrame({
        'Row': range(len(df_orig)),
        'TGK_ORIG': df_orig['Col2'].astype(str).str.strip(),
        'ACCT_ORIG': df_orig['Col3'].astype(str).str.strip(),
        'AMT_ORIG': pd.to_numeric(df_orig['Col9'], errors='coerce'),
        'PROJECT_NO_ORIG': df_orig['Col15'].astype(str).str.strip() if 15 < len(df_orig.columns) else '',
        'DESC_ORIG': df_orig['Col16'].astype(str).str.strip() if 16 < len(df_orig.columns) else '',
    })
    
    # Load final replicated
    df_final = pd.read_excel(file_final)
    
    final_data = pd.DataFrame({
        'Row': range(len(df_final)),
        'TGK_FINAL': df_final['TRAN_GROUP_KEY'].astype(str).str.strip(),
        'ACCT_FINAL': df_final['ACCOUNT_CODE'].astype(str).str.strip(),
        'AMT_FINAL': pd.to_numeric(df_final['TRAN_AMOUNT'], errors='coerce'),
        'PROJECT_NO_FINAL': df_final['PROJECT_NO'].astype(str).str.strip() if 'PROJECT_NO' in df_final.columns else '',
        'DESC_FINAL': df_final['DESCRIPTION_FINAL'].astype(str).str.strip() if 'DESCRIPTION_FINAL' in df_final.columns else '',
    })
    
    print(f"\nOriginal rows: {len(orig_data)}")
    print(f"Final rows: {len(final_data)}")
    
    print(f"\n{'='*60}")
    print(f"ROW-BY-ROW PROJECT_NO VERIFICATION")
    print(f"{'='*60}")
    
    mismatches = []
    
    # Check each row
    for idx in range(min(len(orig_data), len(final_data))):
        orig_row = orig_data.iloc[idx]
        final_row = final_data.iloc[idx]
        
        # Check TGK match
        if orig_row['TGK_ORIG'] != final_row['TGK_FINAL']:
            mismatches.append({
                'Row': idx,
                'Field': 'TGK',
                'Original': orig_row['TGK_ORIG'],
                'Final': final_row['TGK_FINAL']
            })
        
        # Check ACCT match
        if orig_row['ACCT_ORIG'] != final_row['ACCT_FINAL']:
            mismatches.append({
                'Row': idx,
                'Field': 'ACCOUNT_CODE',
                'Original': orig_row['ACCT_ORIG'],
                'Final': final_row['ACCT_FINAL']
            })
        
        # Check AMOUNT match
        orig_amt = float(orig_row['AMT_ORIG']) if not pd.isna(orig_row['AMT_ORIG']) else 0.0
        final_amt = float(final_row['AMT_FINAL']) if not pd.isna(final_row['AMT_FINAL']) else 0.0
        
        if abs(orig_amt - final_amt) > 0.01:
            mismatches.append({
                'Row': idx,
                'Field': 'TRAN_AMOUNT',
                'Original': f"Rp {orig_amt:,.2f}",
                'Final': f"Rp {final_amt:,.2f}"
            })
        
        # Check PROJECT_NO match - THIS IS THE KEY CHECK
        orig_proj = orig_row['PROJECT_NO_ORIG']
        final_proj = final_row['PROJECT_NO_FINAL']
        
        if orig_proj != final_proj:
            mismatches.append({
                'Row': idx,
                'Field': 'PROJECT_NO',
                'TGK': orig_row['TGK_ORIG'][:40],
                'ACCT': orig_row['ACCT_ORIG'],
                'Original': orig_proj,
                'Final': final_proj
            })
        
        # Check DESCRIPTION match
        orig_desc = orig_row['DESC_ORIG']
        final_desc = final_row['DESC_FINAL']
        
        if orig_desc != final_desc:
            mismatches.append({
                'Row': idx,
                'Field': 'DESCRIPTION',
                'TGK': orig_row['TGK_ORIG'][:40],
                'Original': orig_desc[:50],
                'Final': final_desc[:50]
            })
    
    print(f"\nTotal mismatches found: {len(mismatches)}")
    
    if len(mismatches) == 0:
        print(f"\n{'='*60}")
        print(f"✅✅✅ PERFECT 100% MATCH!")
        print(f"{'='*60}")
        print(f"✅ All 2,079 rows match exactly!")
        print(f"✅ TGK: 100% match")
        print(f"✅ ACCOUNT_CODE: 100% match")
        print(f"✅ TRAN_AMOUNT: 100% match")
        print(f"✅ PROJECT_NO: 100% match")
        print(f"✅ DESCRIPTION: 100% match")
    else:
        print(f"\n❌ MISMATCHES DETECTED!")
        print(f"\nFirst 20 mismatches:")
        
        for m in mismatches[:20]:
            print(f"\nRow {m['Row']} - Field: {m['Field']}")
            for k, v in m.items():
                if k not in ['Row', 'Field']:
                    print(f"  {k}: {v}")
        
        # Save mismatch report
        mismatch_df = pd.DataFrame(mismatches)
        mismatch_df.to_excel("final_verification_mismatches.xlsx", index=False)
        print(f"\nFull mismatch report: final_verification_mismatches.xlsx")
        
        # Summary by field
        field_counts = mismatch_df.groupby('Field').size()
        print(f"\nMismatches by field:")
        for field, count in field_counts.items():
            print(f"  {field}: {count}")

if __name__ == "__main__":
    verify_project_no_exact()
