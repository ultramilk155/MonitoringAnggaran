
import oracledb
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from app import create_app

def extract_filtered():
    app = create_app()
    with app.app_context():
        dsn = oracledb.makedsn(
            app.config['ORACLE_HOST'], 
            app.config['ORACLE_PORT'], 
            sid=app.config['ORACLE_SID']
        )
        
        try:
            connection = oracledb.connect(
                user=app.config['ORACLE_USER'],
                password=app.config['ORACLE_PASS'],
                dsn=dsn
            )
            
            print("Executing Filtered Query (EE Filter) for UPPL 2025...")
            
            # List of Expense Elements from user request/image
            ee_filter = "('E201', 'E202', 'E203', 'E204', 'F101', 'F104', 'F106', 'F107')"
            
            query = f"""
SELECT
a.DSTRCT_CODE,
a.PROCESS_DATE,
a.REC900_TYPE,
a.TRANSACTION_NO,
a.USERNO,
a.ACCOUNTANT,
a.ACCOUNT_CODE,
case when substr (trim(ACCOUNT_CODE),-3) in ('301','311','313','411') then 'Reimburse' else 'Fix' end Fix_Reimburs,
substr(a.ACCOUNT_CODE,1,1) SEG1NUM,
case when a.ACCOUNT_CODE is not null then (select b.CCTRE_SEG_DESC from msf920 b where SEGMENT_LEVEL = '01' and substr(a.ACCOUNT_CODE,1,1) = substr(b.COST_CTRE_SEG,1,1)  and b.ACTIVE_STATUS = 'A' )
end SEG1,
substr(a.ACCOUNT_CODE,2,2) SEG2NUM,
case when a.ACCOUNT_CODE is not null then (select b.CCTRE_SEG_DESC from msf920 b where SEGMENT_LEVEL = '02' and substr(a.ACCOUNT_CODE,2,2) = substr(b.COST_CTRE_SEG,1,2)  and b.ACTIVE_STATUS = 'A' )
end SEG2,
substr(a.ACCOUNT_CODE,4,2) SEG3NUM,
case when a.ACCOUNT_CODE is not null then (select b.CCTRE_SEG_DESC from msf920 b where SEGMENT_LEVEL = '03' and substr(a.ACCOUNT_CODE,4,2) = substr(b.COST_CTRE_SEG,1,2)  and b.ACTIVE_STATUS = 'A' )
end SEG3,
substr(a.ACCOUNT_CODE,6,3) SEG4NUM,
case when a.ACCOUNT_CODE is not null then (select b.CCTRE_SEG_DESC from msf920 b where SEGMENT_LEVEL = '04' and substr(a.ACCOUNT_CODE,6,3) = substr(b.COST_CTRE_SEG,1,3)  and b.ACTIVE_STATUS = 'A' )
end SEG4,
substr(a.ACCOUNT_CODE,9,3) SEG5NUM,
case when a.ACCOUNT_CODE is not null then (select b.CCTRE_SEG_DESC from msf920 b where SEGMENT_LEVEL = '05' and substr(a.ACCOUNT_CODE,9,3) = substr(b.COST_CTRE_SEG,1,3)  and b.ACTIVE_STATUS = 'A' )
end SEG5,
substr(a.ACCOUNT_CODE,12,2) SEG6NUM,
case when a.ACCOUNT_CODE is not null then (select b.CCTRE_SEG_DESC from msf920 b where SEGMENT_LEVEL = '06' and substr(a.ACCOUNT_CODE,12,2) = substr(b.COST_CTRE_SEG,1,2)  and b.ACTIVE_STATUS = 'A' )
end SEG6,
substr(a.ACCOUNT_CODE,14,2) SEG7NUM,
case when a.ACCOUNT_CODE is not null then (select b.CCTRE_SEG_DESC from msf920 b where SEGMENT_LEVEL = '07' and substr(a.ACCOUNT_CODE,14,2) = substr(b.COST_CTRE_SEG,1,2)  and b.ACTIVE_STATUS = 'A' )
end SEG7,
substr(a.ACCOUNT_CODE,16,4) EENUM,
case when a.ACCOUNT_CODE is not null then (select c.EXP_ELE_DESC from msf930 c where substr(a.ACCOUNT_CODE,16,4) = substr(c.EXP_ELEMENT,1,4)  and c.ACTIVE_STATUS = 'A' )
end EE,
substr(a.ACCOUNT_CODE,16,1) EE_satu,
a.ACCT_PROFILE,
a.ADJ_RSN_CODE,
a.ALLOC_AR_INV_NO,
a.AR_INV_NO,
a.AR_INV_TYPE,
a.ASSET_CLASSIF,
a.ASSET_NO,
a.ASSET_TY,
a.ATAX_CODE,
a.ATAX_RATE_9,
a.AUTH_BY,
a.AUTO_JNL_FLG,
a.AUTO_SUS_IND,
a.AVERAGE_PRICE,
a.BANK_ACCT_NO,
a.BENEFIT_TYPE,
a.BIN_CODE,
a.BPU_CODE,
a.BRANCH_CODE,
a.CASH_INV_FLAG,
a.CATEGORY_NO,
a.CHEQUE_NO,
a.CHEQUE_RUN_NO,
a.CHEQUE_TYPE,
a.CLAIM_NO,
a.CONSOLIDATE_Z,
a.CONTRACT_NO,
a.CPR_LOC,
a.CPTLSD_QTY,
a.CREATION_DATE,
substr(trim(CREATION_DATE),1,4) cd_tahun,
substr(trim(CREATION_DATE),5,2) cd_bulan,
substr(trim(CREATION_DATE),8,2) cd_tanggal,
a.CREATION_TIME,
a.CREATION_USER,
a.CTAX_CODE,
a.CURRENCY_IND,
a.CURRENCY_TYPE,
a.CUSTODIAN_ID,
a.CUST_NO,
a.CUST_REF,
a.DEPR_REC_TY,
a.DESCRIPTION,
a.DESC_LINE,
a.DOCUMENT_REF,
a.ELEMENT_NO,
a.EMPLOYEE_ID,
a.EQUIP_NO,
a.EXCHANGE_RATE,
a.EXT_INV_NO,
a.FAR_DISTRICT,
a.FA_TRAN_AMT,
a.FA_TRAN_DESC,
a.FOR_CURR_IND,
a.FREIGHT_AMT,
a.FUEL_OIL_TY,
a.FULL_PERIOD,
a.INABILTY_FLG,
a.INSTALL_ID,
a.INT_DIST_IND,
a.INVENT_CAT,
a.INVENT_COSTING,
a.INVENT_PR_AFT,
a.INVENT_PR_BFR,
a.INVT_VAL_AFT,
a.INVT_VAL_BFR,
a.INV_DATE,
a.INV_DSTRCT,
a.INV_ITEM_DESC,
a.INV_ITEM_NO,
a.INV_QTY,
a.IREQ_ITEM,
a.IREQ_ITEM_NO,
a.IREQ_TYPE,
a.ISSUED_BY,
a.ISSUE_REQ_NO,
a.ISS_DSTRCT_CDE,
a.ISS_TYPE,
a.ITEM_NO,
a.ITRAN_TYPE,
a.JOURNAL_DESC,
a.JOURNAL_TYPE,
a.LAB_BATCH_NO,
a.LAB_COST_CL,
a.LAB_EARN_CDE,
a.LAB_RATE,
a.LAST_MOD_DATE,
a.LAST_MOD_TIME,
a.LAST_MOD_USER,
a.LINE_NO,
a.LITRES_ISS,
a.MANJNL_VCHR,
a.MEMO_AMOUNT,
a.MEMO_EQUIP,
a.MEMO_STOCK_CODE,
a.MEMO_WORK_ORDER,
a.MIMS_SL_KEY,
a.NET_PRICE,
a.NET_PR_ADJ_I,
a.NET_PR_ADJ_P,
a.NET_PR_UOI,
a.NET_PR_UOP,
a.NEW_QTY,
a.NEW_QTY_UOI,
a.NO_OF_HOURS,
a.OD_FLAG,
a.OLD_NET_PR_UOI,
a.OLD_QTY,
a.OLD_QTY_UOI,
a.ON_COST_AMT,
a.OPERATOR_ID,
a.ORD_SUPPLIER,
a.ORIG_DST_CDE,
a.OVERRIDE_SW,
a.PAYMENT_REF,
a.PAY_REC_CODE,
a.PC_COMPLETE,
a.PMT_SUPPLIER,
a.PORTION_NO,
a.POSTED_STATUS,
a.PO_ITEM,
a.PO_NO,
a.PREQ_ITEM_NO,
a.PREQ_NO,
a.PREV_NET_PR,
a.PREV_NP_UOI,
a.PREV_NP_UOP,
a.PRICE_CHANGE,
a.PRICING_CODE,
a.PROJECT_NO,
CASE a.project_no WHEN ' ' THEN
CASE WHEN a.tran_type = 'ISS' THEN
		(join(CURSOR(SELECT DISTINCT Decode(b.project_no, ' ', c.project_no, b.project_no) prk_no
			FROM msf232 c, msf620 b
			WHERE SubStr(c.requisition_no, 1, 6) =  a.issue_req_no AND c.dstrct_code = a.dstrct_code AND c.req_232_type = 'I' AND SubStr(c.requisition_no, 9, 4) = '0000' AND
          c.dstrct_code = b.dstrct_code (+) AND c.work_order = b.work_order (+)), ', '))
		WHEN a.tran_type IN ('PRD', 'SVR') THEN
          (join(CURSOR(SELECT DISTINCT Decode(b.project_no, ' ', c.project_no, b.project_no) prk_no
          FROM msf232 c, msf620 b
          WHERE SubStr(c.requisition_no, 1, 6) =  a.preq_no AND c.dstrct_code = a.dstrct_code AND c.req_232_type = 'P' AND SubStr(c.requisition_no, 9, 3) = '000' AND
          c.dstrct_code = b.dstrct_code (+) AND c.work_order = b.work_order (+)), ', '))
		WHEN a.tran_type IN ('SRD') THEN
          (JOIN(CURSOR(SELECT c.ref_code
          FROM msf071 c, msf240 b
          WHERE c.entity_type = 'PUR' AND
          SubStr(c.entity_value, 2, 4) = b.dstrct_code AND
          SubStr(c.entity_value, 6, 9) = b.stock_code AND
          SubStr(c.entity_value, 15, 3) = b.activity_ctr AND
          b.order_no = a.po_no AND
          b.stock_code = a.stock_code AND
          b.dstrct_code = a.dstrct_code), ', '))
        ELSE
          ' '
        END
      ELSE a.project_no
      END PRK_QUERY_DIVANG,
a.PR_ADJ_UOI,
a.PU_CODE,
a.QTY_ADJ_UOI,
a.QTY_ADJ_UOP,
a.QTY_AMOUNT,
a.QTY_RCV_UOI,
a.QTY_RCV_UOP,
a.QUANTITY_ISS,
a.QUANTITY_REPD,
a.QUANTITY_REQ,
a.RATE_AMOUNT,
a.RCPT_DIST_CODE,
a.RECEIPT_AMOUNT,
a.RECEIPT_CURRENCY,
a.RECEIPT_DATE,
a.RECEIPT_NUM,
a.RECEIPT_REF,
a.RECEIVED_BY,
a.REF_DOC,
a.REPORT_STATUS,
a.REP_REQ_ITEM,
a.REP_REQ_NO,
a.REQUESTED_BY,
a.REQ_ITEM,
a.REQ_NO,
a.REQ_TYPE,
a.RESOURCE_TYPE,
a.RESPONS_CODE,
a.REVENUE_CODE,
a.REVERSAL_IND,
a.REVS_KEY_900,
a.RLOC_DESC,
a.RLOC_FROM_ACCT,
a.RLOC_FROM_WO,
a.RLOC_METHOD,
a.RLOC_TO_ACCT,
a.RLOC_TO_PROJECT,
a.RLOC_TO_WO,
a.RLOC_VAR_ACCT,
a.SALES_PERSON_ID,
a.SERV_ITM_IND,
a.SHIFT,
a.SOH_AFTER,
a.SOH_AFTER_BIN,
a.SOH_AFTER_WH,
a.STAT_TYPE,
a.STAT_VALUE,
a.STND_JNL_NO,
a.STOCK_CODE,
a.STOREMAN_ID,
a.SUB_ASSET_NO,
a.SUPPLIER_NO,
a.SUPPLY_CUST_ID,
a.TASK_ID,
a.TAX_CLASS,
a.TAX_CODE,
a.TAX_PC_AFT,
a.TAX_PC_BEF,
a.TAX_PERCENT,
a.TRACK_REQID,
a.TRANS_NO,
a.TRAN_AMOUNT,
a.TRAN_AMOUNT_S,
a.TRAN_GROUP_KEY,
a.TRAN_TYPE,
a.TRAN_TYPE_IND,
a.TRNDTE_REVSD,
a.UNITS_COMPLETE,
a.UNIT_OF_ISSUE,
a.UNIT_OF_PURCH,
a.UNIT_PRICE,
a.VAL_INC_TAX_F,
a.VAL_INC_TAX_L,
a.VAL_INC_TAX_S,
a.VERS_NO,
a.VINTAGE,
a.WHOUSE_ID,
a.WH_ONCOST_AMT,
a.WORK_ORDER,
      CASE WHEN a.inv_item_desc <> ' ' THEN a.inv_item_desc
        WHEN a.journal_desc <> ' ' THEN a.journal_desc
        WHEN a.fa_tran_desc <> ' ' THEN a.fa_tran_desc
        WHEN a.description <> ' ' THEN a.description
        WHEN a.rloc_desc <> ' ' THEN a.rloc_desc
        WHEN a.tran_type IN ('SVR', 'SRD', 'PRD','PRC') THEN a.po_no
        WHEN a.tran_type IN ('ISS') THEN a.stock_code
        ELSE a.desc_line
      END description,
a.WO_TASK_NO,
a.XRATE_TYPE,
a.XREF_DSTRCT_CODE,
a.BANK_RECON_STATUS,
a.BANK_RECON_UUID,
a.BANK_STAT_UUID,
a.DEPOSIT_REF,
a.EXTRACT10_IND,
a.EXTRACT1_IND,
a.EXTRACT2_IND,
a.EXTRACT3_IND,
a.EXTRACT4_IND,
a.EXTRACT5_IND,
a.EXTRACT6_IND,
a.EXTRACT7_IND,
a.EXTRACT8_IND,
a.EXTRACT9_IND,
a.FROM_PAR_PROJ,
a.MATCH_REF_UUID,
a.RECONCILED_DATE,
a.REL_ENT_CODE,
a.TO_PARENT_PROJ,
a.GRANT_LINE_NO,
a.JNL_ITEM,
a.JNL_SOURCE,
a.JOURNAL_DISTRICT,
a.LAST_MOD_EMP,
a.JOURNAL_DESC || a.DESC_LINE as FULL_JNL_DESC,
SUBSTR(a.MIMS_SL_KEY,3,9) as NIK,
case when SUBSTR(a.MIMS_SL_KEY,3,9) is not null then (select TRIM(TRIM (b.first_name) || ' ' || TRIM (b.surname)) from ellipse.msf810 b where TRIM(substr(a.MIMS_SL_KEY,3,12)) = TRIM(b.employee_id))
end nama2
FROM
	msf900 a
WHERE
	DSTRCT_CODE = 'UPPL' 
	AND process_date >= '20250101' 
    and process_date <= '20251201' 
    AND substr(a.ACCOUNT_CODE,16,4) IN {ee_filter}
            """
            
            cursor = connection.cursor()
            cursor.execute(query)
            
            # Fetch columns and handle duplicates
            raw_cols = [col[0] for col in cursor.description]
            seen = {}
            new_cols = []
            for col in raw_cols:
                if col in seen:
                    seen[col] += 1
                    new_cols.append(f"{col}_{seen[col]}")
                else:
                    seen[col] = 0
                    new_cols.append(col)
            
            # Fetch in chunks
            chunk_size = 500
            dfs = []
            total = 0
            
            while True:
                rows = cursor.fetchmany(chunk_size)
                if not rows:
                    break
                
                dfs.append(pd.DataFrame(rows, columns=new_cols))
                total += len(rows)
                print(f"Fetched {total} rows so far...")
            
            print(f"Total extracted: {total}. Saving to Excel...")
            
            if dfs:
                final_df = pd.concat(dfs)
                output_file = "filtered_transactions_uppl_2025.xlsx"
                final_df.to_excel(output_file, index=False)
                print(f"Exported to {output_file}")
            else:
                print("No data found matching the criteria.")

            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    extract_filtered()
