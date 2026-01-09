#!/usr/bin/env python3
"""
Script Organization Analysis
Categorizes all test/experimental scripts created during development.
"""

# PRODUCTION/CORE FILES (DO NOT MOVE)
core_files = [
    'run.py',           # Main application runner
    'config.py',        # Configuration
    'main.py',          # Entry point (if used)
    'models.py',        # DB Models (if standalone)
    'migrate_jobs.py',  # Migration utility (keep for reference)
]

# FINAL WORKING SCRIPTS (KEEP IN ROOT - PROVEN SOLUTIONS)
final_scripts = [
    'merge_final_dashboard.py',      # Final proven merge script
    'consolidate_to_34.py',           # Consolidation to 34 lines
    'cleanup_zero_items.py',          # Zero-value cleanup
    'apply_final_adjustments.py',     # User-specified adjustments
]

# TEST/EXPERIMENTAL SCRIPTS (MOVE TO ARCHIVE)
test_scripts = [
    # PLQ001 Replication Tests
    'replicate_perfect.py',
    'replicate_final.py', 
    'replicate_absolute_final.py',
    
    # Comparison & Analysis
    'compare_plq001_details.py',
    'compare_discrepancy.py',
    'compare_keys.py',
    'compare_exact.py',
    'compare_exact_fields.py',
    'compare_row_by_row.py',
    
    # Data Analysis
    'analyze_plq001_pattern.py',
    'analyze_acct_pattern.py',
    'analyze_aggregation.py',
    
    # Verification Scripts
    'verify_project_no_final.py',
    'final_verification.py',
    'check_db_vs_file_discrepancy.py',
    'verify_merge_composition.py',
    
    # Debugging Scripts
    'debug_plq001_sum.py',
    'debug_single_pair.py',
    'investigate_blank_project.py',
    'investigate_extra_rows.py',
    
    # Check Scripts
    'check_2025_data.py',
    'check_2081_rows.py',
    'check_219m.py',
    'check_broad_duplicates.py',
    'check_budget_line_data.py',
    'check_duplicates.py',
    'check_duplicates_structure.py',
    'check_excel_headers.py',
    'check_ghost_accounts.py',
    'check_id_excel.py',
    'check_merge_targets.py',
    'check_missing_projects.py',
    'check_orig_duplicates.py',
    'check_project_no_col.py',
    'check_uppl_transactions.py',
    
    # Calculation & Extraction Tests
    'calculate_plq001_total.py',
    'calculate_filtered_total.py',
    'extract_filtered_transactions.py',
    
    # Creation/Assembly Scripts
    'create_perfect_final.py',
    'create_perfect_indexed.py',
    
    # Other Test Scripts
    'find_extra_tgks.py',
    'identify_orphans.py',
    'inspect_carry_overs.py',
    'revert_created_lines.py',
    'sync_dashboard_plq001.py',
    'update_dashboard_ellipse.py',
]

print("=" * 80)
print("SCRIPT ORGANIZATION PLAN")
print("=" * 80)
print(f"\nCORE FILES (Keep in root): {len(core_files)}")
for f in core_files:
    print(f"  ✓ {f}")

print(f"\nFINAL WORKING SCRIPTS (Keep in root): {len(final_scripts)}")
for f in final_scripts:
    print(f"  ✓ {f}")

print(f"\nTEST/EXPERIMENTAL SCRIPTS (Move to archive): {len(test_scripts)}")
for f in test_scripts:
    print(f"  → {f}")

print(f"\nTotal scripts to archive: {len(test_scripts)}")
