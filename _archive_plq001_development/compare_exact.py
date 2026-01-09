
import pandas as pd

def compare_exact():
    file_orig = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
    file_repl = "replicated_plq001_exact.xlsx"
    
    print("Loading files for comparison...")
    
    # Original (no header)
    df_orig = pd.read_excel(file_orig, header=None, skiprows=8)
    df_orig.columns = [f"Col{i}" for i in range(len(df_orig.columns))]
    df_orig = df_orig.rename(columns={'Col1': 'FULL_PERIOD', 'Col6': 'EXPENSE_ELEMENT', 'Col9': 'TRAN_AMOUNT'})
    df_orig['TRAN_AMOUNT'] = pd.to_numeric(df_orig['TRAN_AMOUNT'], errors='coerce')
    
    # Replicated
    df_repl = pd.read_excel(file_repl)
    df_repl['TRAN_AMOUNT'] = pd.to_numeric(df_repl['TRAN_AMOUNT'], errors='coerce')
    
    print(f"\nOriginal PLQ001: {len(df_orig)} rows, Total: Rp {df_orig['TRAN_AMOUNT'].sum():,.2f}")
    print(f"Replicated: {len(df_repl)} rows, Total: Rp {df_repl['TRAN_AMOUNT'].sum():,.2f}")
    
    # Compare by EXPENSE_ELEMENT
    print("\n=== Comparison by EXPENSE_ELEMENT ===")
    orig_ee = df_orig.groupby('EXPENSE_ELEMENT')['TRAN_AMOUNT'].agg(['sum', 'count']).rename(columns={'sum': 'Orig_Sum', 'count': 'Orig_Count'})
    repl_ee = df_repl.groupby('EXPENSE_ELEMENT')['TRAN_AMOUNT'].agg(['sum', 'count']).rename(columns={'sum': 'Repl_Sum', 'count': 'Repl_Count'})
    
    comp_ee = orig_ee.join(repl_ee, how='outer').fillna(0)
    comp_ee['Diff_Sum'] = comp_ee['Repl_Sum'] - comp_ee['Orig_Sum']
    comp_ee['Diff_Count'] = comp_ee['Repl_Count'] - comp_ee['Orig_Count']
    
    print(comp_ee.to_string())
    
    # Compare by FULL_PERIOD
    print("\n=== Comparison by FULL_PERIOD ===")
    orig_period = df_orig.groupby('FULL_PERIOD')['TRAN_AMOUNT'].agg(['sum', 'count']).rename(columns={'sum': 'Orig_Sum', 'count': 'Orig_Count'})
    repl_period = df_repl.groupby('FULL_PERIOD')['TRAN_AMOUNT'].agg(['sum', 'count']).rename(columns={'sum': 'Repl_Sum', 'count': 'Repl_Count'})
    
    comp_period = orig_period.join(repl_period, how='outer').fillna(0)
    comp_period['Diff_Sum'] = comp_period['Repl_Sum'] - comp_period['Orig_Sum']
    comp_period['Diff_Count'] = comp_period['Repl_Count'] - comp_period['Orig_Count']
    
    print(comp_period.to_string())
    
    # Save comparison
    with pd.ExcelWriter("comparison_exact_vs_original.xlsx") as writer:
        comp_ee.to_excel(writer, sheet_name='By_EE')
        comp_period.to_excel(writer, sheet_name='By_Period')
    
    print("\nSaved to comparison_exact_vs_original.xlsx")

if __name__ == "__main__":
    compare_exact()
