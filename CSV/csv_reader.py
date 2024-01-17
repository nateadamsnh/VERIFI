import datetime
import tkinter as tk
import csv
import pandas as pd
import mysql.connector



# def checkType(a_list):
#     for element in a_list:
#         if isinstance(element, int):
#             print("It's an Integer")
#         if isinstance(element, str):
#             print("It's an string")
#         if isinstance(element, float):
#             print("It's an floating number")

# numbers = [1, 2, 3, "xyz"]
# checkType(numbers)
def determine_Column_Datatype(rowValues):
    retList = []

    for row in rowValues:

        if isinstance(row, int):
            retList.append("INT")
        elif isinstance(row, str):
            retList.append("STRING")
        elif isinstance(row, float):
            retList.append("FLOAT")
        elif isinstance(row, datetime):
            retList.append("DATETIME")

    return retList

 
def read_csv_to_database(csv_filesetId, csv_file, parent_or_child):

    try:

        conn = mysql.connector.connect(user='root', password='Olliespoint1999*', host='127.0.0.1', database='dev_verifi2', charset = 'utf8')
        cursor = conn.cursor()

        # Log start of loading this csv..
        eventSource = "CSVLoader"
        logArgs = (eventSource, "Start loading file", csv_file) 
        cursor.callproc("sp_Log_Insert_Event", logArgs)        

        # Get just the file name portion of the passed in path and file.
        fileName = csv_file[csv_file.rfind("\\")+1:]


        # cursor.execute("DROP TABLE IF EXISTS CSV_HEADER")
        cursor.execute("CREATE TABLE IF NOT EXISTS csv_header (id INT UNSIGNED NOT NULL AUTO_INCREMENT, csv_fileset_id int, csv_name varchar(128), csv_table varchar(128), " +
                       "csv_column varchar(128), csv_type varchar(50), primary key (id))" )
        
        # Delete everything in the table if we are loading parent (note: parent csv's have to be the first to load in the set)
        if parent_or_child == "P":
            cursor.execute("DELETE from csv_header")
            cursor.execute("ALTER TABLE csv_header AUTO_INCREMENT = 1")
        else:
            cursor.execute("DELETE from csv_header where csv_name = %s", (fileName,) )

        # Limit the maximum column width for the file to load to table.
        # this is necessary because any csv too wide may cause an error on table creation.
        limitCount = 100

        # Open csv and insert just the column names into the db table header table. 
        df = pd.read_csv(csv_file)
        for name in df.columns:
            cursor.execute("INSERT INTO csv_header (csv_fileset_id, csv_name, csv_column, csv_type) VALUES (%s, %s, %s, %s)", (csv_filesetId, fileName, name, parent_or_child, ) )


        # DATA TYPE DETERMINATION HERE...
        # Need to iterate thru each column (on the second row) of the CSV and determine the datatype, int, date, datetime or string
        # using regular expressions in python. 
        # def mytype(v):
        #     s = str(v)
        #     regex = re.compile(r'(?P<list>\[[^]]+\])|(?P<float>\d*\.\d+)|(?P<int>\d+)|(?P<string>[a-zA-Z]+)')
        #     return  r"<type '%s'>" % regex.search(s).lastgroup

        # Get the column count use to create multiple tables if needed (column count > limitCount)
        cursor.execute("select count(1) as COUNTER from csv_header where csv_name = %s", (fileName, ))
        result = cursor.fetchall()
        columnCount = result[0]


        # ****************************** LOOP HERE TO CHUNK BASED ON NUMBER OF FIELDS ADDED 
        for offset in range(0,int(columnCount[0]), limitCount):        
            #print(offset)

            # *****

            # PASS THE csv_fileset_id TO THE PROCEDURE CALL BELOW AND MODIFY THE VIEW TO GET THE MAX
            # ID FOR THE SET OF TABLES INCLUSIVE OF CHILDREN IF THE FILE TYPE = C, IGNORE FOR P
            # create table to load the csv table fields to (limitCount fields at a time as the csv may wider then mysql permits)
            # this procedure uses the data inserted into csv_header table directly above. 
            args = (csv_filesetId, parent_or_child, fileName, limitCount, offset) 
            cursor.callproc("sp_Create_CSV_Table", args )
            resultSet = cursor.stored_results()

            # *****
            
            # construct the sql
            insertStmt = "insert into CSV_IMPORT_" + fileName[0:14]  + str(offset) + " ("
            valuesStmt = "(%s,"
            for results in resultSet: 
                for rows in results.fetchall():
                    insertStmt = insertStmt + (rows[0])
                    valuesStmt = valuesStmt + "%s,"

            insertStmt = insertStmt[:len(insertStmt)-2] + ") VALUES "
            valuesStmt = valuesStmt[:len(valuesStmt)-4] + ")"
            fullSqlStmt = insertStmt + valuesStmt
            #print(fullSqlStmt)

            # Read the CSV file and insert the data into the database
            with open(csv_file, "r", encoding='utf8') as file:
                csv_reader = csv.reader(file)
                # next(csv_reader)  # Skip the header row
                for row in csv_reader:
                    # print (row[offset:limitCount+offset])
                    cursor.execute(fullSqlStmt, row[offset:limitCount+offset])

            csv_ImportTableName = "CSV_IMPORT_" + fileName[0:14]  + str(offset)

            # Update the header table and set the table name to the import table name just created 
            # for the fields it uses... note that the idrel is relative id which is necessary in cases
            # where there are multiple loads as the id (pk and autoincrement) may not be sufficient as its absolute. 
            cursor.execute("UPDATE csv_header a set csv_table = %s WHERE csv_name = %s " + 
                       " AND id = (SELECT id FROM vw_relative_header_id b WHERE a.id = b.id AND a.csv_name = b.csv_name AND b.idrel >= %s)", (csv_ImportTableName, fileName, str(offset), ))

            # ****************************** END CHUNKING LOOP HERE

        
        # if the column count > limitCount then we need to create a view
        if int(columnCount[0]) > limitCount:
            viewArg = (fileName,)
            cursor.callproc("sp_Loader_Create_View", viewArg )

        # logArgs = (eventSource, "End loading file", csv_file) 
        # cursor.callproc("sp_Log_Insert_Event", logArgs)  


        conn.commit()
        conn.close()
        
         

        return True
    except Exception as e:
        # Log the error
        print(f"Error: {e}")
        return False
 

