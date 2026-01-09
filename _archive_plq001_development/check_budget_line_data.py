
from app import create_app
from app.models import BudgetLine

app = create_app()
with app.app_context():
    items = BudgetLine.query.limit(10).all()
    print("ID | Kode | No PRK | Deskripsi | Ellipse RP")
    print("-" * 60)
    for item in items:
        print(f"{item.id} | {item.kode} | {item.no_prk} | {item.deskripsi[:30]} | {item.ellipse_rp}")
