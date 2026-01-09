
# Check why we got 2081 rows instead of 2079
import pandas as pd

file_orig = "/Users/rafindraramadhan/Documents/MonitoringAnggaran/export/PLQ001_Rincian Jurnal dan Transaksi 2025 SD DESEMBER_benar.xlsx"
file_repl = "replicated_plq001_absolute_final.xlsx"

df_orig = pd.read_excel(file_orig, header=None, skiprows=8)
df_orig['TGK'] = df_orig[2].astype(str).str.strip()
df_orig['ACCT'] = df_orig[3].astype(str).str.strip()
df_orig['AMT'] = pd.to_numeric(df_orig[9], errors='coerce')

df_repl = pd.read_excel(file_repl)
df_repl['TGK'] = df_repl['TRAN_GROUP_KEY'].astype(str).str.strip()
df_repl['ACCT'] = df_repl['ACCOUNT_CODE'].astype(str).str.strip()
df_repl['AMT'] = pd.to_numeric(df_repl['TRAN_AMOUNT'], errors='coerce')

# Check for duplicates in each
orig_dups = df_orig.groupby(['TGK', 'ACCT', 'AMT']).size()
orig_dups = orig_dups[orig_dups > 1]

repl_dups = df_repl.groupby(['TGK', 'ACCT', 'AMT']).size()
repl_dups = repl_dups[repl_dups > 1]

print("Checking for duplicate TGK+ACCT+AMT combinations...")
print(f"\nOriginal PLQ001:")
print(f"  Total rows: {len(df_orig)}")
print(f"  Unique TGK+ACCT+AMT: {len(df_orig.groupby(['TGK', 'ACCT', 'AMT']))}")
print(f"  Duplicate combos: {len(orig_dups)}")

print(f"\nReplicated:")
print(f"  Total rows: {len(df_repl)}")
print(f"  Unique TGK+ACCT+AMT: {len(df_repl.groupby(['TGK', 'ACCT', 'AMT']))}")
print(f"  Duplicate combos: {len(repl_dups)}")

if len(orig_dups) > 0:
    print(f"\nDuplicate combos in ORIGINAL:")
    for combo, count in orig_dups.items():
        print(f"  {combo[0][:40]}... | {combo[1]} | {combo[2]:,.2f} : {count} times")

if len(repl_dups) > 0:
    print(f"\nDuplicate combos in REPLICATED:")
    for combo, count in repl_dups.items():
        print(f"  {combo[0][:40]}... | {combo[1]} | {combo[2]:,.2f} : {count} times")
