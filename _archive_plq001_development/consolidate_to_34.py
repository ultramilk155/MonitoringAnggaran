
from app import create_app
from app.extensions import db
from app.models import BudgetLine

def consolidate_to_34():
    app = create_app()
    with app.app_context():
        # Mapping Logic defined in planning
        # Source PRK -> Target PRK
        mapping_rules = {
            "PL252M0101": "PL252M0102", # Maint -> Maint
            "PL252P0201": "PL252P0107", # Prasarana -> Gedung
            "PL252P0301": "PL252P0107", # Sarana -> Gedung
            "PL252P0401": "PL252P0107", # Building Mgmt -> Gedung
            "PL252-UNCATEGORIZED": "PL252P0108" # Misc -> Business Support
        }
        
        lines = BudgetLine.query.filter_by(tahun=2025).all()
        bl_map = {bl.no_prk: bl for bl in lines}
        
        updates = []
        deletes = []
        
        print("Executing Consolidation...")
        for source, target in mapping_rules.items():
            if source in bl_map and target in bl_map:
                s_obj = bl_map[source]
                t_obj = bl_map[target]
                
                amount = s_obj.ellipse_rp or 0
                
                print(f"  Moving {source} ({amount:,.0f}) -> {target}")
                
                # Add to target
                t_obj.ellipse_rp = (t_obj.ellipse_rp or 0) + amount
                
                # Mark source for delete
                deletes.append(s_obj)
            elif source in bl_map:
                print(f"  WARNING: Source {source} exists but Target {target} NOT FOUND. Skipping.")
                
        # Commit changes
        print(f"Deleting {len(deletes)} orphan rows...")
        for d in deletes:
            db.session.delete(d)
            
        db.session.commit()
        
        # Verify final state
        remaining = BudgetLine.query.filter_by(tahun=2025).count()
        total_val = sum([bl.ellipse_rp or 0 for bl in BudgetLine.query.filter_by(tahun=2025).all()])
        
        print(f"\nFinal State:")
        print(f"  Rows: {remaining}")
        print(f"  Total: Rp {total_val:,.2f}")

if __name__ == "__main__":
    consolidate_to_34()
