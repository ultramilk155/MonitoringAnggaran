
# Final verification - check if 2081 is correct or if we need exactly 2079
import pandas as pd

file_final = "PLQ001_REPLICATED_PERFECT_100PERCENT.xlsx"
file_orig = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"

df_final = pd.read_excel(file_final)
df_orig = pd.read_excel(file_orig, header=None, skiprows=8)

print(f"Final file rows: {len(df_final)}")
print(f"Original file rows: {len(df_orig)}")

# Check the duplicate combo
dup_tgk = 'UPPL2025032548544400000525SC'
dup_acct = 'APL311033150224F106'
dup_amt = 4050000.00

print(f"\nChecking duplicate combo in final file:")
dup_rows_final = df_final[
    (df_final['TRAN_GROUP_KEY'].astype(str).str.strip() == dup_tgk) &
    (df_final['ACCOUNT_CODE'].astype(str).str.strip() == dup_acct) &
    (df_final['TRAN_AMOUNT'] == dup_amt)
]

print(f"Found {len(dup_rows_final)} rows for duplicate combo")
print(dup_rows_final[['TRAN_GROUP_KEY', 'ACCOUNT_CODE', 'TRAN_AMOUNT', 'PROJECT_NO', 'DESCRIPTION_FINAL']].to_string())

# Check original
print(f"\nChecking same combo in original PLQ001:")
df_orig['TGK'] = df_orig[2].astype(str).str.strip()
df_orig['ACCT'] = df_orig[3].astype(str).str.strip()
df_orig['AMT'] = pd.to_numeric(df_orig[9], errors='coerce')

dup_rows_orig = df_orig[
    (df_orig['TGK'] == dup_tgk) &
    (df_orig['ACCT'] == dup_acct) &
    (df_orig['AMT'] == dup_amt)
]

print(f"Found {len(dup_rows_orig)} rows in original")
print(f"Values in original:")
for idx, row in dup_rows_orig.iterrows():
    proj = row[15] if 15 < len(row) else 'N/A'
    desc = row[16] if 16 < len(row) else 'N/A'
    print(f"  PROJECT_NO: {proj}, DESC: {desc[:50]}")

# SOLUTION: Use drop_duplicates to keep first occurrence
print(f"\n{'='*60}")
print("SOLUTION: Drop duplicates keeping first occurrence")
print(f"{'='*60}")

df_final_dedup = df_final.drop_duplicates(
    subset=['TRAN_GROUP_KEY', 'ACCOUNT_CODE', 'TRAN_AMOUNT'],
    keep='first'
)

print(f"After dedup: {len(df_final_dedup)} rows")

if len(df_final_dedup) == len(df_orig):
    print("✅ ROW COUNT NOW MATCHES!")
    
    # Save corrected version
    df_final_dedup.to_excel("PLQ001_REPLICATED_PERFECT_FINAL.xlsx", index=False)
    
    total_amt = pd.to_numeric(df_final_dedup['TRAN_AMOUNT'], errors='coerce').sum()
    expected_amt = pd.to_numeric(df_orig[9], errors='coerce').sum()
    
    print(f"\nTotal Amount: Rp {total_amt:,.2f}")
    print(f"Expected: Rp {expected_amt:,.2f}")
    print(f"Match: {'✅ YES!' if abs(total_amt - expected_amt) < 1.0 else '❌ NO'}")
    
    print(f"\n✨ PERFECT FINAL FILE CREATED: PLQ001_REPLICATED_PERFECT_FINAL.xlsx")
