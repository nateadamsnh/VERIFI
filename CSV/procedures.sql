USE dev_verifi2;

DROP PROCEDURE IF EXISTS sp_Create_CSV_Table;

DELIMITER $$

CREATE
DEFINER = 'root'@'localhost'
PROCEDURE sp_Create_CSV_Table (IN in_File_Set_Id int, IN in_Parent_Or_Child varchar(31), IN in_Csv_File varchar(128), IN in_Limit int, IN in_Offset int)
BEGIN

  DECLARE done int DEFAULT FALSE;
  DECLARE sqlStmt varchar(1023);
  DECLARE tableSqlPrefix varchar(511);
  DECLARE tableCreateSqlFields text DEFAULT '';
  DECLARE tableInsertSqlFields text DEFAULT '';
  DECLARE tableSqlPk varchar(127) DEFAULT 'primary key (id))';
  DECLARE sqlTableName varchar(1023);
  DECLARE curVal1 varchar(127);
  DECLARE curVal2 varchar(127);
  DECLARE curVal3 varchar(127);
  DECLARE curVal4 varchar(127);

  DECLARE cur1 CURSOR FOR
  SELECT
    CONCAT(CONCAT('CSV_FIELD', IDREL), ' TEXT NULL, '), 
    CONCAT('CSV_FIELD', IDREL),
    CONCAT(CONCAT('CSV_FIELD', IDREL + maxIdRel), ' TEXT NULL, '), 
    CONCAT('CSV_FIELD', IDREL + maxIdRel)
    FROM vw_relative_header_id
    WHERE CSV_NAME LIKE in_Csv_File ORDER BY IDREL LIMIT in_Limit OFFSET in_Offset;

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;


  OPEN cur1;

read_loop:
  LOOP
    FETCH cur1 INTO curVal1, curVal2, curVal3, curVal4;
    IF done THEN
      LEAVE read_loop;
    END IF;
    
    IF in_Parent_Or_Child = 'P' THEN
        SET tableCreateSqlFields = CONCAT(tableCreateSqlFields, curVal1);
        SET tableInsertSqlFields = CONCAT(tableInsertSqlFields, curVal2);
    ELSEIF in_Parent_Or_Child = 'C' THEN
        SET tableCreateSqlFields = CONCAT(tableCreateSqlFields, curVal3);
        SET tableInsertSqlFields = CONCAT(tableInsertSqlFields, curVal4);
    END IF; 
  END LOOP;

  CLOSE cur1;

  SET sqlTableName = CONCAT(CONCAT('CSV_IMPORT_', SUBSTR(in_Csv_File, 1, 14)), in_Offset);
  SET @sqlText = CONCAT('DROP TABLE IF EXISTS ', sqlTableName);
  PREPARE stmt FROM @sqlText;
  EXECUTE stmt;

  SELECT
    CONCAT('create table ', sqlTableName, ' ( id INT UNSIGNED NOT NULL AUTO_INCREMENT, ') INTO tableSqlPrefix;

  SET @sqlText = CONCAT(tableSqlPrefix, tableCreateSqlFields, tableSqlPk);
  PREPARE stmt FROM @sqlText;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;

  IF in_Parent_Or_Child = 'P' THEN
   SELECT 
    CONCAT(CONCAT('CSV_FIELD', IDREL), ', ') 
   FROM 
    vw_relative_header_id
   WHERE 
    CSV_NAME LIKE in_Csv_File 
   ORDER BY IDREL LIMIT in_Limit OFFSET in_Offset;
  ELSEIF in_Parent_Or_Child = 'C' THEN

   SELECT 
    CONCAT(CONCAT('CSV_FIELD', IDREL + maxIdRel), ', ') 
   FROM 
    vw_relative_header_id
   WHERE 
    CSV_NAME LIKE in_Csv_File 
   ORDER BY IDREL LIMIT in_Limit OFFSET in_Offset;


  end IF;



-- SELECT CONCAT('CSV_FIELD', ROW_NUMBER() OVER (PARTITION BY csv_name ORDER BY id), ', ') FROM csv_header" +      " where csv_name = %s ORDER BY id LIMIT %s OFFSET %s", args

END
$$

DELIMITER ;



