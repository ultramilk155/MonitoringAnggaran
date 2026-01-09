
# Quick check - what's in Col 15 of PLQ001 original?
import pandas as pd

file_orig = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
df = pd.read_excel(file_orig, header=None, skiprows=8, nrows=20)

print("Checking first 20 rows, columns 14-17:")
print("Col14 | Col15 | Col16 | Col17")
print("-" * 80)
for i, row in df.iterrows():
    c14 = str(row[14]) if 14 < len(row) else 'N/A'
    c15 = str(row[15]) if 15 < len(row) else 'N/A'
    c16 = str(row[16]) if 16 < len(row) else 'N/A'
    c17 = str(row[17]) if 17 < len(row) else 'N/A'
    print(f"{c14[:15]:15} | {c15[:15]:15} | {c16[:40]:40} | {c17[:15]:15}")

# Also check replicated file
print("\n" + "="*80)
print("Checking replicated file - PROJECT_NO column:")
print("="*80)

df_repl = pd.read_excel("replicated_plq001_absolute_final.xlsx", nrows=20)
if 'PROJECT_NO' in df_repl.columns:
    print("PROJECT_NO values (first 20):")
    for i, val in enumerate(df_repl['PROJECT_NO'].head(20)):
        print(f"Row {i}: {val}")
else:
    print("PROJECT_NO column not found!")
    print(f"Available columns: {df_repl.columns.tolist()}")
