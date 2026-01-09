
from app import create_app
from app.models import BudgetLine

app = create_app()
with app.app_context():
    # List of missing projects from previous step output
    missing_prks = [
        "PL232M0103", "PL232P0102", "PL242G0101", "PL242G0102", "PL242I0204",
        "PL242J0102", "PL242L0101", "PL242M0101", "PL242P0102", "PL242P0201",
        "PL242P0301", "PL242P0401", "PL252D0000", "PL252S0303"
    ]
    
    print("Checking if missing projects exist in ANY year:")
    for prk in missing_prks:
        items = BudgetLine.query.filter_by(no_prk=prk).all()
        if items:
            for item in items:
                print(f"Found {prk}: ID={item.id}, Tahun={item.tahun}, Ellipse={item.ellipse_rp}")
        else:
            print(f"Not found: {prk}")