def create_Parent_Child_view():
    # Create master view from parent view with child tables (if there are any)
    # 1) Determine if there are any child tables
    # 2) Get the parent key and key field positions.
    # 3) Get the full list of all fields across all tables (and parent view)
    # 4) Construct the view using the child tables as LOJ

    # conn = mysql.connector.connect(user='root', password='Olliespoint1999*', host='127.0.0.1', database='dev_verifi2', charset = 'utf8')
    # cursor = conn.cursor()

    # cursor.execute("select count(1) as COUNTER from csv_header where csv_type = 'C'")
    # result = cursor.fetchall()
    # childCount = result[0]

    # if childCount > 0:

    print("test")

# ************************************************************************** 
# **************************************************************************
# LOAD THE CSV'S
# Example usage
csv_file1 = "C:\MAIN\Verify\csv\RESULTS_PARENTThaiCompleteSurvey(v1).csv"
csv_file2 = "C:\MAIN\Verify\csv\RESULTS_CHILD1ThaiCompleteSurvey(v1)-rubber_plot.csv"
csv_file3 = "C:\MAIN\Verify\csv\RESULTS_CHILD2Thai CompleteSurvey(v1)-somrom.csv"
csv_filesetId = 1
 
# Import CSV into database
import_successful = read_csv_to_database(csv_filesetId, csv_file1, "P")
if import_successful:
    print("CSV read 1 successfully")
else:
    print("Failed to read 1 CSV")
 
import_successful = read_csv_to_database(csv_filesetId, csv_file2, "C")
if import_successful:
    print("CSV read 2 successfully")
else:
    print("Failed to read 2 CSV")

import_successful = read_csv_to_database(csv_filesetId, csv_file3, "C")
if import_successful:
    print("CSV read 3 successfully")
else:
    print("Failed to read 3 CSV")    

# **************************************************************************
# **************************************************************************
# CREATE THE MASTER VIEW THAT CONSOLIDATES THE PARENT AND CHILD CSV'S LOADED ABOVE
    
create_view = create_Parent_Child_view()

