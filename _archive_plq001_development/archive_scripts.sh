#!/bin/bash
# Archive experimental/test scripts from PLQ001 development

# Create archive folder
mkdir -p _archive_plq001_development

# Move test scripts to archive
echo "Moving test scripts to _archive_plq001_development/..."

# PLQ001 Replication Tests
mv -v replicate_perfect.py _archive_plq001_development/ 2>/dev/null || true
mv -v replicate_final.py _archive_plq001_development/ 2>/dev/null || true
mv -v replicate_absolute_final.py _archive_plq001_development/ 2>/dev/null || true

# Comparison Scripts
mv -v compare_plq001_details.py _archive_plq001_development/ 2>/dev/null || true
mv -v compare_discrepancy.py _archive_plq001_development/ 2>/dev/null || true
mv -v compare_keys.py _archive_plq001_development/ 2>/dev/null || true
mv -v compare_exact.py _archive_plq001_development/ 2>/dev/null || true
mv -v compare_exact_fields.py _archive_plq001_development/ 2>/dev/null || true
mv -v compare_row_by_row.py _archive_plq001_development/ 2>/dev/null || true

# Analysis Scripts
mv -v analyze_plq001_pattern.py _archive_plq001_development/ 2>/dev/null || true
mv -v analyze_acct_pattern.py _archive_plq001_development/ 2>/dev/null || true
mv -v analyze_aggregation.py _archive_plq001_development/ 2>/dev/null || true

# Verification Scripts
mv -v verify_project_no_final.py _archive_plq001_development/ 2>/dev/null || true
mv -v final_verification.py _archive_plq001_development/ 2>/dev/null || true
mv -v check_db_vs_file_discrepancy.py _archive_plq001_development/ 2>/dev/null || true
mv -v verify_merge_composition.py _archive_plq001_development/ 2>/dev/null || true

# Debugging Scripts
mv -v debug_plq001_sum.py _archive_plq001_development/ 2>/dev/null || true
mv -v debug_single_pair.py _archive_plq001_development/ 2>/dev/null || true
mv -v investigate_blank_project.py _archive_plq001_development/ 2>/dev/null || true
mv -v investigate_extra_rows.py _archive_plq001_development/ 2>/dev/null || true

# Check Scripts
mv -v check_2025_data.py _archive_plq001_development/ 2>/dev/null || true
mv -v check_2081_rows.py _archive_plq001_development/ 2>/dev/null || true
mv -v check_219m.py _archive_plq001_development/ 2>/dev/null || true
mv -v check_broad_duplicates.py _archive_plq001_development/ 2>/dev/null || true
mv -v check_budget_line_data.py _archive_plq001_development/ 2>/dev/null || true
mv -v check_duplicates.py _archive_plq001_development/ 2>/dev/null || true
mv -v check_duplicates_structure.py _archive_plq001_development/ 2>/dev/null || true
mv -v check_excel_headers.py _archive_plq001_development/ 2>/dev/null || true
mv -v check_ghost_accounts.py _archive_plq001_development/ 2>/dev/null || true
mv -v check_id_excel.py _archive_plq001_development/ 2>/dev/null || true
mv -v check_merge_targets.py _archive_plq001_development/ 2>/dev/null || true
mv -v check_missing_projects.py _archive_plq001_development/ 2>/dev/null || true
mv -v check_orig_duplicates.py _archive_plq001_development/ 2>/dev/null || true
mv -v check_project_no_col.py _archive_plq001_development/ 2>/dev/null || true
mv -v check_uppl_transactions.py _archive_plq001_development/ 2>/dev/null || true

# Calculation Scripts
mv -v calculate_plq001_total.py _archive_plq001_development/ 2>/dev/null || true
mv -v calculate_filtered_total.py _archive_plq001_development/ 2>/dev/null || true
mv -v extract_filtered_transactions.py _archive_plq001_development/ 2>/dev/null || true

# Creation Scripts
mv -v create_perfect_final.py _archive_plq001_development/ 2>/dev/null || true
mv -v create_perfect_indexed.py _archive_plq001_development/ 2>/dev/null || true

# Other Scripts
mv -v find_extra_tgks.py _archive_plq001_development/ 2>/dev/null || true
mv -v identify_orphans.py _archive_plq001_development/ 2>/dev/null || true
mv -v inspect_carry_overs.py _archive_plq001_development/ 2>/dev/null || true
mv -v revert_created_lines.py _archive_plq001_development/ 2>/dev/null || true
mv -v sync_dashboard_plq001.py _archive_plq001_development/ 2>/dev/null || true
mv -v update_dashboard_ellipse.py _archive_plq001_development/ 2>/dev/null || true
mv -v organize_scripts_plan.py _archive_plq001_development/ 2>/dev/null || true

echo ""
echo "Archive complete!"
echo "Archived scripts are in: _archive_plq001_development/"
