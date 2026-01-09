
import pandas as pd
from app import create_app
from app.extensions import db
from app.models import BudgetLine

def sync_dashboard_with_plq001():
    """
    Complete sync of PLQ001 to BudgetLine table for 2025.
    1. Update existing lines.
    2. Create missing lines (likely carry-over) with inferred codes.
    """
    file_path = "PLQ001_REPLICATED_PERFECT_FINAL.xlsx"
    print(f"Reading {file_path}...")
    
    df = pd.read_excel(file_path)
    df['TRAN_AMOUNT'] = pd.to_numeric(df['TRAN_AMOUNT'], errors='coerce').fillna(0)
    
    # Aggregate
    grouped = df.groupby(['PROJECT_NO']).agg({
        'TRAN_AMOUNT': 'sum',
        'DESCRIPTION_FINAL': 'first'
    }).reset_index()
    
    print(f"PLQ001 Total: Rp {grouped['TRAN_AMOUNT'].sum():,.2f}")
    
    app = create_app()
    with app.app_context():
        # Build mapping for 'Kode' inference
        # Get all budget lines to learn mapping (char at index 5 of NO_PRK -> KODE)
        # Format: PL252G... -> G is at index 5 IF starts with PL. 
        # But wait, missing projects are "PL232..." so yes.
        # Check existing mapping
        existing = BudgetLine.query.all()
        char_map = {}
        for bl in existing:
            if bl.no_prk and bl.no_prk.startswith('PL') and len(bl.no_prk) > 6:
                char_code = bl.no_prk[5] # 6th char
                if bl.kode:
                    char_map[char_code] = bl.kode
        
        print(f"Inferred Code Map: {char_map}")
        
        # Process each project
        created_count = 0
        updated_count = 0
        
        for index, row in grouped.iterrows():
            proj_no_raw = str(row['PROJECT_NO']).strip()
            # Handle potential blank/nan
            if not proj_no_raw or proj_no_raw.lower() == 'nan':
                 # Skip if no project number (should be caught by earlier fixes but safe check)
                 continue
                 
            amount = row['TRAN_AMOUNT']
            desc = row['DESCRIPTION_FINAL']
            
            # DB Key expected: "PL" + proj_no
            db_prk = "PL" + proj_no_raw
            
            # Find in DB
            bl = BudgetLine.query.filter_by(tahun=2025, no_prk=db_prk).first()
            
            if bl:
                # Update
                bl.ellipse_rp = amount
                updated_count += 1
            else:
                # Create New
                # Infer Kode
                char_target = db_prk[5] if len(db_prk) > 6 else '?'
                kode_val = char_map.get(char_target, '99-LAINNYA')
                
                new_bl = BudgetLine(
                    kode=kode_val,
                    no_prk=db_prk,
                    deskripsi=desc or f"Carry Over Project {db_prk}",
                    tahun=2025,
                    pagu_material=0,
                    pagu_jasa=0,
                    pagu_total=0,
                    ellipse_rp=amount,
                    usulan_rab_rp=0,
                    terkontrak_rp=0,
                    terbayar_rp=0
                )
                db.session.add(new_bl)
                created_count += 1
                desc_str = desc if desc else "No Description"
                print(f"Creating NEW BudgetLine: {db_prk} ({desc_str[:30]}...) -> Kode: {kode_val}, Amt: {amount:,.0f}")
        
        db.session.commit()
        
        # Verify
        all_2025 = BudgetLine.query.filter_by(tahun=2025).all()
        final_total = sum([item.ellipse_rp or 0 for item in all_2025])
        
        print(f"\n{'='*60}")
        print("SYNC RESULTS")
        print(f"{'='*60}")
        print(f"Updated: {updated_count}")
        print(f"Created: {created_count}")
        print(f"Total BudgetLines 2025: {len(all_2025)}")
        print(f"Final Dashboard Total: Rp {final_total:,.2f}")
        print(f"PLQ001 Total:        Rp {grouped['TRAN_AMOUNT'].sum():,.2f}")
        
        diff = final_total - grouped['TRAN_AMOUNT'].sum()
        print(f"Difference:          Rp {diff:,.2f}")
        
        if abs(diff) < 1.0:
            print("✅ SUCCESS! Dashboard will now explicitly match PLQ001.")
        else:
            print("❌ STILL MISMATCHED.")

if __name__ == "__main__":
    sync_dashboard_with_plq001()
