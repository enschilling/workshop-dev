WHENEVER SQLERROR EXIT SQL.SQLCODE
SET DEFINE ON
SET VERIFY OFF
SET FEEDBACK ON

DEFINE source_password = 'Replace_With_Strong_Password'

CREATE USER seer_source IDENTIFIED BY "&source_password"
  DEFAULT TABLESPACE data
  TEMPORARY TABLESPACE temp;
ALTER USER seer_source QUOTA UNLIMITED ON data;
GRANT CREATE SESSION, CREATE TABLE TO seer_source;

CREATE TABLE seer_source.inspection_compliance (
  inspection_number   VARCHAR2(30) PRIMARY KEY,
  project_reference   VARCHAR2(40) NOT NULL,
  asset_reference     VARCHAR2(40) NOT NULL,
  compliance_area     VARCHAR2(80) NOT NULL,
  result_status       VARCHAR2(30) NOT NULL,
  finding_description VARCHAR2(500),
  inspected_at        TIMESTAMP WITH TIME ZONE NOT NULL
);

INSERT ALL
  INTO seer_source.inspection_compliance VALUES ('INS-55091','AUS-BANK-01','FIELD-AST-STL-01','MATERIAL_TRACEABILITY','PASS','Mill certificates and member markings verified',TIMESTAMP '2026-07-09 18:20:00 UTC')
  INTO seer_source.inspection_compliance VALUES ('INS-55103','AUS-BANK-01','FIELD-AST-STL-01','BOLT_INSTALLATION','PASS','Bolt lot and tensioning records accepted',TIMESTAMP '2026-07-11 19:10:00 UTC')
  INTO seer_source.inspection_compliance VALUES ('INS-44190','HOU-MIXED-02','FIELD-AST-POD-02','SUPPLIER_CERTIFICATION','REQUEST_INFO','Updated AISC certificate required before release',TIMESTAMP '2026-07-10 16:45:00 UTC')
  INTO seer_source.inspection_compliance VALUES ('INS-33210','HAR-SEISMIC-03','FIELD-AST-BRC-03','WELD_PROCEDURE','FAIL','Seismic demand-critical weld qualification is incomplete',TIMESTAMP '2026-07-12 21:15:00 UTC')
SELECT 1 FROM dual;
COMMIT;

SELECT result_status, COUNT(*) AS inspection_count
FROM seer_source.inspection_compliance
GROUP BY result_status
ORDER BY result_status;

PROMPT Remote inspection source is ready.
