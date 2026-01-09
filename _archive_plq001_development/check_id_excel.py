
import pandas as pd

def check_id_in_excel():
    file_my = "filtered_transactions_uppl_2025.xlsx"
    target_id = "30891360000"
    
    print(f"Checking for ID {target_id} in {file_my}...")
    
    df = pd.read_excel(file_my)
    df['TRANSACTION_NO'] = df['TRANSACTION_NO'].astype(str).str.strip()
    
    if target_id in df['TRANSACTION_NO'].values:
        print("FOUND in Excel!")
        row = df[df['TRANSACTION_NO'] == target_id]
        print(row.to_string())
    else:
        print("NOT FOUND in Excel.")
        print("Sample IDs in Excel:")
        print(df['TRANSACTION_NO'].head().tolist())

if __name__ == "__main__":
    check_id_in_excel()
