
from jinjasql import JinjaSql
import mysql.connector
import matplotlib
import pandas as pd



def main():


    conn = mysql.connector.connect(user='root', password='Olliespoint1999*', host='127.0.0.1', database='dev_verifi2', charset = 'utf8')
    cursor = conn.cursor()

    sqlStmt = '''SELECT AVG(age) AS AVERAGE_AGE, gender FROM (SELECT FLOOR(DATEDIFF(NOW(), 
    DATE( CSV_FIELD{{ sSourceDbField }} )) / 365) AS age, CSV_FIELD{{ sGroupDbField }} AS gender 
    FROM VW_IMP_TABLES WHERE CSV_FIELD{{ sSourceDbField }} > '' AND CSV_FIELD{{ sGroupDbField }} > '' AND id > 1) a WHERE age > 4 GROUP BY gender'''

    params = {
    'sSourceDbField': 15,
    'sGroupDbField': 26,
    }


    j = JinjaSql(param_style='pyformat')
    query, bind_params = j.prepare_query(sqlStmt, params)
    
    # print(query)
    # print(bind_params)
    frm = pd.read_sql(query, conn, params=bind_params)    
    ax = frm.plot.bar(x='gender', y='AVERAGE_AGE', rot=0)
    # print(query % bind_params)

    # results = cursor.execute(query % bind_params)
    # results = cursor.fetchall()
    # for rows in results:
    #     print(rows)    

    conn.commit()
    conn.close()    


main()