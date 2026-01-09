
from app import create_app
from app.models import BudgetLine
from app.extensions import db
from sqlalchemy import func

app = create_app()
with app.app_context():
    # Check for duplicates in no_prk for 2025
    duplicates = db.session.query(
        BudgetLine.no_prk, func.count(BudgetLine.id)
    ).filter_by(tahun=2025).group_by(BudgetLine.no_prk).having(func.count(BudgetLine.id) > 1).all()
    
    if duplicates:
        print(f"FOUND {len(duplicates)} DUPLICATE PRKs:")
        for prk, count in duplicates:
            print(f"  {prk}: {count} times")
            items = BudgetLine.query.filter_by(no_prk=prk, tahun=2025).all()
            for item in items:
                print(f"    ID: {item.id} | Desc: {item.deskripsi} | Amt: {item.ellipse_rp}")
    else:
        print("No exact string duplicates found in no_prk.")

    # Check for potential near-duplicates (e.g. spacing)
    print("\nChecking for potential near-duplicates (normalized):")
    all_lines = BudgetLine.query.filter_by(tahun=2025).all()
    norm_map = {}
    
    for item in all_lines:
        norm_prk = item.no_prk.strip().upper().replace(" ", "")
        if norm_prk in norm_map:
            prev = norm_map[norm_prk]
            print(f"  POTENTIAL DUPLICATE: '{item.no_prk}' (ID {item.id}) vs '{prev.no_prk}' (ID {prev.id})")
        else:
            norm_map[norm_prk] = item

    # Check the 15 created items specifically
    created_prks = [
        "PL-", "PL232M0103", "PL232P0102", "PL242G0101", "PL242G0102", "PL242I0204",
        "PL242J0102", "PL242L0101", "PL242M0101", "PL242P0102", "PL242P0201",
        "PL242P0301", "PL242P0401", "PL252D0000", "PL252S0303"
    ]
    
    print("\nVerifying Created Items status:")
    for prk in created_prks:
        lines = BudgetLine.query.filter_by(no_prk=prk, tahun=2025).all()
        if len(lines) > 1:
             print(f"  ❌ {prk} exists {len(lines)} times!")
        elif len(lines) == 1:
             print(f"  ✅ {prk} exists once.")
        else:
             print(f"  ❓ {prk} missing?")
