
import pandas as pd

def check_orig_duplicates():
    file_orig = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
    
    print("Checking original PLQ001 for TGK+ACCT duplicates...")
    
    df_orig = pd.read_excel(file_orig, header=None, skiprows=8)
    df_orig.columns = [f"Col{i}" for i in range(len(df_orig.columns))]
    df_orig['TGK'] = df_orig['Col2'].astype(str).str.strip()
    df_orig['ACCT'] = df_orig['Col3'].astype(str).str.strip()
    df_orig['AMT'] = pd.to_numeric(df_orig['Col9'], errors='coerce')
    
    print(f"Total rows: {len(df_orig)}")
    
    # Check for duplicates
    combo_counts = df_orig.groupby(['TGK', 'ACCT']).size()
    duplicates = combo_counts[combo_counts > 1]
    
    print(f"Unique TGK+ACCT combos: {len(combo_counts)}")
    print(f"Duplicate TGK+ACCT combos: {len(duplicates)}")
    
    if len(duplicates) > 0:
        print("\nSample duplicates in ORIGINAL PLQ001:")
        print(duplicates.head(10))
        
        # Look at one example
        first_dup = duplicates.index[0]
        print(f"\nExample duplicate: TGK={first_dup[0][:40]}..., ACCT={first_dup[1]}")
        dup_rows = df_orig[(df_orig['TGK'] == first_dup[0]) & (df_orig['ACCT'] == first_dup[1])]
        print(f"Rows: {len(dup_rows)}")
        print(dup_rows[['Col2', 'Col3', 'Col9', 'Col16']].to_string(index=False))
    
    # Now check the specific TGK from our extra rows
    target_tgk = 'UPPL2025013130891360000JI82M'
    print(f"\n" + "="*60)
    print(f"Checking TGK: {target_tgk} in ORIGINAL PLQ001")
    print("="*60)
    
    target_rows = df_orig[df_orig['TGK'] == target_tgk]
    print(f"Found {len(target_rows)} rows for this TGK in original")
    
    if len(target_rows) > 0:
        print("\nAccount codes for this TGK in original:")
        print(target_rows[['Col3', 'Col9']].to_string(index=False))
    else:
        print("TGK NOT FOUND in original PLQ001!")

if __name__ == "__main__":
    check_orig_duplicates()
