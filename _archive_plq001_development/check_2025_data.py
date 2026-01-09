
from app import create_app
from app.models import BudgetLine

app = create_app()
with app.app_context():
    # Check 2025
    items = BudgetLine.query.filter_by(tahun=2025).limit(10).all()
    print("Checking 2025 Budget Lines:")
    if not items:
        print("No budget lines found for 2025")
    else:
        print("ID | Kode | No PRK | Deskripsi | Ellipse RP")
        for item in items:
            print(f"{item.id} | {item.kode} | {item.no_prk} | {item.deskripsi[:30]} | {item.ellipse_rp}")
            
    # Also check if there are any PRKs starting with '252'
    print("\nChecking for PRKs starting with '252':")
    items_252 = BudgetLine.query.filter(BudgetLine.no_prk.like('%252%')).limit(5).all()
    for item in items_252:
        print(f"{item.id} | {item.tahun} | {item.no_prk}")
