
from app import create_app
from app.models import BudgetLine

app = create_app()
with app.app_context():
    # Targets that we created
    targets = ["242G0101", "242G0102", "232M0103"]
    
    print("Broad search for targets:")
    for t in targets:
        print(f"\nSearching for *{t}*...")
        # Search distinct deskripsi or no_prk
        items = BudgetLine.query.filter(
            (BudgetLine.no_prk.like(f'%{t}%')) | 
            (BudgetLine.kode.like(f'%{t}%'))
        ).all()
        
        if items:
            for item in items:
                print(f"  FOUND: ID={item.id}, NoPRK='{item.no_prk}', Desc='{item.deskripsi}', Tahun={item.tahun}")
        else:
            print("  Not found.")
            
    # List ALL 2025 PRKs to visually check
    print("\nAll 2025 PRKs:")
    all_2025 = BudgetLine.query.filter_by(tahun=2025).all()
    for item in all_2025:
        print(f"ID={item.id} | {item.no_prk} | {item.deskripsi[:40]}")
