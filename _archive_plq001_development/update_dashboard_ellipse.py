
import pandas as pd
from app import create_app
from app.extensions import db
from app.models import BudgetLine

def update_dashboard_ellipse():
    """
    Update BudgetLine.ellipse_rp with aggregated values from PLQ001_REPLICATED_PERFECT_FINAL.xlsx
    Mapping: BudgetLine.no_prk = "PL" + PLQ001.PROJECT_NO
    """
    file_path = "PLQ001_REPLICATED_PERFECT_FINAL.xlsx"
    print(f"Reading {file_path}...")
    
    df = pd.read_excel(file_path)
    
    # Aggregate by PROJECT_NO
    # Ensure TRAN_AMOUNT is numeric
    df['TRAN_AMOUNT'] = pd.to_numeric(df['TRAN_AMOUNT'], errors='coerce').fillna(0)
    
    # Group
    grouped = df.groupby('PROJECT_NO')['TRAN_AMOUNT'].sum().reset_index()
    
    print(f"Found {len(grouped)} unique PROJECT_NOs in PLQ001")
    print(f"Total Amount in File: Rp {df['TRAN_AMOUNT'].sum():,.2f}")
    
    app = create_app()
    with app.app_context():
        # Get all 2025 budget lines
        budget_lines = BudgetLine.query.filter_by(tahun=2025).all()
        print(f"Found {len(budget_lines)} BudgetLines for 2025 in DB")
        
        updated_count = 0
        total_db_ellipse_before = sum([bl.ellipse_rp or 0 for bl in budget_lines])
        
        # Create a map for faster lookup: "252..." -> BudgetLine object
        # Note: DB has "PL252...", so we strip "PL" to match PLQ001 "252..."
        # OR add "PL" to PLQ001 project no.
        # Let's verify DB format again. DB has "PL252G0102". PLQ001 has "252G0102".
        # So key should be bl.no_prk[2:] if it starts with PL? 
        # Or just match using "PL" + project_no.
        
        bl_map = {}
        for bl in budget_lines:
            # Normalize key
            key = bl.no_prk.strip()
            bl_map[key] = bl
            
        # Update
        for index, row in grouped.iterrows():
            proj_no =  str(row['PROJECT_NO']).strip()
            amount = row['TRAN_AMOUNT']
            
            # Construct DB key
            db_key = "PL" + proj_no
            
            if db_key in bl_map:
                bl = bl_map[db_key]
                bl.ellipse_rp = amount
                updated_count += 1
                # print(f"Updated {db_key}: Rp {amount:,.2f}")
            else:
                print(f"Warning: Project {proj_no} (DB Key: {db_key}) not found in BudgetLine table!")
        
        db.session.commit()
        
        # Verify total after update
        # Re-fetch or rely on objects
        total_db_ellipse_after = sum([bl.ellipse_rp or 0 for bl in budget_lines])
        
        print(f"\n{'='*60}")
        print(f"UPDATE SUMMARY")
        print(f"{'='*60}")
        print(f"BudgetLines Updated: {updated_count}/{len(budget_lines)}")
        print(f"Total Ellipse BEFORE: Rp {total_db_ellipse_before:,.2f}")
        print(f"Total Ellipse AFTER:  Rp {total_db_ellipse_after:,.2f}")
        print(f"Target Total:         Rp {df['TRAN_AMOUNT'].sum():,.2f}")
        
        diff = total_db_ellipse_after - df['TRAN_AMOUNT'].sum()
        print(f"Difference:           Rp {diff:,.2f}")
        
        if abs(diff) < 1.0:
            print("✅ DASHBOARD UPDATE SUCCESSFUL! Totals match.")
        else:
            print("❌ TOTALS DO NOT MATCH. Check for missing projects or mapping issues.")

if __name__ == "__main__":
    update_dashboard_ellipse()
