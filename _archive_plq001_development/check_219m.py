
import pandas as pd

def check_219m():
    df = pd.read_excel("PLQ001_REPLICATED_PERFECT_FINAL.xlsx")
    df['AMT'] = pd.to_numeric(df['TRAN_AMOUNT'], errors='coerce')
    
    matches = df[df['AMT'].abs() > 219000000] # Just check around this value or equal
    matches = df[(df['AMT'] > 219800000) & (df['AMT'] < 219900000) | (df['AMT'] > -219900000) & (df['AMT'] < -219800000)]
    
    print("Transactions matching +/- 219,838,791:")
    print(matches[['PROJECT_NO', 'TRAN_AMOUNT', 'DESCRIPTION_FINAL']].to_string())

if __name__ == "__main__":
    check_219m()