DROP PROCEDURE IF EXISTS sp_Loader_Create_View;
delimiter ;;
CREATE PROCEDURE sp_Loader_Create_View(IN in_Csv_Name varchar(127))
BEGIN
  DECLARE done int DEFAULT FALSE;
  DECLARE viewCreateHeader     varchar(127) DEFAULT 'create or replace view VW_IMP_TABLES as SELECT ';
  DECLARE viewCreateFields     text DEFAULT '';
  DECLARE viewCreateFrom       text DEFAULT 'FROM ';
  DECLARE viewCreateWhere      text DEFAULT 'WHERE ';

  DECLARE curVal1 varchar(127);
  DECLARE curVal2 varchar(127);
  DECLARE curVal3 varchar(127);
  DECLARE cur1 CURSOR FOR
  SELECT 
  dimpTab.csv_table,
  isc.column_name,
  isc.ordinal_position 
  FROM 
  (SELECT DISTINCT csv_table FROM csv_header where csv_name = in_Csv_Name) dimpTab,
  information_schema.columns isc 
  WHERE 
  table_name       = dimpTab.csv_table
  AND table_schema = DATABASE()
  ORDER BY 
  1, 
  3;

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
  OPEN cur1;

  # Create view using the csv_name to find all import tables and columns created from the procedure sp_Create_CSV_Table.
  # needs to lookup tables and columns from csv_header and information_schema.columns for this database.

  # 1) get the list of import tables from the csv_header where the csv_name = in_CsvName
  # 2) For each table in the list, get the columns from information_schema.columns 
  # 3) using the import tables and columns, construct a sql string to create the view. 


read_loop:
  LOOP
    FETCH cur1 INTO curVal1, curVal2, curVal3;
    IF done THEN
      LEAVE read_loop;
    END IF;
    IF curVal2 != 'id' THEN
      set viewCreateFields = CONCAT(CONCAT(CONCAT(CONCAT(viewCreateFields, curVal1), '.'), curVal2), ', ');
    ELSE 
      # Add the first ID field only... 
      IF LENGTH(viewCreateFields) = 0 THEN
        set viewCreateFields = CONCAT(CONCAT(CONCAT(CONCAT(viewCreateFields, curVal1), '.'), curVal2), ', ');
      end IF;

      set viewCreateFrom   = CONCAT(CONCAT(viewCreateFrom, curVal1), ', ');
      set viewCreateWhere  = CONCAT(CONCAT(CONCAT(CONCAT(viewCreateWhere, curVal1), '.'), curVal2), ' = ');
    end IF;
  END LOOP;

  CLOSE cur1;

  set viewCreateFields = CONCAT(SUBSTR(viewCreateFields, 1, LENGTH(viewCreateFields) - 2), ' ');
  set viewCreateFrom   = CONCAT(SUBSTR(viewCreateFrom, 1, LENGTH(viewCreateFrom) - 2), ' ');
  set viewCreateWhere = SUBSTR(viewCreateWhere, 1, LENGTH(viewCreateWhere) - 3); 



  SET @sqlText =  CONCAT(CONCAT(CONCAT(viewCreateHeader, viewCreateFields), viewCreateFrom), viewCreateWhere);
  PREPARE stmt FROM @sqlText;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;

  -- SELECT @sqlText;


END;;
DELIMITER ;

CREATE OR REPLACE VIEW vw_relative_header_id
AS
SELECT
  ROW_NUMBER() OVER (PARTITION BY csv_name
  ORDER BY id) AS idrel,
  id,
  csv_table,
  csv_name,
  csv_column
FROM csv_header
WHERE -- csv_table = 'CSV_IMPORT_RESULTS_PARENT100'
csv_name = 'RESULTS_PARENTThaiCompleteSurvey(v1).csv'
ORDER BY 4, 3, 1;


DELIMITER ;;

drop function IF EXISTS fn_GetColumnPosFromName;
CREATE FUNCTION fn_GetColumnPosFromName(in_ColumnName varchar(128)) RETURNS int
    DETERMINISTIC
BEGIN
  DECLARE retVal int DEFAULT 0;

  select idrel INTO retVal FROM vw_relative_header_id WHERE csv_column = in_ColumnName LIMIT 1;
RETURN retVal;
END;;

DELIMITER ;