
from app import create_app
from app.models import BudgetLine

def list_candidates():
    app = create_app()
    with app.app_context():
        lines = BudgetLine.query.filter_by(tahun=2025).all()
        print(f"Total Lines: {len(lines)}")
        
        core = []
        orphans = []
        
        for bl in lines:
            # Assume Core items are those with Pagu > 0
            # OR those that match the standard PL252 format we expect?
            # User said "34 items". Let's see which ones have Pagu.
            if (bl.pagu_total or 0) > 0:
                core.append(bl)
            else:
                orphans.append(bl)
                
        print(f"\nCORE ITEMS (Pagu > 0): {len(core)}")
        for x in core:
            print(f"  [{x.kode}] {x.no_prk} : {x.deskripsi[:40]} | Pagu: {x.pagu_total:,.0f}")
            
        print(f"\nORPHAN ITEMS (Pagu = 0): {len(orphans)}")
        for x in orphans:
            print(f"  [{x.kode}] {x.no_prk} : {x.deskripsi[:40]} | Real: {x.ellipse_rp:,.0f}")

if __name__ == "__main__":
    list_candidates()
