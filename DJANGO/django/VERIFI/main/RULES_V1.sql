-- all fields need to be verified having value and transformed (if needed as is dob to age)
-- outliers need to be excluded i.e. age > 4 (no toddlers identified as farmers)
-- potential issue: what if there is repeat data (i.e. a farmer has been entered more than once, this will throw off the average).

select * FROM rules;

SELECT
  AVG(age) AS AVERAGE_AGE,
  gender
FROM (SELECT
    FLOOR(DATEDIFF(NOW(), DATE(CSV_FIELD15)) / 365) AS age, -- operation (take date and intrepret as dob and determine age)
    CSV_FIELD26 AS gender
  FROM csv_import_results_parent0
  WHERE CSV_FIELD15 > ''        -- lookup from source_field_name to _age = csv_field15
  AND CSV_FIELD26 > ''          -- lookup from group_field_name = gender = csv_field26
  AND id > 1) a                 -- always exclude the first row as its the header
WHERE age > 4
GROUP BY gender;                -- lookup from group_field_name = gender = csv_field26

-- *************************************************************************************

-- plot yield by farm...
-- Input_Farm_ID = csv_field18
-- PGS_total_yield_daily = csv_field142


SELECT
  CSV_FIELD18 AS Input_Farm_ID,
  CAST(CSV_FIELD142 AS DECIMAL) AS PGS_total_yield_daily
FROM csv_import_results_parent0 cip0,
     csv_import_results_parent100 cip1
WHERE cip0.id = cip1.id
AND cip0.id > 1
AND CSV_FIELD18 > ''
AND CSV_FIELD142 > ''
ORDER BY 2 ASC;



