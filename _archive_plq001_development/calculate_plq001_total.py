
import pandas as pd
import os

def calculate_plq_total():
    file_path = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
    target_ee = ['E201', 'E202', 'E203', 'E204', 'F101', 'F104', 'F106', 'F107']
    
    if os.path.exists(file_path):
        try:
            # Read file without header, skipping metadata rows (first 8 rows seem to be metadata/empty)
            # Row 9 (index 8) was the first data row seen in previous inspection
            print("Reading Excel...")
            df = pd.read_excel(file_path, header=None, skiprows=8)
            
            # Based on previous inspection:
            # Col 6 = Expense Element (e.g., F104)
            # Col 9 = Amount (e.g., 198366149)
            
            # Filter
            # Convert to string and strip just in case
            df[6] = df[6].astype(str).str.strip()
            
            print(f"Total Rows read: {len(df)}")
            
            filtered_df = df[df[6].isin(target_ee)]
            
            print(f"Filtered Rows matches: {len(filtered_df)}")
            
            # Sum Amount (Col 9)
            # Ensure numeric
            total = pd.to_numeric(filtered_df[9], errors='coerce').sum()
            
            print(f"\nTotal Amount (PLQ001) for {target_ee}:")
            print(f"Rp {total:,.2f}")
            
            print("\nBreakdown:")
            breakdown = filtered_df.groupby(6)[9].sum().sort_values(ascending=False)
            print(breakdown.map('{:,.2f}'.format))
            
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"File not found: {file_path}")

if __name__ == "__main__":
    calculate_plq_total()
