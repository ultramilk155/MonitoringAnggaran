
import pandas as pd

def find_extra_tgks():
    file_orig = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
    file_repl = "replicated_plq001_exact.xlsx"
    
    print("Finding extra TGKs in replication...")
    
    # Original
    df_orig = pd.read_excel(file_orig, header=None, skiprows=8)
    df_orig['TGK'] = df_orig[2].astype(str).str.strip()
    orig_tgks = set(df_orig['TGK'].unique())
    
    # Replicated
    df_repl = pd.read_excel(file_repl)
    df_repl['TGK'] = df_repl['TRAN_GROUP_KEY'].astype(str).str.strip()
    repl_tgks = set(df_repl['TGK'].unique())
    
    # Extra in replication
    extra_tgks = repl_tgks - orig_tgks
    print(f"\nExtra TGKs in Replication (not in Original): {len(extra_tgks)}")
    
    # Analyze extra TGKs
    extra_df = df_repl[df_repl['TGK'].isin(extra_tgks)].copy()
    
    print(f"Extra rows count: {len(extra_df)}")
    print(f"Extra amount total: Rp {extra_df['TRAN_AMOUNT'].sum():,.2f}")
    
    # Breakdown by DESC_TRAN_TYPE
    print("\nExtra rows by DESC_TRAN_TYPE:")
    print(extra_df['DESC_TRAN_TYPE'].value_counts())
    
    # Breakdown by FULL_PERIOD
    print("\nExtra rows by FULL_PERIOD:")
    print(extra_df['FULL_PERIOD'].value_counts().sort_index())
    
    # Breakdown by EXPENSE_ELEMENT
    print("\nExtra rows by EXPENSE_ELEMENT:")
    print(extra_df['EXPENSE_ELEMENT'].value_counts())
    
    # Check CREATION_DATE range
    print("\nExtra rows CREATION_DATE range:")
    print(f"Min: {extra_df['CREATION_DATE'].min()}, Max: {extra_df['CREATION_DATE'].max()}")
    
    # Sample extra rows
    print("\nSample extra rows:")
    print(extra_df[['TGK', 'FULL_PERIOD', 'EXPENSE_ELEMENT', 'DESC_TRAN_TYPE', 'TRAN_AMOUNT', 'CREATION_DATE']].head(10).to_string(index=False))
    
    # Save extra rows for inspection
    extra_df.to_excel("extra_tgks_not_in_original.xlsx", index=False)
    print("\nSaved to extra_tgks_not_in_original.xlsx")

if __name__ == "__main__":
    find_extra_tgks()
