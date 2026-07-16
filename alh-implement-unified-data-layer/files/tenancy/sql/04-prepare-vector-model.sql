WHENEVER SQLERROR EXIT SQL.SQLCODE
SET DEFINE ON
SET VERIFY OFF
SET ECHO OFF
SET FEEDBACK ON

DEFINE workshop_user = 'SEER_WORKSHOP'

PROMPT Stage 4 of 6: Preparing directory access and temporary privileges for the vector model.

CREATE OR REPLACE DIRECTORY onnx_dir AS 'onnx_model';
GRANT READ, WRITE ON DIRECTORY onnx_dir TO &workshop_user;
GRANT SELECT, UPDATE ON seer_gold.document_chunks TO &workshop_user;

PROMPT Stage 4 complete: Vector model directory and temporary document-chunk privileges are prepared.
