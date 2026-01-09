
from app import create_app
from app.extensions import db
from app.models import BudgetLine

def revert_additions():
    app = create_app()
    with app.app_context():
        # Identify the lines to delete
        # These are the ones we identified as 'created' in previous step
        # Safest way: delete by specific NO_PRK list
        to_delete = [
            "PL-", "PL232M0103", "PL232P0102", "PL242G0101", "PL242G0102", "PL242I0204",
            "PL242J0102", "PL242L0101", "PL242M0101", "PL242P0102", "PL242P0201",
            "PL242P0301", "PL242P0401", "PL252D0000", "PL252S0303"
        ]
        
        print(f"Deleting {len(to_delete)} BudgetLines...")
        
        count = 0
        for prk in to_delete:
            item = BudgetLine.query.filter_by(no_prk=prk, tahun=2025).first()
            if item:
                print(f"  Deleting ID {item.id}: {item.no_prk} ({item.deskripsi}) - Ellipse: {item.ellipse_rp:,.0f}")
                db.session.delete(item)
                count += 1
            else:
                print(f"  Not found (already deleted?): {prk}")
                
        db.session.commit()
        print(f"Done. Deleted {count} lines.")
        
        # Recalculate Dashboard Total
        total_remaining = sum([bl.ellipse_rp or 0 for bl in BudgetLine.query.filter_by(tahun=2025).all()])
        print(f"New Dashboard Total: Rp {total_remaining:,.2f}")

if __name__ == "__main__":
    revert_additions()
