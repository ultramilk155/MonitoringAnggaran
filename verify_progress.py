from app import app, db, BudgetLine, JobDetail, JobProgress, User

def verify_progress():
    with app.app_context():
        db.create_all()
        # Setup: Ensure Admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Admin user not found. Run app first.")
            return

        # Create a test job
        bl = BudgetLine.query.first()
        if not bl:
             bl = BudgetLine(kode='TEST_PROG', no_prk='TEST-PROG', deskripsi='Test Progress')
             db.session.add(bl)
             db.session.commit()

        job = JobDetail(
            budget_line_id=bl.id,
            nama_pekerjaan="Test Progress Job"
        )
        db.session.add(job)
        db.session.commit()
        
        # 1. Add Progress Log
        print("Adding progress log...")
        log = JobProgress(
            job_id=job.id,
            user_id=admin.id,
            notes="Testing progress log entry",
            progress_percent=25
        )
        db.session.add(log)
        db.session.commit()
        
        # 2. Verify Log exists
        saved_log = JobProgress.query.filter_by(job_id=job.id).first()
        if saved_log and saved_log.notes == "Testing progress log entry" and saved_log.progress_percent == 25:
            print("PASS: Progress log saved correctly.")
        else:
            print("FAIL: Progress log not found or incorrect.")
            
        # 3. Verify Relationship
        job_refreshed = JobDetail.query.get(job.id)
        if len(job_refreshed.progress_logs) > 0:
            print("PASS: JobDetail relationship works.")
            print(f"Log content: {job_refreshed.progress_logs[0].notes}")
        else:
             print("FAIL: JobDetail relationship failed.")

        # Cleanup
        db.session.delete(saved_log)
        db.session.delete(job)
        if bl.kode == 'TEST_PROG':
            db.session.delete(bl)
        db.session.commit()

if __name__ == "__main__":
    verify_progress()
