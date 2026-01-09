#!/bin/bash
# Final Cleanup of Root Directory

echo "Moving remaining test scripts to archive..."

# Migration/Fix Scripts (Already proven and can be archived)
mv -v app_backup.py _archive_plq001_development/ 2>/dev/null || true
mv -v apply_final_adjustments.py _archive_plq001_development/ 2>/dev/null || true
mv -v cleanup_zero_items.py _archive_plq001_development/ 2>/dev/null || true
mv -v consolidate_to_34.py _archive_plq001_development/ 2>/dev/null || true
mv -v merge_final_dashboard.py _archive_plq001_development/ 2>/dev/null || true

# Old/Junk Scripts
mv -v main.py _archive_plq001_development/ 2>/dev/null || true
mv -v models.py _archive_plq001_development/ 2>/dev/null || true

# Test Scripts
mv -v replicate_plq001_100percent.py _archive_plq001_development/ 2>/dev/null || true
mv -v replicate_plq001_exact.py _archive_plq001_development/ 2>/dev/null || true
mv -v replicate_plq001.py _archive_plq001_development/ 2>/dev/null || true
mv -v search_transaction_fast.py _archive_plq001_development/ 2>/dev/null || true
mv -v search_transaction_source.py _archive_plq001_development/ 2>/dev/null || true

# Verification Scripts
mv -v verify_100_match.py _archive_plq001_development/ 2>/dev/null || true
mv -v verify_aggregation.py _archive_plq001_development/ 2>/dev/null || true
mv -v verify_column_list.py _archive_plq001_development/ 2>/dev/null || true
mv -v verify_edit_delete.py _archive_plq001_development/ 2>/dev/null || true
mv -v verify_missing_transaction.py _archive_plq001_development/ 2>/dev/null || true
mv -v verify_progress.py _archive_plq001_development/ 2>/dev/null || true

echo ""
echo "Final Cleanup Complete!"
