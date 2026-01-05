import oracledb
from dotenv import load_dotenv
load_dotenv()
from app import create_app
from app.services.ellipse import ellipse_service

app = create_app()

def format_currency(value):
    if value is None:
        return "0"
    return f"{value:,.2f}"

def check_uppl_transactions(identifiers):
    district = 'UPPL'
    print(f"Checking MSF900 transactions in {district} for {len(identifiers)} identifiers...")
    
    with app.app_context():
        connection = ellipse_service.get_connection()
        cwd = connection.cursor()

        print("\n" + "="*80)
        print(f"{'Project No':<15} | {'Total TRAN_AMOUNT':<20} | {'Count':<10}")
        print("="*80)

        total_all = 0

        for raw_id in identifiers:
            project_id = raw_id
            if project_id.startswith('PL'):
                project_id = project_id[2:]

            try:
                # Targeted query for specific District + Project
                query = f"""
                    SELECT SUM(TRAN_AMOUNT), COUNT(*) 
                    FROM MSF900 
                    WHERE DSTRCT_CODE = '{district}' 
                      AND PROJECT_NO = '{project_id}'
                """
                cwd.execute(query)
                row = cwd.fetchone()
                
                amount = row[0] if row[0] else 0
                count = row[1] if row[1] else 0
                
                total_all += amount
                
                print(f"{project_id:<15} | {format_currency(amount):<20} | {count:<10}")

            except Exception as e:
                print(f"{project_id:<15} | Error: {e}")

        print("="*80)
        print(f"Grand Total     : {format_currency(total_all)}")
        print("="*80)
        
        cwd.close()
        connection.close()

if __name__ == "__main__":
    ids_to_check = [
        "PL252G0101", "PL252G0102", "PL252G0103", "PL252I0101", "PL252I0102",
        "PL252I0103", "PL252I0104", "PL252J0101", "PL252J0102", "PL252J0103",
        "PL252K0101", "PL252L0101", "PL252M0102", "PL252N0101", "PL252N0102",
        "PL252N0103", "PL252O0101", "PL252O0102", "PL252O0103", "PL252O0104",
        "PL252O0105", "PL252O0106", "PL252O0107", "PL252O0108", "PL252O0109",
        "PL252P0101", "PL252P0102", "PL252P0103", "PL252P0104", "PL252P0105",
        "PL252P0106", "PL252P0107", "PL252P0108", "PL252P0109"
    ]
    check_uppl_transactions(ids_to_check)
