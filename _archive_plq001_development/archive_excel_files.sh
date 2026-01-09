#!/bin/bash
# Archive test Excel files

echo "Moving test Excel files to archive..."

# Production file to KEEP: PLQ001_REPLICATED_PERFECT_FINAL.xlsx
# Everything else is test/intermediate files

# Move test/intermediate Excel files
mv -v "PLQ001_REPLICATED_PERFECT_100PERCENT.xlsx" _archive_plq001_development/ 2>/dev/null || true
mv -v "comparison_by_expense_element.xlsx" _archive_plq001_development/ 2>/dev/null || true
mv -v "comparison_exact_vs_original.xlsx" _archive_plq001_development/ 2>/dev/null || true
mv -v "discrepancy_details_plq_vs_my.xlsx" _archive_plq001_development/ 2>/dev/null || true
mv -v "extra_tgks_not_in_original.xlsx" _archive_plq001_development/ 2>/dev/null || true
mv -v "filtered_transactions_uppl_2025.xlsx" _archive_plq001_development/ 2>/dev/null || true
mv -v "project_no_mismatches.xlsx" _archive_plq001_development/ 2>/dev/null || true
mv -v "replicated_plq001_100percent.xlsx" _archive_plq001_development/ 2>/dev/null || true
mv -v "replicated_plq001_absolute_final.xlsx" _archive_plq001_development/ 2>/dev/null || true
mv -v "replicated_plq001_exact.xlsx" _archive_plq001_development/ 2>/dev/null || true
mv -v "replicated_plq001_final.xlsx" _archive_plq001_development/ 2>/dev/null || true
mv -v "replicated_plq001_perfect.xlsx" _archive_plq001_development/ 2>/dev/null || true
mv -v "replicated_plq001_uppl_2025.xlsx" _archive_plq001_development/ 2>/dev/null || true
mv -v "row_by_row_mismatches.xlsx" _archive_plq001_development/ 2>/dev/null || true
mv -v "test_joins_result.xlsx" _archive_plq001_development/ 2>/dev/null || true

# Also move the report file
mv -v "merge_verification_report.md" _archive_plq001_development/ 2>/dev/null || true

echo ""
echo "Excel files archived!"
echo "Production file kept: PLQ001_REPLICATED_PERFECT_FINAL.xlsx"
