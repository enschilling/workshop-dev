WHENEVER SQLERROR EXIT SQL.SQLCODE
SET DEFINE ON
SET VERIFY OFF
SET ECHO OFF
SET FEEDBACK ON

DEFINE workshop_user = 'SEER_WORKSHOP'

PROMPT Stage 6 of 6: Creating the vector index, granting read access, and validating the environment.

CREATE VECTOR INDEX seer_gold.document_chunks_hnsw_idx
  ON seer_gold.document_chunks (embedding)
  ORGANIZATION INMEMORY NEIGHBOR GRAPH
  DISTANCE COSINE
  WITH TARGET ACCURACY 95;

BEGIN
  FOR t IN (
    SELECT owner, table_name
    FROM all_tables
    WHERE owner IN ('SEER_BRONZE', 'SEER_SILVER', 'SEER_GOLD')
  ) LOOP
    EXECUTE IMMEDIATE
      'GRANT SELECT ON ' || DBMS_ASSERT.ENQUOTE_NAME(t.owner) || '.' ||
      DBMS_ASSERT.ENQUOTE_NAME(t.table_name) || ' TO ' ||
      DBMS_ASSERT.ENQUOTE_NAME(UPPER('&workshop_user'));
  END LOOP;
END;
/

SELECT owner, object_type, COUNT(*) AS object_count
FROM all_objects
WHERE owner IN ('SEER_BRONZE', 'SEER_SILVER', 'SEER_GOLD')
  AND object_type IN ('TABLE', 'INDEX')
GROUP BY owner, object_type
ORDER BY owner, object_type;

SELECT 'DOCUMENT_EMBEDDINGS' AS validation_name,
       CASE WHEN COUNT(*) > 0 AND COUNT(embedding) = COUNT(*) THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS checked_rows
FROM seer_gold.document_chunks
UNION ALL
SELECT 'GOLD_PRODUCTS', CASE WHEN COUNT(*) >= 4 THEN 'PASS' ELSE 'FAIL' END, COUNT(*)
FROM seer_gold.data_product_catalog
UNION ALL
SELECT 'VECTOR_MODEL', CASE WHEN COUNT(*) = 1 THEN 'PASS' ELSE 'FAIL' END, COUNT(*)
FROM all_mining_models
WHERE owner = UPPER('&workshop_user') AND model_name = 'ALL_MINILM_L12_V2';

PROMPT Stage 6 complete: Workshop grants, vector index, and readiness checks are complete.
