
import pandas as pd
import numpy as np

def compare_exact_match():
    """
    Compare by matching exact TGK+ACCT+AMOUNT combinations
    """
    file_orig = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
    file_repl = "replicated_plq001_absolute_final.xlsx"
    
    print("Loading files...")
    
    # Original
    df_orig = pd.read_excel(file_orig, header=None, skiprows=8)
    df_orig.columns = [f"Col{i}" for i in range(len(df_orig.columns))]
    
    ori = pd.DataFrame({
        'TGK': df_orig['Col2'].astype(str).str.strip(),
        'ACCT': df_orig['Col3'].astype(str).str.strip(),
        'AMT': pd.to_numeric(df_orig['Col9'], errors='coerce'),
        'PROJECT_NO_ORIG': df_orig['Col15'].astype(str).str.strip() if 15 < len(df_orig.columns) else '',
        'DESC_ORIG': df_orig['Col16'].astype(str).str.strip() if 16 < len(df_orig.columns) else '',
    })
    
    # Replicated
    df_repl = pd.read_excel(file_repl)
    rep = pd.DataFrame({
        'TGK': df_repl['TRAN_GROUP_KEY'].astype(str).str.strip(),
        'ACCT': df_repl['ACCOUNT_CODE'].astype(str).str.strip(),
        'AMT': pd.to_numeric(df_repl['TRAN_AMOUNT'], errors='coerce'),
        'PROJECT_NO_REPL': df_repl['PROJECT_NO'].astype(str).str.strip() if 'PROJECT_NO' in df_repl.columns else '',
        'DESC_REPL': df_repl['DESCRIPTION_FINAL'].astype(str).str.strip() if 'DESCRIPTION_FINAL' in df_repl.columns else '',
    })
    
    print(f"Original: {len(ori)} rows")
    print(f"Replicated: {len(rep)} rows")
    
    # Merge on TGK+ACCT+AMT
    merged = ori.merge(rep, on=['TGK', 'ACCT', 'AMT'], how='outer', indicator=True)
    
    both = merged[merged['_merge'] == 'both']
    only_orig = merged[merged['_merge'] == 'left_only']
    only_repl = merged[merged['_merge'] == 'right_only']
    
    print(f"\n{'='*60}")
    print(f"MERGE RESULTS:")
    print(f"{'='*60}")
    print(f"Matched (in both): {len(both)}")
    print(f"Only in original: {len(only_orig)}")
    print(f"Only in replicated: {len(only_repl)}")
    
    if len(only_orig) > 0 or len(only_repl) > 0:
        print("\n⚠️ NOT ALL ROWS MATCHED!")
        if len(only_orig) > 0:
            print(f"\nSample rows only in original:")
            print(only_orig[['TGK', 'ACCT', 'AMT', 'PROJECT_NO_ORIG']].head().to_string())
        if len(only_repl) > 0:
            print(f"\nSample rows only in replicated:")
            print(only_repl[['TGK', 'ACCT', 'AMT', 'PROJECT_NO_REPL']].head().to_string())
    
    # For matched rows, check PROJECT_NO
    print(f"\n{'='*60}")
    print(f"PROJECT_NO FIELD COMPARISON (matched rows):")
    print(f"{'='*60}")
    
    proj_mismatch = both[both['PROJECT_NO_ORIG'] != both['PROJECT_NO_REPL']]
    
    print(f"Rows with PROJECT_NO mismatch: {len(proj_mismatch)}")
    
    if len(proj_mismatch) > 0:
        print(f"\nFirst 10 PROJECT_NO mismatches:")
        for idx, row in proj_mismatch.head(10).iterrows():
            print(f"\nTGK: {row['TGK'][:50]}")
            print(f"  Original: '{row['PROJECT_NO_ORIG']}'")
            print(f"  Replicated: '{row['PROJECT_NO_REPL']}'")
        
        # Save mismatches
        proj_mismatch.to_excel("project_no_mismatches.xlsx", index=False)
        print(f"\nFull PROJECT_NO mismatch report: project_no_mismatches.xlsx")
    else:
        print("✅ All PROJECT_NO values match!")
    
    # Check DESCRIPTION_FINAL
    desc_mismatch = both[both['DESC_ORIG'] != both['DESC_REPL']]
    print(f"\nRows with DESCRIPTION mismatch: {len(desc_mismatch)}")
    
    if len(desc_mismatch) > 0:
        print(f"Sample DESCRIPTION mismatches (first 3):")
        for idx, row in desc_mismatch.head(3).iterrows():
            print(f"\nTGK: {row['TGK'][:50]}")
            print(f"  Original: '{row['DESC_ORIG'][:60]}'")
            print(f"  Replicated: '{row['DESC_REPL'][:60]}'")

if __name__ == "__main__":
    compare_exact_match()
