
import pandas as pd

def investigate():
    file_orig = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
    file_repl = "replicated_plq001_100percent.xlsx"
    
    print("Investigating the 3 extra rows...")
    
    # Original
    df_orig = pd.read_excel(file_orig, header=None, skiprows=8)
    df_orig.columns = [f"Col{i}" for i in range(len(df_orig.columns))]
    df_orig['TGK'] = df_orig['Col2'].astype(str).str.strip()
    df_orig['ACCT'] = df_orig['Col3'].astype(str).str.strip()
    df_orig['AMT'] = pd.to_numeric(df_orig['Col9'], errors='coerce')
    
    # Replicated  
    df_repl = pd.read_excel(file_repl)
    df_repl['TGK'] = df_repl['TRAN_GROUP_KEY'].astype(str).str.strip()
    df_repl['ACCT'] = df_repl['ACCOUNT_CODE'].astype(str).str.strip()
    df_repl['AMT'] = pd.to_numeric(df_repl['TRAN_AMOUNT'], errors='coerce')
    
    # Find extra combos
    orig_combos = set(zip(df_orig['TGK'], df_orig['ACCT']))
    repl_combos = set(zip(df_repl['TGK'], df_repl['ACCT']))
    
    extra_in_repl = repl_combos - orig_combos
    
    print(f"\nExtra combos: {len(extra_in_repl)}")
    for combo in extra_in_repl:
        print(f"\nTGK: {combo[0]}")
        print(f"ACCT: {combo[1]}")
        
        # Get rows from replication
        rows = df_repl[(df_repl['TGK'] == combo[0]) & (df_repl['ACCT'] == combo[1])]
        print(f"Amount: Rp {rows['AMT'].sum():,.2f}")
        print(f"Description: {rows['DESCRIPTION_FINAL'].iloc[0]}")
        print(f"Posted Status: {rows['POSTED_STATUS'].iloc[0]}")
        print(f"Report Status: {rows['REPORT_STATUS'].iloc[0]}")
    
    # Try aggregating by TGK+ACCT
    print("\n" + "="*50)
    print("APPROACH 1: Aggregate by TGK+ACCT with SUM")
    print("="*50)
    
    repl_agg = df_repl.groupby(['TGK', 'ACCT']).agg({
        'AMT': 'sum',
        'FULL_PERIOD': 'first',
        'EXPENSE_ELEMENT': 'first'
    }).reset_index()
    
    print(f"After aggregation: {len(repl_agg)} rows")
    print(f"Original: {len(df_orig)} rows")
    print(f"Difference: {len(repl_agg) - len(df_orig)}")
    
    total_agg = repl_agg['AMT'].sum()
    total_orig = df_orig['AMT'].sum()
    print(f"\nTotal after agg: Rp {total_agg:,.2f}")
    print(f"Original total: Rp {total_orig:,.2f}")
    print(f"Difference: Rp {total_agg - total_orig:,.2f}")
    
    if len(repl_agg) == len(df_orig):
        print("\n✓ ROW COUNT MATCHES after aggregation!")
        # Save this version
        # But we need full columns, not just aggregated
        print("\nNeed to create full query with aggregation...")

if __name__ == "__main__":
    investigate()
