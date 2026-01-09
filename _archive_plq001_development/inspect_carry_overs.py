
import pandas as pd

def inspect_pl_dash():
    file_path = "PLQ001_REPLICATED_PERFECT_FINAL.xlsx"
    df = pd.read_excel(file_path)
    
    # Check for rows where PROJECT_NO might be resulting in "PL-"
    # i.e., empty strings, NaNs, or just "-"
    
    print("Inspecting potential 'PL-' sources:")
    # Filter where PROJECT_NO is missing or looks like it would result in empty suffix
    # The sync script did: db_prk = "PL" + str(row['PROJECT_NO']).strip()
    # So if project_no is an empty string, we get "PL". 
    # Or if project_no is "-", we get "PL-".
    
    suspects = df[df['PROJECT_NO'].astype(str).str.strip().isin(['', '-', 'nan', 'None'])]
    
    if not suspects.empty:
        print(f"Found {len(suspects)} rows:")
        print(suspects[['TRAN_GROUP_KEY', 'ACCOUNT_CODE', 'TRAN_AMOUNT', 'PROJECT_NO', 'DESCRIPTION_FINAL']].to_string())
    else:
        print("No obvious blank/dash PROJECT_NO found.")
        
    # Also check the specific carry overs
    print("\nVerifying mapping logic for carry-overs:")
    carry_overs = [
        "232M0103", "232P0102", "242G0101", "242G0102", "242I0204",
        "242J0102", "242L0101", "242M0101", "242P0102", "242P0201",
        "242P0301", "242P0401"
    ]
    
    columns = ['PROJECT_NO', 'TRAN_AMOUNT']
    matched = df[df['PROJECT_NO'].isin(carry_overs)]
    print(f"Found {len(matched)} carry-over transactions.")
    if not matched.empty:
         print(matched.groupby('PROJECT_NO')['TRAN_AMOUNT'].sum())

if __name__ == "__main__":
    inspect_pl_dash()
