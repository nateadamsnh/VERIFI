-- 
-- Set character set the client will use to send SQL statements to the server
--
SET NAMES 'utf8';

--
-- Set default database
--
USE verifi_main;

--
-- Drop table `users`
--
DROP TABLE IF EXISTS users;

--
-- Set default database
--
USE verifi_main;

--
-- Create table `users`
--
CREATE TABLE users (
  id int UNSIGNED NOT NULL AUTO_INCREMENT,
  user_name varchar(50) NOT NULL,
  first_name varchar(50) NOT NULL,
  last_name varchar(50) NOT NULL, 
  password varchar(1023) NOT NULL,
  role_id int NOT NULL,
  uid varchar(1023) NOT NULL,
  PRIMARY KEY (id)
)
ENGINE = INNODB,
AUTO_INCREMENT = 2,
CHARACTER SET utf8mb4,
COLLATE utf8mb4_0900_ai_ci,
ROW_FORMAT = DYNAMIC;


INSERT INTO users (user_name, password, first_name, last_name, role_id, uid) VALUES ('nateadams', 'x', 'Nate', 'Adams',  1, uuid());

-- select * FROM user_roles;

drop TABLE IF exists user_roles;
CREATE TABLE user_roles (
  id int UNSIGNED NOT NULL AUTO_INCREMENT,
  role_name varchar(63) NOT NULL,
  PRIMARY KEY (id)
);

INSERT INTO user_roles (role_name) VALUES ('provider');
INSERT INTO user_roles (role_name) VALUES ('consumer');
INSERT INTO user_roles (role_name) VALUES ('administrator');
INSERT INTO user_roles (role_name) VALUES ('arbitrator');



DROP TABLE IF EXISTS permission_items;
CREATE TABLE permission_items (
id int UNSIGNED NOT NULL AUTO_INCREMENT,
permission_item varchar(63) NOT NULL,
PRIMARY KEY (id)
);

insert INTO permission_items (permission_item) VALUES ('Administration');
insert INTO permission_items (permission_item) VALUES ('Dashboard');
insert INTO permission_items (permission_item) VALUES ('Settings'); 
insert INTO permission_items (permission_item) VALUES ('Reports'); 
insert INTO permission_items (permission_item) VALUES ('Transactions');
insert INTO permission_items (permission_item) VALUES ('Data');


DROP TABLE IF EXISTS role_permissions;
CREATE TABLE role_permissions (
  id int UNSIGNED NOT NULL AUTO_INCREMENT,
  role_id int NOT NULL,
  permission_item_id int NOT NULL,
  PRIMARY KEY (id)
  );

INSERT INTO role_permissions (role_id, permission_item_id) VALUES (1, 2);
INSERT INTO role_permissions (role_id, permission_item_id) VALUES (1, 3);
INSERT INTO role_permissions (role_id, permission_item_id) VALUES (1, 4);
INSERT INTO role_permissions (role_id, permission_item_id) VALUES (1, 5);
INSERT INTO role_permissions (role_id, permission_item_id) VALUES (1, 6);

INSERT INTO role_permissions (role_id, permission_item_id) VALUES (2, 2);
INSERT INTO role_permissions (role_id, permission_item_id) VALUES (2, 3);


INSERT INTO role_permissions (role_id, permission_item_id) VALUES (3, 1);
INSERT INTO role_permissions (role_id, permission_item_id) VALUES (3, 2);
INSERT INTO role_permissions (role_id, permission_item_id) VALUES (3, 3);
INSERT INTO role_permissions (role_id, permission_item_id) VALUES (3, 4);
INSERT INTO role_permissions (role_id, permission_item_id) VALUES (3, 5);


drop table IF EXISTS uploaded_documents;
CREATE TABLE uploaded_documents (
id int UNSIGNED NOT NULL AUTO_INCREMENT,
file_name varchar(1023) NOT NULL,
file_path varchar(1023) NOT NULL,
document longblob NOT NULL,
uploaded_by_uid varchar(1023) not null, 
date_added datetime DEFAULT NOW(),
status varchar(31) DEFAULT 'uploaded',
PRIMARY KEY (id)
) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci ENGINE=INNODB;


