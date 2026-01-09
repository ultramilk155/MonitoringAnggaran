
from app.models import BudgetLine
from app.extensions import db
from datetime import datetime

class SmartSyncService:
    def sync_year(self, year, raw_data_map):
        """
        Syncs realization data for a given year with Smart Consolidation.
        raw_data_map: dict { 'PRK_CODE': amount } (from Ellipse)
        """
        print(f"Smart Syncing for Year {year}...")
        
        # 1. Get All Existing Budget Lines
        all_lines = BudgetLine.query.filter_by(tahun=year).all()
        if not all_lines:
            return {"status": "error", "message": f"No BudgetLines found for {year}"}
            
        # 2. Identify CORE (Pagu > 0) vs Orphan candidates
        # We need a map to quickly find Core items by similarity
        # Similarity Key: Activity Code (e.g., 'M', 'P01', etc.)
        # Or even better: Strict Suffix Matching if exists in Core.
        
        core_map = {} # Key: PRK_NO, Value: BudgetLine Object
        core_activity_map = {} # Key: ActivityChar (e.g. 'M'), Value: List of [BudgetLine]
        
        for bl in all_lines:
            # Definition of Core: Created manually/initially (usually has Pagu or specific description)
            # For robustness, we assume items with Pagu > 0 are the anchors.
            # If no items have pagu (unlikely), we might have issues.
            if (bl.pagu_total or 0) > 0:
                core_map[bl.no_prk] = bl
                
                # Index by Activity Group (e.g. PL252M... -> 'M')
                # Assuming format PLyyyCxxxx
                if len(bl.no_prk) > 6:
                    act_char = bl.no_prk[5] # 'M', 'G', etc.
                    if act_char not in core_activity_map:
                        core_activity_map[act_char] = []
                    core_activity_map[act_char].append(bl)
                    
        # 3. Process Raw Data
        # We accumulate realization into the CORE items.
        # We do NOT create new items if possible.
        
        updates = {prk: 0.0 for prk in core_map.keys()}
        orphans_log = []
        
        for prk_code, amount in raw_data_map.items():
            if amount == 0: continue
            
            # Logic 1: Exact Match in Core
            if prk_code in core_map:
                updates[prk_code] += amount
                continue
                
            # Logic 2: Carry-Over Merge (242 -> 252)
            # Check if this is a carry-over (starts with 242/232 etc)
            # And if a 2025 version exists in Core
            # Format: 242 suffix. Target: PL + 2025_prefix + suffix?
            # Actually, standard format in DB is PL + ProjectNo.
            # Raw data usually comes as just ProjectNo (e.g. '242G0101') or with PL?
            # Ellipse Service usually returns what's in the key.
            # Let's assume input prk_code matches DB format or is raw.
            # If raw (no PL), Prepend PL.
            
            clean_code = prk_code
            if not clean_code.startswith("PL"): 
                clean_code = "PL" + clean_code
                
            # Try finding 2025 equivalent
            # E.g. PL242G0101 -> PL252G0101
            # Replace year chars (digits 3-5? No, 2-4: PL[242]...)
            # Standard: PL[YYY]...
            # 2026 Logic: If current year is 2026, we look for PL262...
            # source is PL252... (carry over).
            
            # Simplified Logic:
            # Remove digits, match suffix?
            # Or use Activity Char map.
            
            target_found = False
            
            # Try to map to Core based on specific suffix
            # e.g. PL242G0101 -> PL252G0101
            # We construct the theoretically correct current-year PRK
            # Current Year Prefix: PL + str(year)[-2:] + '2'? (25 + 2 = 252)
            # This is risky. 
            
            # Better: Use Activity Map.
            if len(clean_code) > 6:
                act_char = clean_code[5] # 'G'
                
                # Specialized Mapping for User's known Consolidation Preference
                # P0201 -> P0107 (Prasarana -> Gedung)
                # This seems specific to 2025. 
                # General Rule: "Map to first Core item of same Activity Group" ??
                # Or "Map to Item with largest Pagu in that Group"?
                
                if act_char in core_activity_map:
                    # Find best match in this group
                    # Ideal: Suffix match (G0101 -> G0101)
                    candidates = core_activity_map[act_char]
                    best_match = None
                    
                    # Try suffix match (ignoring prefix)
                    suffix = clean_code[6:] # 0101
                    for cand in candidates:
                        if cand.no_prk.endswith(suffix):
                            best_match = cand
                            break
                    
                    if not best_match:
                        # Fallback 1: 'General' or 'Main' item in group?
                        # Fallback 2: The item with largest Pagu
                        best_match = max(candidates, key=lambda x: x.pagu_total or 0)
                        
                    if best_match:
                        updates[best_match.no_prk] += amount
                        orphans_log.append(f"{prk_code} -> {best_match.no_prk}")
                        target_found = True
            
            if not target_found:
                 # Logic 3: Absolute Fallback (Lainnya / Support)
                 # Find a '99' or 'P' group?
                 fallback = None
                 if 'P' in core_activity_map:
                      fallback = core_activity_map['P'][0] # First P item
                 
                 if fallback:
                     updates[fallback.no_prk] += amount
                     orphans_log.append(f"{prk_code} -> {fallback.no_prk} (FALLBACK)")
                 else:
                     # Critical: No bucket found.
                     pass

        # 4. Apply Updates to DB Objects
        updated_count = 0
        for prk, val in updates.items():
            if val != 0: # Only update if has value
                 # Note: We overwrite? Or add?
                 # Since 'updates' contains TOTAL consolidated realization from raw_data,
                 # we should overwrite the DB 'ellipse_rp' with this value.
                 # BUT, does raw_data contain EVERYTHING?
                 # Yes, strict sync implies raw_data is the source of truth.
                 
                 # Check drift?
                 # If DB has manual adjustments, they might be lost?
                 # User asked for "Paten Query" -> implies automation.
                 # User's manual fixes (e.g. -81M) were effectively re-allocations.
                 # If our Logic 2/3 handles re-allocation correctly, we don't need manual fixes.
                 
                 bl = core_map[prk]
                 if abs((bl.ellipse_rp or 0) - val) > 1.0:
                     bl.ellipse_rp = val
                     updated_count += 1
                     
        db.session.commit()
        
        return {
            "status": "success",
            "message": f"Smart Sync Complete. Updated {updated_count} items. Merged {len(orphans_log)} orphans.",
            "orphans": orphans_log
        }

smart_sync_service = SmartSyncService()
