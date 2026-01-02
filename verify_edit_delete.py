from app import app, db, BudgetLine, JobDetail, update_budget_line_totals

def verify_edit_delete():
    with app.app_context():
        # Setup: Create a test budget line
        bl = BudgetLine.query.filter_by(kode='TEST_ED').first()
        if bl:
            db.session.delete(bl)
            db.session.commit()
            
        bl = BudgetLine(kode='TEST_ED', no_prk='TEST-PRK-ED', deskripsi='Test Edit Delete')
        db.session.add(bl)
        db.session.commit()
        
        # 1. Add Job
        job = JobDetail(
            budget_line_id=bl.id,
            nama_pekerjaan="Job 1",
            rab_sebelum_ppn=1000,
            terkontrak_rp=0,
            terbayar_rp=0
        )
        db.session.add(job)
        db.session.commit()
        update_budget_line_totals(bl)
        
        print(f"Initial: RAB={bl.usulan_rab_rp} (Expected 1000)")
        if bl.usulan_rab_rp != 1000:
             print("FAIL: Initial Add failed")
             return

        # 2. Simulate Edit
        # Find job again to ensure fresh session state
        job = JobDetail.query.get(job.id)
        job.rab_sebelum_ppn = 5000
        job.terkontrak_rp = 2000
        db.session.commit()
        update_budget_line_totals(bl)
        
        # Refresh BL
        bl = BudgetLine.query.get(bl.id)
        print(f"After Edit: RAB={bl.usulan_rab_rp} (Expected 5000), Terkontrak={bl.terkontrak_rp} (Expected 2000)")
        
        if bl.usulan_rab_rp == 5000 and bl.terkontrak_rp == 2000:
            print("PASS: Edit functionality works (totals updated).")
        else:
            print("FAIL: Edit functionality failed.")
            
        # 3. Simulate Delete
        db.session.delete(job)
        db.session.commit()
        update_budget_line_totals(bl)
        
        # Refresh BL
        bl = BudgetLine.query.get(bl.id)
        print(f"After Delete: RAB={bl.usulan_rab_rp} (Expected 0)")
        
        if bl.usulan_rab_rp == 0:
            print("PASS: Delete functionality works (totals updated).")
        else:
            print("FAIL: Delete functionality failed.")

        # Cleanup
        db.session.delete(bl)
        db.session.commit()

if __name__ == "__main__":
    verify_edit_delete()
