import datetime
import pandas as pd
import mysql.connector
import configparser
# from jinjasql import JinjaSql
# import matplotlib
# import pandas as pd

def Log(dbCursor, eventSource, eventMessage, eventDetail):
    logArgs = (eventSource, eventMessage, eventDetail) 
    dbCursor.callproc("sp_Log_Insert_Event", logArgs)     

def GetColumnPosFromName(dbCursor, columnName):
    retVal = []
    dbCursor.execute("SELECT CONCAT('CSV_FIELD', fn_GetColumnPosFromName(%s))", (columnName, ))
    results = dbCursor.fetchall()
    retVal = results[0][0]
    return (retVal)

def ProcessPlot(dbCursor, rowToProcess):

    # SELECT
    # CSV_FIELD18 AS Input_Farm_ID,
    # CAST(CSV_FIELD142 AS DECIMAL) AS PGS_total_yield_daily
    # FROM csv_import_results_parent0 cip0,
    #     csv_import_results_parent100 cip1
    # WHERE cip0.id = cip1.id
    # AND cip0.id > 1
    # AND CSV_FIELD18 > ''
    # AND CSV_FIELD142 > ''
    # ORDER BY 2 ASC;

    print(rowToProcess)


def ProcessAverage(dbCursor, rowToProcess):

    # using the object rowToProcess, construct the sql string above.
    # note, if the rowToProcess("sourceDbField") = a date and not a number, need to convert to a date.
    # note, need to use vw_relative_header_id for relative positioning of fields as id in insufficient.
    # {'id': 1, 'sourceDbTable': 'VW_IMP_TABLES', 'sourceDbField': '_age', 'operation': 'AVERAGE', 'groupId': 2, 'groupDbField': 'gender', 'operationOrderId': 1}

    # 1) get the position of the field (sourceDbField) from vw_relative_header_id which maps to the CSV_FIELD in the table (sourceDbTable)
    sSourceDbField = GetColumnPosFromName(dbCursor, rowToProcess["sourceDbField"]) # SELECT fn_GetColumnPosFromName('_age'); returns 15
    # 2) get the position of the field (group_field_name) from vw_relative_header_id which also maps to the CSV_FIELD in the table (sourceDbTable)
    sGroupDbField = GetColumnPosFromName(dbCursor, rowToProcess["group_field_name"]) # SELECT fn_GetColumnPosFromName('gender'); returns 26
    # 3) get the source table from which to selct on..
    sSourceDbTable = rowToProcess["sourceDbTable"]

    # 4) using the items above, construct the sql and place results into the process_results table.

    # Need to query against a 'post loaded', cleaned up dataset from the csv data?
    # if so, then we may be able to simplify the query to calc a direct average against fields
    # that are durable (i.e. not null, legit age instead of DOB, etc)


    # sqlStmt = '''SELECT AVG(age) AS AVERAGE_AGE, gender FROM (SELECT FLOOR(DATEDIFF(NOW(), 
    #     DATE( {{ sSourceDbField }} )) / 365) AS age, {{ sGroupDbField }} AS gender 
    #     FROM {{ sSourceDbTable }} WHERE {{ sSourceDbField }} > '' AND {{ sGroupDbField }} > '' AND id > 1) a WHERE age > 4 GROUP BY gender'''

    # params = {
    # 'sSourceDbField': sSourceDbField,
    # 'sGroupDbField': sGroupDbField,
    # 'sSourceDbTable': sSourceDbTable,
    # }

    # sqlStmt = '''SELECT AVG(age) AS AVERAGE_AGE, gender FROM (SELECT FLOOR(DATEDIFF(NOW(), 
    #     DATE( {{ sSourceDbField }} )) / 365) AS age, {{ sGroupDbField }} AS gender 
    #     FROM {{ sSourceDbTable }} WHERE {{ sSourceDbField }} > '' AND {{ sGroupDbField }} > '' AND id > 1) a WHERE age > 4 GROUP BY gender'''

    # j = JinjaSql(param_style='pyformat')
    # query, bind_params = j.prepare_query(sqlStmt, params)
    # frm = pd.read_sql(query, conn, params=bind_params)    
    # ax = frm.plot.bar(x='gender', y='AVERAGE_AGE', rot=0)

    # print(query % bind_params)

# ********************************************************************************************
# ********************************************************************************************
# ********************************************************************************************
    
def main_PostCsvLoad():
    # PURPOSE: to isolate all the data of interest as defined in the rules table.
    #          the fields in the rules table are saved off here. Only not null 
    #          values are saved as well as any data type validation (?) and 
    #          post load (csv) processing is done here.
    
    conn = mysql.connector.connect(user='root', password='Olliespoint1999*', host='127.0.0.1', database='dev_verifi2', charset = 'utf8')
    cursor = conn.cursor()

    # Log start of this function.
    eventSource = "main_PostCsvLoad"
    Log(cursor, eventSource, "Starting Process", None)


    conn.commit()
    conn.close()


# ********************************************************************************************
# ********************************************************************************************
# ********************************************************************************************    

def main_ProcessRules():

    try:

        conn = mysql.connector.connect(user='root', password='Olliespoint1999*', host='127.0.0.1', database='dev_verifi2', charset = 'utf8')
        cursor = conn.cursor()


        # Log start of this function.
        eventSource = "main_ProcessRules"
        Log(cursor, eventSource, "Starting Process", None)

        
        # Read the rules to process.

        rowsDict = []
        cursorDict = conn.cursor(dictionary=True)
        cursorDict.callproc("sp_Server_GetRules")
        resultSet = cursorDict.stored_results()

        # Load from DB cursorDict into a dictionary object.
        for result in resultSet:
            for row in result.fetchall():
                rowsDict.append(dict(row))

        for row in rowsDict:
            match row["operation"]:
                case "PLOT":
                    ProcessPlot(cursor, row)
                case "AVERAGE":
                    ProcessAverage(cursor, row)
                case _:
                    print("default")

        # # Construct the logic to process the rules based on the contents of the array.
        # # Output the results to a process results table.
        # # Log end of processing rules.

        conn.commit()
        conn.close()

        return True
    except Exception as e:
        # Log the error
        print(f"Error: {e}")
        return False            




# CALL THIS TO ISOLATE THE DATA (CSV) LOADED INTO A POST LOAD TABLE.
# THIS POST LOAD TABLE IS MEANT TO CONTAIN ONLY THE FIELDS FROM THE RULES TABLE THAT ARE NEEDED 
# AND HAS THE DURABLE DATA (NOT NULL, IS NOT REPEATED, ETC)

if not main_PostCsvLoad():
    print ("error executing main_PostLoad, see above")
else:
    print ("Successfully Executed main_PostLoad")

# CALL THIS TO PROCESS RULES AGAINST DATA THAT HAS BEEN SCRUBBED AND STORED INTO A PROCESS TABLE.
# if not main_ProcessRules():
#     print ("error executing main_ProcessRules, see above")
# else:
#     print ("Successfully Executed main_ProcessRules")