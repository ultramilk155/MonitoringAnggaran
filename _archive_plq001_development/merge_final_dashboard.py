
import pandas as pd
from app import create_app
from app.extensions import db
from app.models import BudgetLine

def merge_dashboard_final():
    file_path = "PLQ001_REPLICATED_PERFECT_FINAL.xlsx"
    print(f"Reading {file_path}...")
    
    df = pd.read_excel(file_path)
    df['TRAN_AMOUNT'] = pd.to_numeric(df['TRAN_AMOUNT'], errors='coerce').fillna(0)
    
    # Mapping Logic
    def get_target_db_prk(row):
        proj = str(row['PROJECT_NO']).strip()
        amt = row['TRAN_AMOUNT']
        
        # Handle special cases first
        if proj in ['-', 'nan', 'None', '']:
            # Special logic for the -136M reversal
            if abs(amt - (-136530000)) < 1.0:
                return "PL252I0204" # Map to same as the positive 242I0204 -> 252I0204
            return "PL252-UNCATEGORIZED"
            
        # Normal Carry Over Mapping
        # 242xxxxx -> 252xxxxx
        if proj.startswith('242') or proj.startswith('232'):
            suffix = proj[3:]
            return "PL252" + suffix
            
        # Standard 2025 projects
        if proj.startswith('252'):
            return "PL" + proj
            
        # Fallback
        return "PL" + proj

    # Apply mapping
    print("Applying mapping logic...")
    df['TARGET_PRK'] = df.apply(get_target_db_prk, axis=1)
    
    # Group by Target PRK
    grouped = df.groupby('TARGET_PRK')['TRAN_AMOUNT'].sum().reset_index()
    
    print(f"Total Aggr Amount: Rp {grouped['TRAN_AMOUNT'].sum():,.2f}")
    
    # Update DB
    app = create_app()
    with app.app_context():
        # Code Inference Map (from existing)
        existing = BudgetLine.query.filter_by(tahun=2025).all()
        char_map = {}
        for bl in existing:
            if bl.no_prk.startswith('PL') and len(bl.no_prk) > 6:
                char_map[bl.no_prk[5]] = bl.kode
                
        # 1. Reset all 2025 ellipse amounts to 0 (to avoid double counting if re-run)
        # Actually safer to just overwrite with new sums
        # But we need to be careful not to delete manual data? 
        # Ellipse RP is auto-populated, so overwriting is fine.
        
        # Build map of existing objects
        bl_map = {bl.no_prk: bl for bl in existing}
        
        updated = 0
        created = 0
        
        for index, row in grouped.iterrows():
            prk = row['TARGET_PRK']
            amount = row['TRAN_AMOUNT']
            
            if prk in bl_map:
                bl_map[prk].ellipse_rp = amount
                updated += 1
            else:
                # Create New
                # Infer Code
                char_code = prk[5] if len(prk) > 6 else '?'
                kode_val = char_map.get(char_code, '99-LAINNYA')
                
                # Check if this PRK existed in carry-over list for Description
                # Try to find original description from first occurrence in df
                sample = df[df['TARGET_PRK'] == prk].iloc[0]
                desc = sample['DESCRIPTION_FINAL']
                if pd.isna(desc) or desc == '':
                   desc = f"Merged Project {prk}"
                   
                new_bl = BudgetLine(
                    kode=kode_val,
                    no_prk=prk,
                    deskripsi=desc,
                    tahun=2025,
                    ellipse_rp=amount
                )
                db.session.add(new_bl)
                created += 1
                # print(f"Created {prk}: Rp {amount:,.0f}")
                
        db.session.commit()
        
        # Final Verification
        final_total = sum([bl.ellipse_rp or 0 for bl in BudgetLine.query.filter_by(tahun=2025).all()])
        print(f"\n{'='*60}")
        print("FINAL MERGE RESULT")
        print(f"{'='*60}")
        print(f"Updated: {updated}")
        print(f"Created: {created}")
        print(f"DB Total:  Rp {final_total:,.2f}")
        print(f"PLQ Total: Rp {108436047458.10:,.2f}")
        print(f"Diff:      Rp {final_total - 108436047458.10:,.2f}")

if __name__ == "__main__":
    merge_dashboard_final()
