
import pandas as pd

def verify_100_match():
    file_orig = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
    file_repl = "replicated_plq001_100percent.xlsx"
    
    print("Verifying 100% match...")
    
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
    
    print(f"\nOriginal: {len(df_orig)} rows, Total: Rp {df_orig['AMT'].sum():,.2f}")
    print(f"Replicated: {len(df_repl)} rows, Total: Rp {df_repl['AMT'].sum():,.2f}")
    
    # Match by TGK + ACCT combo
    orig_combos = set(zip(df_orig['TGK'], df_orig['ACCT']))
    repl_combos = set(zip(df_repl['TGK'], df_repl['ACCT']))
    
    print(f"\nOriginal unique TGK+ACCT: {len(orig_combos)}")
    print(f"Replicated unique TGK+ACCT: {len(repl_combos)}")
    
    extra_in_repl = repl_combos - orig_combos
    missing_in_repl = orig_combos - repl_combos
    
    print(f"\nExtra in Replicated (not in Original): {len(extra_in_repl)}")
    print(f"Missing in Replicated (in Original but not Repl): {len(missing_in_repl)}")
    
    if extra_in_repl:
        print("\nSample Extra in Replicated:")
        for combo in list(extra_in_repl)[:5]:
            rows = df_repl[(df_repl['TGK'] == combo[0]) & (df_repl['ACCT'] == combo[1])]
            print(f"  TGK={combo[0][:30]}..., ACCT={combo[1]}, AMT={rows['AMT'].sum():,.2f}")
    
    if missing_in_repl:
        print("\nSample Missing in Replicated:")
        for combo in list(missing_in_repl)[:5]:
            rows = df_orig[(df_orig['TGK'] == combo[0]) & (df_orig['ACCT'] == combo[1])]
            print(f"  TGK={combo[0][:30]}..., ACCT={combo[1]}, AMT={rows['AMT'].sum():,.2f}")
    
    # Compare totals by EE
    print("\n=== Comparison by EXPENSE_ELEMENT ===")
    df_orig['EE'] = df_orig['Col6'].astype(str).str.strip()
    
    orig_ee = df_orig.groupby('EE')['AMT'].agg(['sum', 'count']).rename(columns={'sum': 'Orig', 'count': 'Orig_N'})
    repl_ee = df_repl.groupby('EXPENSE_ELEMENT')['AMT'].agg(['sum', 'count']).rename(columns={'sum': 'Repl', 'count': 'Repl_N'})
    
    comp = orig_ee.join(repl_ee, how='outer').fillna(0)
    comp['Diff'] = comp['Repl'] - comp['Orig']
    comp['Diff_N'] = comp['Repl_N'] - comp['Orig_N']
    print(comp.to_string())

if __name__ == "__main__":
    verify_100_match()
