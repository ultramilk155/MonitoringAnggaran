
import pandas as pd
import numpy as np

def compare_row_by_row():
    """
    Detailed row-by-row comparison between PLQ001 original and replicated
    """
    file_orig = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
    file_repl = "replicated_plq001_absolute_final.xlsx"
    
    print("Loading files for row-by-row comparison...")
    
    # Load original (no header, map to column names based on our knowledge)
    df_orig = pd.read_excel(file_orig, header=None, skiprows=8)
    df_orig.columns = [f"Col{i}" for i in range(len(df_orig.columns))]
    
    # Map known columns from original
    # Based on earlier analysis:
    # Col2=TGK, Col3=ACCT, Col6=EE, Col9=AMOUNT, Col16=Description, etc.
    orig_mapped = pd.DataFrame({
        'DSTRCT_CODE': df_orig['Col0'],
        'FULL_PERIOD': df_orig['Col1'],
        'TGK': df_orig['Col2'].astype(str).str.strip(),
        'ACCT': df_orig['Col3'].astype(str).str.strip(),
        'EXPENSE_ELEMENT': df_orig['Col6'].astype(str).str.strip(),
        'TRAN_AMOUNT': pd.to_numeric(df_orig['Col9'], errors='coerce'),
        'PROJECT_NO': df_orig['Col15'] if 15 < len(df_orig.columns) else None,
        'DESCRIPTION': df_orig['Col16'] if 16 < len(df_orig.columns) else None,
    })
    
    # Load replicated
    df_repl = pd.read_excel(file_repl)
    df_repl['TGK'] = df_repl['TRAN_GROUP_KEY'].astype(str).str.strip()
    df_repl['ACCT'] = df_repl['ACCOUNT_CODE'].astype(str).str.strip()
    
    print(f"\nOriginal rows: {len(orig_mapped)}")
    print(f"Replicated rows: {len(df_repl)}")
    
    # Sort both by TGK+ACCT+AMOUNT for alignment
    orig_mapped = orig_mapped.sort_values(['TGK', 'ACCT', 'TRAN_AMOUNT']).reset_index(drop=True)
    df_repl = df_repl.sort_values(['TGK', 'ACCT', 'TRAN_AMOUNT']).reset_index(drop=True)
    
    print("\n" + "="*60)
    print("FIELD-BY-FIELD COMPARISON")
    print("="*60)
    
    # Compare key fields
    mismatches = []
    
    for idx in range(len(orig_mapped)):
        orig_row = orig_mapped.iloc[idx]
        repl_row = df_repl.iloc[idx] if idx < len(df_repl) else None
        
        if repl_row is None:
            mismatches.append({
                'Row': idx,
                'Issue': 'Missing in replication',
                'TGK': orig_row['TGK']
            })
            continue
        
        # Check TRAN_AMOUNT
        orig_amt = float(orig_row['TRAN_AMOUNT']) if not pd.isna(orig_row['TRAN_AMOUNT']) else 0.0
        repl_amt = float(repl_row['TRAN_AMOUNT']) if not pd.isna(repl_row['TRAN_AMOUNT']) else 0.0
        
        if abs(orig_amt - repl_amt) > 0.01:
            mismatches.append({
                'Row': idx,
                'Field': 'TRAN_AMOUNT',
                'TGK': orig_row['TGK'],
                'Original': orig_amt,
                'Replicated': repl_amt
            })
        
        # Check EXPENSE_ELEMENT
        orig_ee = str(orig_row['EXPENSE_ELEMENT']).strip()
        repl_ee = str(repl_row['EXPENSE_ELEMENT']).strip() if 'EXPENSE_ELEMENT' in repl_row else ''
        
        if orig_ee != repl_ee:
            mismatches.append({
                'Row': idx,
                'Field': 'EXPENSE_ELEMENT',
                'TGK': orig_row['TGK'],
                'Original': orig_ee,
                'Replicated': repl_ee
            })
        
        # Check PROJECT_NO (this is where user mentioned issues)
        if 'PROJECT_NO' in orig_row and 'PROJECT_NO' in repl_row:
            orig_proj = str(orig_row['PROJECT_NO']).strip() if not pd.isna(orig_row['PROJECT_NO']) else ''
            repl_proj = str(repl_row['PROJECT_NO']).strip() if not pd.isna(repl_row['PROJECT_NO']) else ''
            
            if orig_proj != repl_proj:
                mismatches.append({
                    'Row': idx,
                    'Field': 'PROJECT_NO',
                    'TGK': orig_row['TGK'],
                    'Original': orig_proj,
                    'Replicated': repl_proj
                })
    
    print(f"\nTotal mismatches found: {len(mismatches)}")
    
    if mismatches:
        print("\n❌ MISMATCHES DETECTED:")
        print(f"First 10 mismatches:")
        for m in mismatches[:10]:
            print(f"\nRow {m['Row']}:")
            for k, v in m.items():
                if k != 'Row':
                    print(f"  {k}: {v}")
        
        # Save full mismatch report
        mismatch_df = pd.DataFrame(mismatches)
        mismatch_df.to_excel("row_by_row_mismatches.xlsx", index=False)
        print(f"\nFull mismatch report saved to: row_by_row_mismatches.xlsx")
    else:
        print("\n✅ PERFECT! All fields match row-by-row!")
    
    # Check for blank PROJECT_NO cases
    print("\n" + "="*60)
    print("BLANK PROJECT_NO ANALYSIS")
    print("="*60)
    
    blank_proj_orig = orig_mapped[orig_mapped['PROJECT_NO'].isna() | (orig_mapped['PROJECT_NO'] == '')]
    print(f"Original rows with blank PROJECT_NO: {len(blank_proj_orig)}")
    
    if 'PROJECT_NO' in df_repl.columns:
        blank_proj_repl = df_repl[df_repl['PROJECT_NO'].isna() | (df_repl['PROJECT_NO'] == '')]
        print(f"Replicated rows with blank PROJECT_NO: {len(blank_proj_repl)}")
        
        if len(blank_proj_orig) != len(blank_proj_repl):
            print(f"⚠️  Difference in blank PROJECT_NO count: {len(blank_proj_repl) - len(blank_proj_orig)}")

if __name__ == "__main__":
    compare_row_by_row()
