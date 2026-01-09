
import pandas as pd
from app import create_app
from app.models import BudgetLine

def check_targets():
    app = create_app()
    with app.app_context():
        carry_overs = [
            "232M0103", "232P0102", "242G0101", "242G0102", "242I0204",
            "242J0102", "242L0101", "242M0101", "242P0102", "242P0201",
            "242P0301", "242P0401"
        ]
        
        print("Checking target 2025 PRKs for carry-overs:")
        
        mapping = {} # old -> new
        
        for co in carry_overs:
            # Logic: Replace prefix year (232/242) with 252.
            # CO format: YYZ + Suffix. 242G0101. 
            # Target: PL252 + G0101.
            suffix = co[3:] # G0101
            target_prk = "PL252" + suffix
            
            # Check DB
            exists = BudgetLine.query.filter_by(no_prk=target_prk, tahun=2025).first()
            if exists:
                print(f"  ✅ {co} -> {target_prk} (Found: {exists.deskripsi[:30]})")
                mapping[co] = target_prk
            else:
                print(f"  ❌ {co} -> {target_prk} NOT FOUND")
                
        # Look for 13,683,128 match
        print("\nSearching for transaction amount 13,683,128:")
        df = pd.read_excel("PLQ001_REPLICATED_PERFECT_FINAL.xlsx")
        df['AMT'] = pd.to_numeric(df['TRAN_AMOUNT'], errors='coerce')
        
        matches = df[df['AMT'].abs() == 13683128]
        if not matches.empty:
            print(matches[['PROJECT_NO', 'TRAN_AMOUNT', 'DESCRIPTION_FINAL']].to_string())
        else:
            print("No transaction with absolute value 13,683,128 found.")
            
        return mapping

if __name__ == "__main__":
    check_targets()
