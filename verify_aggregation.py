from app import app, db, BudgetLine, JobDetail, update_budget_line_totals

def verify():
    with app.app_context():
        # Get or create a test budget line
        bl = BudgetLine.query.first()
        if not bl:
            print("No BudgetLine found. Creating one.")
            bl = BudgetLine(kode='TEST', no_prk='TEST-PRK', deskripsi='Test')
            db.session.add(bl)
            db.session.commit()
            
        print(f"Initial State: RAB={bl.usulan_rab_rp}, Terkontrak={bl.terkontrak_rp}")
        
        # Add a test job
        job = JobDetail(
            budget_line_id=bl.id,
            nama_pekerjaan="Test Job Verification",
            rab_sebelum_ppn=1000000,
            terkontrak_rp=800000,
            terbayar_rp=500000
        )
        db.session.add(job)
        db.session.commit()
        
        print("Job Added. Running update...")
        
        # Manually trigger update logic (simulating app.py)
        # We need to fetch BL again or ensure it's refreshed to see the new job
        # update_budget_line_totals takes a budget_line object.
        # If we pass the 'bl' object from before commit, does 'bl.jobs' have the new job?
        
        # In app.py: we do update_budget_line_totals(budget_line) right after commit.
        # Let's see if SQLALchemy auto-refreshes the relationship.
        
        update_budget_line_totals(bl)
        
        print(f"Updated State: RAB={bl.usulan_rab_rp}, Terkontrak={bl.terkontrak_rp}")
        
        if bl.usulan_rab_rp >= 1000000:
             print("SUCCESS: BudgetLine updated correctly.")
        else:
             print("FAILURE: BudgetLine totals did not increase.")
             
        # Cleanup
        db.session.delete(job)
        # Re-update to clean stats
        db.session.commit()
        update_budget_line_totals(bl)

if __name__ == "__main__":
    verify()
