
import pandas as pd
from app import create_app
from app.models import BudgetLine

def verify_merge_composition():
    print("Verifying Merge Composition and DB Values...")
    
    # 1. Load PLQ Data
    df = pd.read_excel("PLQ001_REPLICATED_PERFECT_FINAL.xlsx")
    df['TRAN_AMOUNT'] = pd.to_numeric(df['TRAN_AMOUNT'], errors='coerce').fillna(0)
    
    # 2. Define Mapping Logic (Same as before)
    def get_target_db_prk(row):
        proj = str(row['PROJECT_NO']).strip()
        amt = row['TRAN_AMOUNT']
        
        if proj in ['-', 'nan', 'None', '']:
            if abs(amt - (-136530000)) < 1.0: return "PL252I0204"
            if abs(amt - (-219838791)) < 1.0: return "PL252P0108" # Explicit fix for 219M
            return "PL252-UNCATEGORIZED"
            
        if proj.startswith('242') or proj.startswith('232'):
            suffix = proj[3:]
            return "PL252" + suffix
        if proj.startswith('252'):
            return "PL" + proj
        return "PL" + proj

    df['TARGET_PRK'] = df.apply(get_target_db_prk, axis=1)
    
    # 3. Analyze Composition
    # Group by Target, but keep list of sources
    report = {}
    
    grouped = df.groupby('TARGET_PRK')
    
    for target, group in grouped:
        sources = group.groupby('PROJECT_NO')['TRAN_AMOUNT'].sum().to_dict()
        total = group['TRAN_AMOUNT'].sum()
        report[target] = {
            'sources': sources,
            'calculated_total': total
        }
        
    # 4. Compare with DB
    app = create_app()
    with app.app_context():
        db_lines = BudgetLine.query.filter_by(tahun=2025).all()
        db_map = {bl.no_prk: bl.ellipse_rp or 0 for bl in db_lines}
        
        print(f"\n{'='*100}")
        print(f"{'TARGET PRK':<20} | {'DB VALUE':<20} | {'CALC TOTAL':<20} | {'DIFF':<15} | {'COMPOSITION'}")
        print(f"{'='*100}")
        
        mismatches = []
        
        for target, data in report.items():
            calc_val = data['calculated_total']
            db_val = db_map.get(target, 0) # If not in DB, 0
            
            diff = db_val - calc_val
            
            # Format sources string
            comp_str = ", ".join([f"{k}: {v:,.0f}" for k, v in data['sources'].items()])
            
            # Highlight if merged (more than 1 source) or mismatch
            is_merged = len(data['sources']) > 1
            is_mismatch = abs(diff) > 1.0
            
            if is_mismatch or is_merged:
                status = "MISMATCH" if is_mismatch else "OK"
                print(f"{target:<20} | {db_val:,.0f} | {calc_val:,.0f} | {diff:,.0f} ({status}) | {comp_str}")
                
                if is_mismatch:
                    mismatches.append(target)
                    
        print(f"\n{'='*100}")
        if mismatches:
            print(f"FOUND {len(mismatches)} MISMATCHES!")
        else:
            print("ALL MERGED TOTALS MATCH DATABASE PERFECTLY.")

if __name__ == "__main__":
    verify_merge_composition()
