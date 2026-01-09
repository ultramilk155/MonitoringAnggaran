
# Check account code pattern for the blank PROJECT_NO cases
import pandas as pd

mismatches = pd.read_excel("project_no_mismatches.xlsx")

print("Analyzing ACCOUNT_CODE patterns for blank PROJECT_NO cases...")
print("\nFirst 20 cases:")
print("ACCOUNT_CODE | Expected PROJECT_NO")
print("-" * 60)

for idx, row in mismatches.head(20).iterrows():
    acct = row['ACCT']
    proj = row['PROJECT_NO_ORIG']
    
    # Try to find pattern
    # Account format: APL + Segments
    # APL 1 9 26 40 11 34 22 E204
    # Let me check different segments
    
    print(f"{acct:25} | {proj}")
    
    # Check if project number appears in account code
    if proj in acct:
        print(f"  ^^^ PROJECT {proj} appears directly in account!")

# Check segment structure
print("\n" + "="*60)
print("Analyzing account code segments:")
print("="*60)

sample_acct = mismatches.iloc[0]['ACCT']
sample_proj = mismatches.iloc[0]['PROJECT_NO_ORIG']

print(f"Sample ACCOUNT: {sample_acct}")
print(f"Expected PROJECT: {sample_proj}")
print(f"\nSegment breakdown:")
print(f"Pos 0-2  (Prefix):  {sample_acct[0:3]}")
print(f"Pos 3-4  (Seg1):    {sample_acct[3:5]}")
print(f"Pos 5-8  (Seg2):    {sample_acct[5:9]}")
print(f"Pos 9-10 (Seg3):    {sample_acct[9:11]}")
print(f"Pos 11-14(Seg4):    {sample_acct[11:15]}")
print(f"Pos 15-18(EE):      {sample_acct[15:19]}")

# Look for 252M or similar in PROJECT_NO '252M0102'
# Maybe it's constructed from multiple segments?
print(f"\nLooking for '252' in account: {sample_acct}")
print(f"Looking for 'M' in account: {sample_acct}")

# Check all unique PROJECT_NO values
unique_projs = mismatches['PROJECT_NO_ORIG'].unique()
print(f"\n\nUnique PROJECT_NO values in mismatches ({len(unique_projs)}):")
for p in sorted(unique_projs)[:20]:
    count = len(mismatches[mismatches['PROJECT_NO_ORIG'] == p])
    print(f"  {p}: {count} occurrences")