-- select document FROM uploaded_documents;

DROP PROCEDURE IF EXISTS sp_User_Get_MainPermissions;
delimiter ;;
CREATE PROCEDURE sp_User_Get_MainPermissions(IN in_Uid varchar(1021))
BEGIN
  
  SELECT 
  pi.permission_item AS permission_item
  FROM
  users u, user_roles ur, role_permissions rp, permission_items pi 
  WHERE
  u.role_id = ur.id
  AND rp.role_id = ur.id
  AND pi.id = rp.permission_item_id
  AND u.uid = in_Uid;

END
;;
DELIMITER ;




-- CALL sp_User_Get_MainPermissions('f0fc98bc-8ec5-11ee-9fc4-7c10c9456023');

DROP PROCEDURE IF EXISTS sp_User_Insert_Get_FilesUploaded;
delimiter ;;
CREATE PROCEDURE sp_User_Insert_Get_FilesUploaded(IN in_Uid varchar(1021), IN in_File_Name varchar(1023), IN in_File_Path varchar(1023), IN in_Document longblob)
BEGIN
  
  IF NOT ISNULL(in_Document) then
    insert into uploaded_documents (file_name, file_path, document, uploaded_by_uid) values (in_File_Name, in_File_Path, in_Document, in_Uid);
  END IF;


  SELECT
    file_name,
    date_added,
    status
  FROM
    uploaded_documents
  WHERE
    uploaded_by_uid = in_Uid;

END
;;
DELIMITER ;

DROP TABLE IF EXISTS questions;
CREATE TABLE questions (
id int UNSIGNED NOT NULL AUTO_INCREMENT,
question_src_id int NOT NULL,
question_text varchar(1023) NOT NULL,
question_description varchar(1023) NULL,
PRIMARY KEY (id)
);

-- INSERT INTO questions (question_src_id, question_text, question_description) SELECT csv_field1, csv_field6, ' ' FROM csv_questions_table WHERE csv_field6 > '';



-- select * FROM csv_questions_table;

-- select * FROM questions;

-- holds the questions to source data (csv or otherwise) associations..
-- to be used as the source for the rules map
DROP table IF EXISTS questions_data_map;
CREATE TABLE questions_data_map (
id int UNSIGNED NOT NULL AUTO_INCREMENT,
rule_definition_id int NULL,
data_map_group_id int NOT NULL DEFAULT 0,
questions_id int NOT NULL,
data_source_id int NOT NULL default 0,
data_column_position int NOT NULL,
PRIMARY KEY (id)
);

INSERT INTO questions_data_map (rule_definition_id, questions_id, 

drop TABLE IF EXISTS rule_definitions;
CREATE TABLE rule_definitions (
id int UNSIGNED NOT NULL AUTO_INCREMENT,
rule_description varchar(1023) NOT NULL,  -- what the rule does, i.e. avg of a species per collective.
rule varchar(1023) NOT NULL,       -- contains the aggregate, i.e. AVG, SUM, etc.
rule_filter varchar(1023) NULL, -- contains the filter for the rule (i.e. species)
rule_group  varchar(1023) NULL, -- contains what to group on (i.e. plot, collective, etc)
PRIMARY KEY (id)
);



-- sp_Get_SurveyQuestions

DROP PROCEDURE IF EXISTS sp_Get_SurveyQuestions;
delimiter ;;
CREATE PROCEDURE sp_Get_SurveyQuestions()
BEGIN
  
  SELECT id, question_text, question_description FROM questions;

END
;;
DELIMITER ;

-- CALL sp_Get_SurveyQuestions();

DROP PROCEDURE IF EXISTS sp_Get_SurveyHeader;
delimiter ;;
CREATE PROCEDURE sp_Get_SurveyHeader()
BEGIN
  
  SELECT id, csv_column FROM csv_header;

END
;;
DELIMITER ;


select * FROM users;

-- UPDATE users set role_id = 3; -- administrator
UPDATE users set role_id = 1; -- provider
-- UPDATE users set role_id = 2; -- consumer


select * FROM csv_header ch;