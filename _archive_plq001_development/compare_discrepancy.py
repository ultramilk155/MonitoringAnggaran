
import pandas as pd
import os

def compare_discrepancy():
    file_my = "filtered_transactions_uppl_2025.xlsx"
    file_plq = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
    target_ee = ['E201', 'E202', 'E203', 'E204', 'F101', 'F104', 'F106', 'F107']
    
    # 1. Load My Extraction
    print("Loading My Extraction...")
    df_my = pd.read_excel(file_my)
    # Ensure TRANSACTION_NO is string
    df_my['TRANSACTION_NO'] = df_my['TRANSACTION_NO'].astype(str).str.strip()
    my_ids = set(df_my['TRANSACTION_NO'].unique())
    print(f"My Extraction Transactions: {len(my_ids)}")
    
    # 2. Load PLQ001
    print("Loading PLQ001...")
    # Skip metadata rows
    df_plq = pd.read_excel(file_plq, header=None, skiprows=8) 
    
    # Filter by user specified EE (Col 6)
    df_plq[6] = df_plq[6].astype(str).str.strip()
    df_plq = df_plq[df_plq[6].isin(target_ee)].copy()
    
    # Extract Transaction ID from Col 2
    # Format: UPPL + YYYYMMDD (8) + ID (11) + ...
    # Start at index 4+8=12, take 11 chars
    def extract_id(val):
        s = str(val).strip()
        if len(s) > 20: 
            return s[12:23] # Adjust simpler logic if needed
        return s
        
    df_plq['PARSED_ID'] = df_plq[2].apply(extract_id)
    plq_ids = set(df_plq['PARSED_ID'].unique())
    print(f"PLQ Transactions (Filtered): {len(plq_ids)}")
    
    # 3. Compare
    missing_in_my = plq_ids - my_ids
    print(f"Transactions in PLQ but Missing in My Extraction: {len(missing_in_my)}")
    
    # 4. Analyze Discrepancy
    if missing_in_my:
        missing_df = df_plq[df_plq['PARSED_ID'].isin(missing_in_my)].copy()
        
        # Col 9 is Amount
        missing_df[9] = pd.to_numeric(missing_df[9], errors='coerce')
        total_missing_val = missing_df[9].sum()
        
        print(f"\nTotal Value of Missing Transactions: Rp {total_missing_val:,.2f}")
        
        # Breakdown by Description (Col 16) - "Pekerjaan apa saja"
        print("\n--- Missing Jobs Breakdown (Top 20) ---")
        # Rename col 16 for clarity
        missing_df.rename(columns={16: 'Job_Description', 9: 'Amount'}, inplace=True)
        
        grouped = missing_df.groupby('Job_Description')['Amount'].sum().sort_values(ascending=False).head(20)
        print(grouped.map('{:,.2f}'.format))
        
        # Save detailed mismatch report
        missing_df.to_excel("discrepancy_details_plq_vs_my.xlsx", index=False)
        print("\nSaved detailed discrepancy report to discrepancy_details_plq_vs_my.xlsx")

if __name__ == "__main__":
    compare_discrepancy()
