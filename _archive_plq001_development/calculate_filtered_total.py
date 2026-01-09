
import pandas as pd
import os

def calculate_total():
    file_path = "filtered_transactions_uppl_2025.xlsx"
    
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path)
            
            # Ensure TRAN_AMOUNT is numeric
            # The column name in the file should be TRAN_AMOUNT or similar based on the query alias
            # The query script used 'TRAN_AMOUNT' directly.
            
            if 'TRAN_AMOUNT' in df.columns:
                total_amount = df['TRAN_AMOUNT'].sum()
                
                print(f"Total Amount: {total_amount:,.2f}")
                
                # Breakdown by Expense Element if available
                if 'EENUM' in df.columns: # Substr(16,4) renamed to EENUM in query? 
                    # Checking query... "substr(a.ACCOUNT_CODE,16,4) EENUM" - YES.
                    print("\nBreakdown by Expense Element (EENUM):")
                    breakdown = df.groupby('EENUM')['TRAN_AMOUNT'].sum().sort_values(ascending=False)
                    print(breakdown.map('{:,.2f}'.format))
                    
            else:
                print("Column TRAN_AMOUNT not found.")
                print(df.columns)
                
        except Exception as e:
            print(f"Error reading Excel: {e}")
    else:
        print(f"File {file_path} not found.")

if __name__ == "__main__":
    calculate_total()
