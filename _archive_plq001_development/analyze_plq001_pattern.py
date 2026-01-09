
import pandas as pd
import os

def analyze_pattern():
    file_plq = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
    
    print("Loading PLQ001 for pattern analysis...")
    
    # Load without header
    df = pd.read_excel(file_plq, header=None, skiprows=8)
    
    # Based on earlier inspection, map columns
    # Col 0 = DSTRCT_CODE
    # Col 1 = FULL_PERIOD (YYYYMM)
    # Col 2 = TRAN_GROUP_KEY
    # Col 3 = ACCOUNT_CODE
    # Col 6 = EXPENSE_ELEMENT
    # Col 9 = TRAN_AMOUNT
    # Col 11 = CREATION_DATE or TRANSACTION_DATE?
    # Col 12 = Another date?
    
    df.columns = [f"Col{i}" for i in range(len(df.columns))]
    
    print(f"Total Rows: {len(df)}")
    
    # 1. Analyze FULL_PERIOD (Col 1)
    print("\n=== 1. FULL_PERIOD (YYYYMM) Distribution ===")
    period_dist = df['Col1'].value_counts().sort_index()
    print(period_dist)
    
    # 2. Analyze Date columns (Col 11, Col 12)
    print("\n=== 2. Date Columns Analysis ===")
    print("Sample of Col 11 and Col 12:")
    print(df[['Col11', 'Col12']].head(10).to_string())
    
    # Check min/max of date columns
    df['Col11_str'] = df['Col11'].astype(str)
    df['Col12_str'] = df['Col12'].astype(str)
    
    print(f"\nCol 11 (Date?) - Min: {df['Col11_str'].min()}, Max: {df['Col11_str'].max()}")
    print(f"Col 12 (Date?) - Min: {df['Col12_str'].min()}, Max: {df['Col12_str'].max()}")
    
    # 3. Analyze ACCOUNT_CODE patterns (Col 3)
    print("\n=== 3. ACCOUNT_CODE Analysis ===")
    df['ACCT'] = df['Col3'].astype(str).str.strip()
    
    # Segment 1 (Digit 1)
    df['SEG1'] = df['ACCT'].str[0:1]
    print("Segment 1 Distribution:")
    print(df['SEG1'].value_counts())
    
    # Segment 2 (Digit 2-3)
    df['SEG2'] = df['ACCT'].str[1:3]
    print("\nSegment 2 (Digits 2-3) Distribution:")
    print(df['SEG2'].value_counts())
    
    # Check if all have 'PL' in position 2-3
    has_pl = (df['SEG2'] == 'PL').sum()
    print(f"\nRows with 'PL' in Segment 2: {has_pl} / {len(df)}")
    
    # Expense Element (Digit 16-19)
    df['EE'] = df['ACCT'].str[15:19]
    print("\nExpense Element (Digits 16-19) Distribution:")
    print(df['EE'].value_counts())
    
    # 4. Transaction Type Analysis (if available)
    # From earlier, Col 8 might be transaction type description
    print("\n=== 4. Transaction Type (Col 8) Analysis ===")
    print(df['Col8'].value_counts())
    
    # 5. Analyze TRAN_GROUP_KEY pattern (Col 2)
    print("\n=== 5. TRAN_GROUP_KEY Pattern ===")
    df['TGK'] = df['Col2'].astype(str).str.strip()
    # Extract year from TGK (Format: UPPL + YYYYMMDD + ...)
    df['TGK_Year'] = df['TGK'].str[4:8]
    print("Year in TRAN_GROUP_KEY:")
    print(df['TGK_Year'].value_counts())
    
    # 6. Check for any pattern in first/last characters of ACCOUNT_CODE
    print("\n=== 6. ACCOUNT_CODE First/Last Chars ===")
    print("First 3 chars:")
    print(df['ACCT'].str[:3].value_counts().head(10))
    print("\nLast 4 chars (should be EE):")
    print(df['ACCT'].str[-4:].value_counts())
    
    # 7. Summary of filters discovered
    print("\n" + "="*50)
    print("=== DISCOVERED FILTERS ===")
    print("="*50)
    print(f"1. FULL_PERIOD Range: {df['Col1'].min()} to {df['Col1'].max()}")
    print(f"2. Segment 2 (PL check): {'YES - All have PL' if has_pl == len(df) else f'MIXED - {has_pl}/{len(df)}'}")
    print(f"3. Expense Elements: {sorted(df['EE'].unique().tolist())}")
    print(f"4. Transaction Types: {df['Col8'].unique().tolist()}")
    print(f"5. Date Range (Col11): {df['Col11_str'].min()} to {df['Col11_str'].max()}")
    print(f"6. Date Range (Col12): {df['Col12_str'].min()} to {df['Col12_str'].max()}")

if __name__ == "__main__":
    analyze_pattern()
