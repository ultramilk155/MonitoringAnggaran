
import pandas as pd
import os

def inspect_keys():
    file_my = "filtered_transactions_uppl_2025.xlsx"
    file_plq = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
    
    print("--- Inspecting Keys ---")
    
    # 1. Load My Extraction
    if os.path.exists(file_my):
        df_my = pd.read_excel(file_my, nrows=5)
        print(f"\n[My Extraction] Sample:")
        print(df_my[['TRANSACTION_NO', 'ACCOUNT_CODE', 'TRAN_AMOUNT']].to_string())
    
    # 2. Load PLQ001
    if os.path.exists(file_plq):
        df_plq = pd.read_excel(file_plq, header=None, skiprows=8, nrows=5)
        print(f"\n[PLQ001] Sample (Cols 2, 3, 9):")
        # Col 2: Transaction ID?
        # Col 3: Account Code?
        # Col 9: Amount
        print(df_plq[[2, 3, 9]].to_string())

if __name__ == "__main__":
    inspect_keys()
