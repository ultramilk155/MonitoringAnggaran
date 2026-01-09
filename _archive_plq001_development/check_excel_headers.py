
import pandas as pd
import os

def check_headers():
    file_path = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
    
    if os.path.exists(file_path):
        print(f"Reading headers from: {os.path.basename(file_path)}")
        try:
            # Read first 15 rows raw
            df = pd.read_excel(file_path, header=None, nrows=15)
            print("--- Scanning First 15 Rows for Headers ---")
            for idx, row in df.iterrows():
                # Filter out NaNs to see if any text exists
                values = [str(x) for x in row.values if pd.notna(x) and str(x).strip() != '']
                print(f"Row {idx}: {values}")
                
        except Exception as e:
            print(f"Error reading Excel: {e}")
    else:
        print(f"File not found: {file_path}")

if __name__ == "__main__":
    check_headers()
