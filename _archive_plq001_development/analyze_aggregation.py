
import pandas as pd

def analyze_aggregation():
    file_orig = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
    file_repl = "replicated_plq001_exact.xlsx"
    
    print("Analyzing TRAN_GROUP_KEY patterns...")
    
    # Original (no header)
    df_orig = pd.read_excel(file_orig, header=None, skiprows=8)
    df_orig.columns = [f"Col{i}" for i in range(len(df_orig.columns))]
    # Col 2 = TRAN_GROUP_KEY, Col 3 = ACCOUNT_CODE
    df_orig['TGK'] = df_orig['Col2'].astype(str).str.strip()
    df_orig['ACCT'] = df_orig['Col3'].astype(str).str.strip()
    df_orig['AMT'] = pd.to_numeric(df_orig['Col9'], errors='coerce')
    
    # Replicated
    df_repl = pd.read_excel(file_repl)
    df_repl['TGK'] = df_repl['TRAN_GROUP_KEY'].astype(str).str.strip()
    df_repl['ACCT'] = df_repl['ACCOUNT_CODE'].astype(str).str.strip()
    df_repl['AMT'] = pd.to_numeric(df_repl['TRAN_AMOUNT'], errors='coerce')
    
    print(f"\nOriginal unique TRAN_GROUP_KEY: {df_orig['TGK'].nunique()}")
    print(f"Replicated unique TRAN_GROUP_KEY: {df_repl['TGK'].nunique()}")
    
    # Check if Original has 1 row per TGK+ACCT combo
    orig_combo = df_orig.groupby(['TGK', 'ACCT']).size()
    repl_combo = df_repl.groupby(['TGK', 'ACCT']).size()
    
    print(f"\nOriginal unique TGK+ACCT combos: {len(orig_combo)}")
    print(f"Replicated unique TGK+ACCT combos: {len(repl_combo)}")
    
    # Check for duplicates in Original
    orig_dups = orig_combo[orig_combo > 1]
    repl_dups = repl_combo[repl_combo > 1]
    
    print(f"\nOriginal TGK+ACCT duplicates: {len(orig_dups)}")
    print(f"Replicated TGK+ACCT duplicates: {len(repl_dups)}")
    
    if len(repl_dups) > 0:
        print("\nSample duplicates in Replicated:")
        print(repl_dups.head(10))
        
        # Get one duplicate example
        first_dup = repl_dups.index[0]
        print(f"\nExample duplicate rows for TGK={first_dup[0]}, ACCT={first_dup[1]}:")
        dup_rows = df_repl[(df_repl['TGK'] == first_dup[0]) & (df_repl['ACCT'] == first_dup[1])]
        print(dup_rows[['TGK', 'ACCT', 'AMT', 'DESCRIPTION_FINAL']].to_string(index=False))
    
    # Check if aggregating by TGK+ACCT with SUM would match
    print("\n=== Testing Aggregation ===")
    repl_agg = df_repl.groupby(['TGK', 'ACCT']).agg({'AMT': 'sum'}).reset_index()
    print(f"Replicated after TGK+ACCT aggregation: {len(repl_agg)} rows")
    print(f"Original: {len(df_orig)} rows")
    
    if len(repl_agg) != len(df_orig):
        # Try different aggregation keys
        print("\nTrying just TGK...")
        repl_tgk = df_repl.groupby('TGK').agg({'AMT': 'sum'}).reset_index()
        orig_tgk = df_orig.groupby('TGK').agg({'AMT': 'sum'}).reset_index()
        print(f"Replicated TGK groups: {len(repl_tgk)}")
        print(f"Original TGK groups: {len(orig_tgk)}")

if __name__ == "__main__":
    analyze_aggregation()
