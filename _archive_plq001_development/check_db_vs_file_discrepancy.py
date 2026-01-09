
import pandas as pd
from app import create_app
from app.models import BudgetLine

def analyze_discrepancy():
    print("Analyzing Dashboard vs PLQ001 Discrepancy...")
    
    # 1. Load PLQ001 Final
    file_path = "PLQ001_REPLICATED_PERFECT_FINAL.xlsx"
    df = pd.read_excel(file_path)
    df['TRAN_AMOUNT'] = pd.to_numeric(df['TRAN_AMOUNT'], errors='coerce').fillna(0)
    
    # Calculate File Total
    file_total = df['TRAN_AMOUNT'].sum()
    print(f"PLQ001 File Total: Rp {file_total:,.2f}")
    
    app = create_app()
    with app.app_context():
        # 2. Get DB Total
        all_lines = BudgetLine.query.filter_by(tahun=2025).all()
        db_total = sum([bl.ellipse_rp or 0 for bl in all_lines])
        print(f"Dashboard DB Total: Rp {db_total:,.2f}")
        
        diff = db_total - file_total
        print(f"Difference:       Rp {diff:,.2f}")
        
        # 3. Find candidates for the difference
        # Looking for items in DB that have value but maybe not in file, or mismatched
        
        # Re-construct our mapping logic to see what SHOULD be
        # We mapped everything to PL252... or PL...
        
        # Let's verify each DB item against the file accumulation
        # First, aggregate file by Target PRK logic again
        def get_target_db_prk(row):
            proj = str(row['PROJECT_NO']).strip()
            amt = row['TRAN_AMOUNT']
            if proj in ['-', 'nan', 'None', '']:
                if abs(amt - (-136530000)) < 1.0: return "PL252I0204"
                return "PL252-UNCATEGORIZED"
            if proj.startswith('242') or proj.startswith('232'):
                suffix = proj[3:]
                return "PL252" + suffix
            if proj.startswith('252'):
                return "PL" + proj
            return "PL" + proj

        df['TARGET_PRK'] = df.apply(get_target_db_prk, axis=1)
        grouped = df.groupby('TARGET_PRK')['TRAN_AMOUNT'].sum().to_dict()
        
        print("\nChecking line-by-line:")
        mismatches = []
        for bl in all_lines:
            db_val = bl.ellipse_rp or 0
            if db_val == 0: continue
            
            target_val = grouped.get(bl.no_prk, 0)
            
            if abs(db_val - target_val) > 1.0:
                print(f"  MISMATCH: {bl.no_prk} | DB: {db_val:,.0f} | File: {target_val:,.0f} | Diff: {db_val - target_val:,.0f}")
                mismatches.append((bl, db_val - target_val))
            # else:
            #     print(f"  MATCH: {bl.no_prk}")
                
        # Also check if any file items missing in DB
        print("\nChecking for File items missing in DB:")
        db_prks = set([bl.no_prk for bl in all_lines])
        for prk, val in grouped.items():
            if prk not in db_prks and abs(val) > 1.0:
                print(f"  MISSING IN DB: {prk} | Amt: {val:,.0f}")

if __name__ == "__main__":
    analyze_discrepancy()
