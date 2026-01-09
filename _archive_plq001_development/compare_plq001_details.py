
import pandas as pd
import os

def compare_details():
    file_original = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
    file_replicated = "replicated_plq001_uppl_2025.xlsx"
    
    print("Loading files...")
    
    # Original PLQ001 (no header, skip 8 rows)
    # Based on earlier inspection:
    # Col 2 = TRAN_GROUP_KEY
    # Col 3 = ACCOUNT_CODE
    # Col 6 = EXPENSE_ELEMENT
    # Col 9 = TRAN_AMOUNT
    # Col 16 = Description
    df_orig = pd.read_excel(file_original, header=None, skiprows=8)
    df_orig.columns = [f"Col{i}" for i in range(len(df_orig.columns))]
    
    # Map to known columns
    df_orig = df_orig.rename(columns={
        'Col2': 'TRAN_GROUP_KEY',
        'Col3': 'ACCOUNT_CODE', 
        'Col6': 'EXPENSE_ELEMENT',
        'Col9': 'TRAN_AMOUNT',
        'Col16': 'DESCRIPTION'
    })
    
    # Replicated PLQ001 (has header)
    df_repl = pd.read_excel(file_replicated)
    
    print(f"Original PLQ001: {len(df_orig)} rows")
    print(f"Replicated PLQ001: {len(df_repl)} rows")
    
    # Ensure TRAN_AMOUNT is numeric
    df_orig['TRAN_AMOUNT'] = pd.to_numeric(df_orig['TRAN_AMOUNT'], errors='coerce')
    df_repl['TRAN_AMOUNT'] = pd.to_numeric(df_repl['TRAN_AMOUNT'], errors='coerce')
    
    # Summary by Expense Element
    print("\n--- Summary by EXPENSE_ELEMENT ---")
    
    orig_by_ee = df_orig.groupby('EXPENSE_ELEMENT')['TRAN_AMOUNT'].agg(['sum', 'count']).rename(columns={'sum': 'Orig_Sum', 'count': 'Orig_Count'})
    repl_by_ee = df_repl.groupby('EXPENSE_ELEMENT')['TRAN_AMOUNT'].agg(['sum', 'count']).rename(columns={'sum': 'Repl_Sum', 'count': 'Repl_Count'})
    
    comparison = orig_by_ee.join(repl_by_ee, how='outer').fillna(0)
    comparison['Diff_Sum'] = comparison['Repl_Sum'] - comparison['Orig_Sum']
    comparison['Diff_Count'] = comparison['Repl_Count'] - comparison['Orig_Count']
    
    print(comparison.to_string())
    
    # Find unique keys
    # Use TRAN_GROUP_KEY as primary identifier
    df_orig['KEY'] = df_orig['TRAN_GROUP_KEY'].astype(str).str.strip()
    df_repl['KEY'] = df_repl['TRAN_GROUP_KEY'].astype(str).str.strip()
    
    orig_keys = set(df_orig['KEY'].unique())
    repl_keys = set(df_repl['KEY'].unique())
    
    only_in_orig = orig_keys - repl_keys
    only_in_repl = repl_keys - orig_keys
    common_keys = orig_keys & repl_keys
    
    print(f"\n--- Key Analysis (TRAN_GROUP_KEY) ---")
    print(f"Keys only in Original: {len(only_in_orig)}")
    print(f"Keys only in Replicated: {len(only_in_repl)}")
    print(f"Common Keys: {len(common_keys)}")
    
    # Analyze records only in Original
    if only_in_orig:
        df_only_orig = df_orig[df_orig['KEY'].isin(only_in_orig)]
        total_only_orig = df_only_orig['TRAN_AMOUNT'].sum()
        print(f"\nTotal Amount of records ONLY in Original: Rp {total_only_orig:,.2f}")
        print("Sample (Top 5):")
        print(df_only_orig[['KEY', 'ACCOUNT_CODE', 'EXPENSE_ELEMENT', 'TRAN_AMOUNT', 'DESCRIPTION']].head().to_string(index=False))
    
    # Analyze records only in Replicated
    if only_in_repl:
        df_only_repl = df_repl[df_repl['KEY'].isin(only_in_repl)]
        total_only_repl = df_only_repl['TRAN_AMOUNT'].sum()
        print(f"\nTotal Amount of records ONLY in Replicated: Rp {total_only_repl:,.2f}")
        print("Sample (Top 5):")
        print(df_only_repl[['KEY', 'ACCOUNT_CODE', 'EXPENSE_ELEMENT', 'TRAN_AMOUNT', 'DESCRIPTION_FINAL']].head().to_string(index=False))
    
    # Save detailed comparison
    comparison.to_excel("comparison_by_expense_element.xlsx")
    print("\nSaved comparison to comparison_by_expense_element.xlsx")

if __name__ == "__main__":
    compare_details()
