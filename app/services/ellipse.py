import oracledb
from flask import current_app

class EllipseDB:
    def get_connection(self):
        """
        Establishes a connection to the Oracle database using config values.
        """
        try:
            dsn = oracledb.makedsn(
                current_app.config['ORACLE_HOST'], 
                current_app.config['ORACLE_PORT'], 
                sid=current_app.config['ORACLE_SID']
            )
            
            connection = oracledb.connect(
                user=current_app.config['ORACLE_USER'],
                password=current_app.config['ORACLE_PASS'],
                dsn=dsn
            )
            return connection
        except Exception as e:
            print(f"Oracle Connection Error: {e}")
            return None

    def check_connection(self):
        """
        Verifies if the connection is alive.
        Returns: (success: bool, message: str)
        """
        conn = None
        try:
            conn = self.get_connection()
            if conn:
                version = conn.version
                return True, f"Connected (v{version})"
            else:
                return False, "Failed to connect"
        except Exception as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def fetch_prk_realization(self, project_codes, year=None):
        """
        Fetches realization (TRAN_AMOUNT) sum from MSF900 for given project codes.
        
        Args:
            project_codes: List of PRK codes (used for mapping, though query pulls all for context)
            year: Integer year to filter data (default: current year)
            
        Returns:
            Dictionary {full_project_code: amount}
        """
        import datetime
        conn = self.get_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        results = {}
        
        # Default year if not provided
        if not year:
            year = datetime.datetime.now().year
            
        start_date = f"{year}0101"
        end_date = f"{year}1231"
        
        # Prepare valid PRK set for faster lookup in Python
        # (We will pull everything for the criteria and filter in Python to ensure 
        # the complex PRK derivation logic matches)
        valid_prks = set(project_codes)
        
        # Initialize all requested codes to 0
        for code in project_codes:
            results[code] = 0

        try:
            query = f"""
SELECT
    -- 1. Project No (Logika mencari Project No agar tidak kosong -- Derived PRK)
    CASE a.project_no 
        WHEN ' ' THEN
            CASE 
                WHEN a.tran_type = 'ISS' THEN
                    (SELECT DISTINCT LISTAGG(Decode(b.project_no, ' ', c.project_no, b.project_no), ', ') WITHIN GROUP (ORDER BY Decode(b.project_no, ' ', c.project_no, b.project_no))
                     FROM msf232 c, msf620 b
                     WHERE SubStr(c.requisition_no, 1, 6) = a.issue_req_no 
                     AND c.dstrct_code = a.dstrct_code 
                     AND c.req_232_type = 'I' 
                     AND SubStr(c.requisition_no, 9, 4) = '0000' 
                     AND c.dstrct_code = b.dstrct_code (+) 
                     AND c.work_order = b.work_order (+))
                WHEN a.tran_type IN ('PRD', 'SVR') THEN
                    (SELECT DISTINCT LISTAGG(Decode(b.project_no, ' ', c.project_no, b.project_no), ', ') WITHIN GROUP (ORDER BY Decode(b.project_no, ' ', c.project_no, b.project_no))
                     FROM msf232 c, msf620 b
                     WHERE SubStr(c.requisition_no, 1, 6) = a.preq_no 
                     AND c.dstrct_code = a.dstrct_code 
                     AND c.req_232_type = 'P' 
                     AND SubStr(c.requisition_no, 9, 3) = '000' 
                     AND c.dstrct_code = b.dstrct_code (+) 
                     AND c.work_order = b.work_order (+))
                WHEN a.tran_type IN ('SRD') THEN
                    (SELECT DISTINCT LISTAGG(c.ref_code, ', ') WITHIN GROUP (ORDER BY c.ref_code)
                     FROM msf071 c, msf240 b
                     WHERE c.entity_type = 'PUR' 
                     AND SubStr(c.entity_value, 2, 4) = b.dstrct_code 
                     AND SubStr(c.entity_value, 6, 9) = b.stock_code 
                     AND SubStr(c.entity_value, 15, 3) = b.activity_ctr 
                     AND b.order_no = a.po_no 
                     AND b.stock_code = a.stock_code 
                     AND b.dstrct_code = a.dstrct_code)
                ELSE ' ' 
            END
        ELSE a.project_no 
    END AS REAL_PROJECT_NO,

    -- 2. Jumlah Rupiah
    a.TRAN_AMOUNT

FROM
    msf900 a
WHERE
    a.DSTRCT_CODE = 'UPPL'
    AND a.PROCESS_DATE >= :start_date
    AND a.PROCESS_DATE <= :end_date
    
    -- Filter Expense Element (Material Fixed & Jasa Borongan Fixed)
    AND substr(a.ACCOUNT_CODE, 16, 4) IN (
        'E199',
        'E201', 'E202', 'E203', 'E204',
        'E310',
        'E410', 'E412',
        'F101', 'F102', 'F103', 'F104', 'F105', 'F106', 'F107', 'F108', 'F109',
        'F199',
        'F310', 'F312',
        'F410', 'F412'
    )
            """
            
            cursor.execute(query, start_date=start_date, end_date=end_date)
            rows = cursor.fetchall()
            
            # Aggregate results in Python
            for row in rows:
                derived_prk_raw = row[0]
                amount = row[1] or 0
                
                # Handle potentially None or dirty PRK strings
                if derived_prk_raw:
                    # The derived PRK might be a listagg or contain spaces, 
                    # but typically for 1-to-1 matching we expect a clean code.
                    # We will try to match it against our valid list.
                    
                    # Also, the derived PRK from Oracle might satisfy the 'PL' prefix or not.
                    # In our previous debugging, Oracle returned '252...' while User uses 'PL252...'
                    # So we need to normalize.
                    
                    derived_prk = str(derived_prk_raw).strip()
                    
                    # Try direct match
                    if derived_prk in valid_prks:
                         results[derived_prk] += float(amount)
                    else:
                        # Try adding 'PL' prefix if missing
                        pl_prefixed = f"PL{derived_prk}"
                        if pl_prefixed in valid_prks:
                             results[pl_prefixed] += float(amount)
                        
                        # Note: If it still doesn't match, we ignore it 
                        # (it's a transaction for a project we are not tracking)
                    
            return results
            
        except Exception as e:
            print(f"Error fetching realization: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            cursor.close()
            conn.close()

# Singleton instance for easy import
ellipse_service = EllipseDB()
