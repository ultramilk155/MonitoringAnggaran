
from app import create_app
from app.extensions import db
from app.models import BudgetLine

def cleanup_zero_lines():
    app = create_app()
    with app.app_context():
        # Find 2025 lines with 0 Pagu and 0 Realisasi
        # Also check they are 'Auto-Created' types (no description or specific patterns?)
        # For safety, just checking 0/0 is usually enough for "Monitoring" view
        # unless user manually created a placeholder.
        
        candidates = BudgetLine.query.filter_by(tahun=2025).all()
        to_delete = []
        
        print("Scanning for Zero-Value lines (Pagu=0, Realisasi=0)...")
        
        for bl in candidates:
            pagu = bl.pagu_total or 0
            real = bl.ellipse_rp or 0
            
            # Use small epsilon for float comparison
            if abs(pagu) < 1.0 and abs(real) < 1.0:
                print(f"  Candidate: {bl.no_prk} ({bl.deskripsi}) - Ellipse: {real}")
                to_delete.append(bl)
                
        if not to_delete:
            print("No zero-value lines found.")
            return

        print(f"\nDeleting {len(to_delete)} lines...")
        for bl in to_delete:
            db.session.delete(bl)
            
        db.session.commit()
        print("Cleanup complete.")

if __name__ == "__main__":
    cleanup_zero_lines()
