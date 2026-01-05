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

    def fetch_prk_realization(self, project_codes):
        """
        Fetches realization (TRAN_AMOUNT) sum from MSF900 for given project codes.
        Returns a dictionary {full_project_code: amount}
        """
        conn = self.get_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        results = {}
        
        # Prepare codes: strip 'PL' for querying, keep map to original
        # Map: stripped_code -> original_code
        code_map = {}
        processed_codes = []
        
        for code in project_codes:
            clean_code = code[2:] if code.startswith('PL') else code
            code_map[clean_code] = code
            processed_codes.append(clean_code)
            results[code] = 0 # Default to 0
            
        if not processed_codes:
            return results

        try:
            # We can't pass a list directly to IN clause easily in binding 
            # if the list is huge, but for reasonable size it's fine.
            # Using manual string formatting for transparency/simplicity here 
            # as these are internal codes.
            
            # For Oracle IN clause limit (1000), we might need chunking 
            # but assuming < 1000 items for now.
            
            codes_str = "'" + "','".join(processed_codes) + "'"
            
            query = f"""
                SELECT PROJECT_NO, SUM(TRAN_AMOUNT)
                FROM MSF900
                WHERE DSTRCT_CODE = 'UPPL'
                  AND PROJECT_NO IN ({codes_str})
                GROUP BY PROJECT_NO
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                proj_no = row[0]
                amount = row[1] or 0
                
                # Map back to original code
                if proj_no in code_map:
                    original = code_map[proj_no]
                    results[original] = float(amount)
                    
            return results
            
        except Exception as e:
            print(f"Error fetching realization: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

# Singleton instance for easy import
ellipse_service = EllipseDB()
