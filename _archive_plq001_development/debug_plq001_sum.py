
import pandas as pd
import numpy as np

def debug_excel_structure():
    file_path = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
    
    print(f"Reading {file_path}...")
    
    # Read raw without assuming header info
    df_raw = pd.read_excel(file_path, header=None)
    
    print(f"Total raw rows: {len(df_raw)}")
    print(f"Total raw columns: {len(df_raw.columns)}")
    
    # Try to calculate sum on Column J (Index 9)
    # The screenshot shows column J is TRAN_AMOUNT
    
    # Convert col 9 to numeric, errors='coerce' to turn text headers to NaN
    col_j_numeric = pd.to_numeric(df_raw[9], errors='coerce')
    
    total_sum = col_j_numeric.sum()
    count_numeric = col_j_numeric.count()
    
    print(f"\nAnalysis of Column J (Index 9):")
    print(f"Total Sum of ALL numeric cells: Rp {total_sum:,.2f}")
    print(f"Count of numeric cells: {count_numeric}")
    
    target_sum = 108436047458.10
    diff = total_sum - target_sum
    
    print(f"\nTarget Sum (from Screenshot): Rp {target_sum:,.2f}")
    print(f"Difference: Rp {diff:,.2f}")
    
    if abs(diff) < 1.0:
        print("✅ MATCH FOUND using raw read!")
    else:
        print("❌ Still mismatch.")
        
    print(f"\nInspect first 15 rows of Column J:")
    print(df_raw[[0, 9]].head(15).to_string())
    
    print(f"\nInspect rows causing the difference (if any skipped previously):")
    # My previous read skipped 8 rows. Let's look at those sum
    header_area = col_j_numeric.iloc[:9]
    print(f"Sum of first 9 rows: {header_area.sum()}")
    
    # Check if there are sums at the bottom?
    print(f"\nInspect last 10 rows of Column J:")
    print(df_raw[[0, 9]].tail(10).to_string())

if __name__ == "__main__":
    debug_excel_structure()
