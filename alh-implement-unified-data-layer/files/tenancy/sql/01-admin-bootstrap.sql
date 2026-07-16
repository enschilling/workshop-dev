WHENEVER SQLERROR EXIT SQL.SQLCODE
SET DEFINE ON
SET VERIFY OFF
SET ECHO OFF
SET FEEDBACK ON
SET SERVEROUTPUT ON

DEFINE workshop_user = 'SEER_WORKSHOP'
DEFINE workshop_password = 'Replace_With_Strong_Password'

PROMPT Stage 1 of 6: Creating the workshop schemas and Database Actions user.
PROMPT Review and replace the workshop_password value before running this script.

CREATE USER seer_bronze NO AUTHENTICATION;
CREATE USER seer_silver NO AUTHENTICATION;
CREATE USER seer_gold NO AUTHENTICATION;

ALTER USER seer_bronze QUOTA UNLIMITED ON data;
ALTER USER seer_silver QUOTA UNLIMITED ON data;
ALTER USER seer_gold QUOTA UNLIMITED ON data;

CREATE USER &workshop_user IDENTIFIED BY "&workshop_password"
  DEFAULT TABLESPACE data
  TEMPORARY TABLESPACE temp;

ALTER USER &workshop_user QUOTA UNLIMITED ON data;

GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE MINING MODEL TO &workshop_user;
GRANT DWROLE TO &workshop_user;
GRANT DATA_TRANSFORM_USER TO &workshop_user;
GRANT ADPUSER TO &workshop_user;
GRANT EXECUTE ON DBMS_CLOUD TO &workshop_user;
GRANT EXECUTE ON DBMS_VECTOR TO &workshop_user;
GRANT EXECUTE ON DBMS_VECTOR_CHAIN TO &workshop_user;

BEGIN
  ORDS_ADMIN.ENABLE_SCHEMA(
    p_enabled             => TRUE,
    p_schema              => UPPER('&workshop_user'),
    p_url_mapping_type    => 'BASE_PATH',
    p_url_mapping_pattern => LOWER('&workshop_user'),
    p_auto_rest_auth      => TRUE
  );
END;
/

BEGIN
  DBMS_CLOUD_ADMIN.ENABLE_RESOURCE_PRINCIPAL();
  DBMS_CLOUD_ADMIN.ENABLE_RESOURCE_PRINCIPAL(username => UPPER('&workshop_user'));
END;
/

PROMPT Stage 1 complete: Workshop schemas, Database Actions user, and resource principal are enabled.
