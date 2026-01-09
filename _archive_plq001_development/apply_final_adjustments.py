
from app import create_app
from app.extensions import db
from app.models import BudgetLine

def apply_adjustments():
    app = create_app()
    with app.app_context():
        # Diffs provided by user
        # Target = Current + Diff
        adjustments = {
            "PL252O0102": -13683128.0,
            "PL252P0102": -81637365.0,
            "PL252P0105": -81805540.40,
            "PL252P0107": 81637365.0,
            "PL252P0108": 95488668.40 # Derived sum
        }
        
        print("Applying User Adjustments...")
        
        lines = BudgetLine.query.filter_by(tahun=2025).all()
        bl_map = {bl.no_prk: bl for bl in lines}
        
        for prk, diff in adjustments.items():
            if prk in bl_map:
                bl = bl_map[prk]
                old_val = bl.ellipse_rp or 0
                new_val = old_val + diff
                
                print(f"  {prk}: {old_val:,.2f} + ({diff:,.2f}) -> {new_val:,.2f}")
                bl.ellipse_rp = new_val
            else:
                print(f"  ERROR: {prk} not found!")

        db.session.commit()
        
        total_val = sum([bl.ellipse_rp or 0 for bl in BudgetLine.query.filter_by(tahun=2025).all()])
        print(f"\nFinal Total: Rp {total_val:,.2f}")

if __name__ == "__main__":
    apply_adjustments()
