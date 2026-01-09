
import pandas as pd

# Quick analysis - how many TGK+ACCT have duplicates and what are their amounts?
file_orig = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
df = pd.read_excel(file_orig, header=None, skiprows=8)
df['TGK'] = df[2].astype(str).str.strip()
df['ACCT'] = df[3].astype(str).str.strip()
df['AMT'] = pd.to_numeric(df[9], errors='coerce')

# Group and check
grouped = df.groupby(['TGK', 'ACCT']).agg({'AMT': ['count', 'first', 'sum']})
dups = grouped[grouped[('AMT', 'count')] > 1]

print(f"Total rows in PLQ001: {len(df)}")
print(f"Unique TGK+ACCT: {len(grouped)}")
print(f"Duplicate TGK+ACCT pairs: {len(dups)}")
print(f"\nSample duplicates:")
print(dups.head(10).to_string())

# Check if duplicates have same amount per row
print("\n=== Checking if duplicates have identical amounts ===")
for combo in list(dups.index)[:5]:
    subset = df[(df['TGK'] == combo[0]) & (df['ACCT'] == combo[1])]
    print(f"\n{combo[0][:40]}... | {combo[1]}")
    print(f"Amounts: {subset['AMT'].tolist()}")
    print(f"All same? {len(subset['AMT'].unique()) == 1}")
