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

# Singleton instance for easy import
ellipse_service = EllipseDB()
