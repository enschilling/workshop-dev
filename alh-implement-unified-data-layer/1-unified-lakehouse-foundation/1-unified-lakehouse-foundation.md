# Lab 1: Explore the Unified Lakehouse Foundation

## Introduction

Alex has an approved business ontology, but an ontology alone does not make source data trustworthy. The underlying records still arrive with different identifiers, formats, quality levels, and update schedules. In this lab, you will inspect the representative source feeds prepared for Seer Construction Group and follow them through a prebuilt Bronze, Silver, and Gold medallion architecture implemented inside ALH.

The workshop uses simulated extracts from enterprise systems because the LiveLabs environment does not connect to live Fusion ERP, Primavera, CRM, or on-premises applications. OCI Object Storage and Oracle Autonomous AI Lakehouse are the real services used to store, organize, and query the workshop data.

AIDP could perform equivalent transformations with Spark notebooks and workflows. In this workshop, ALH is both the transformation environment and the serving layer. You will prove that boundary by using Data Studio to link an Object Storage CSV as a Bronze external table and then running a small Bronze-to-Silver SQL transformation directly in ALH.

**Estimated Time:** 25 minutes

### Objectives

In this lab, you will:

- Verify that the pre-provisioned workshop schemas and data are available.
- Create a Bronze external table over a CSV in OCI Object Storage using the Data Studio interface.
- Inspect representative structured feeds and unstructured project documents.
- Run a representative Bronze-to-Silver transformation inside ALH.
- Explain what belongs in Bronze, Silver, and Gold.
- Trace a steel-delivery business event across multiple source extracts.
- Review data quality, reconciliation, and lineage evidence.

### Prerequisites

- Completion of the **Get Started** section
- The `workshop_username` and `workshop_user_password` values from the Terraform outputs
- Access to Database Actions and Data Studio for the Autonomous AI Lakehouse
- Read access to `SEER_BRONZE`, `SEER_SILVER`, and `SEER_GOLD`
- A database resource principal with read access to the workshop Object Storage bucket
- `DWROLE` and permission to create a table and view in your assigned workshop schema

> **Note:** Object names in this first draft establish the environment contract. The setup package and final guide must be validated together before publication.

## Task 1: Verify the workshop environment

The environment was built before the workshop. Begin with a short readiness check so later exercises fail early and clearly if a required asset is missing.

1. Open the SQL worksheet provided for your Autonomous AI Lakehouse instance.

2. Run the following query to confirm your connected database user:

    ```sql
    SELECT USER AS connected_user FROM dual;
    ```

3. Confirm that the three medallion schemas are visible:

    ```sql
    SELECT owner, COUNT(*) AS object_count
    FROM all_objects
    WHERE owner IN ('SEER_BRONZE', 'SEER_SILVER', 'SEER_GOLD')
      AND object_type IN ('TABLE', 'VIEW')
    GROUP BY owner
    ORDER BY owner;
    ```

4. Confirm that the workshop contains source data, conformed entities, Gold products, and document chunks:

    ```sql
    SELECT 'Bronze source records' AS asset, COUNT(*) AS row_count
    FROM seer_bronze.source_record_inventory
    UNION ALL
    SELECT 'Silver assets', COUNT(*)
    FROM seer_silver.assets
    UNION ALL
    SELECT 'Gold project context', COUNT(*)
    FROM seer_gold.project_context
    UNION ALL
    SELECT 'Searchable document chunks', COUNT(*)
    FROM seer_gold.document_chunks;
    ```

5. Verify that every result contains at least one row. If an object is missing, stop and use the **Need Help?** section before continuing.

## Task 2: Link an Object Storage CSV as a Bronze external table

The workshop setup uploaded representative source extracts to a private Object Storage bucket. In this task, you will use the Autonomous AI Database Data Studio interface to link one CSV without copying it into a managed database table. The resulting external table is the Bronze source for your hands-on transformation.

1. Return to the Database Actions Launchpad, select **Data Studio**, and then select **Data Load**.

2. In the Data Load navigation, select **Connections**.

3. Select **Create**, and then select **New Cloud Store Location**.

4. Configure the cloud store location:

    - **Name:** `SEER_LAKE_SOURCE`
    - **Credential:** `OCI$RESOURCE_PRINCIPAL`
    - **Cloud Store:** Oracle Cloud Infrastructure Object Storage
    - **Bucket URI:** Use the `object_storage_base_uri` value from the Terraform outputs.

    The environment setup has already enabled the resource principal for your database user and granted it read access to this private bucket. You do not need an OCI username, auth token, or signing key.

5. Select **Next**, confirm that the cloud data location is reachable, and select **Create**.

6. From the Data Load navigation, select **Link Data**, and then select **Cloud Store**.

    > **Link rather than load:** **Link Data** leaves the CSV in Object Storage and creates an external table. **Load Data** would copy the rows into a managed database table.

7. Select `SEER_LAKE_SOURCE`, browse to `source-data/suppliers`, and drag `supplier_extract.csv` into the data link cart.

8. On the file card, select **Settings** and configure the link:

    - **Table name:** `SUPPLIER_TRANSFORM_EXT`
    - **Validation Type:** Full
    - **Encoding:** UTF-8
    - **Text enclosure:** Double quote
    - **Field delimiter:** Comma
    - **Start processing data at row:** `0`
    - **Column header row:** Selected
    - **Partition column:** None
    - **Use Wildcard:** Not selected

9. In **Mapping**, retain the source-aligned columns. This is a Bronze asset, so do not standardize names, statuses, certifications, or locations yet.

10. Select **Include** for the optional `FILE$NAME` and `SYSTIMESTAMP` source columns. Rename the corresponding target columns:

    - `FILE$NAME` to `SOURCE_FILE_NAME`
    - `SYSTIMESTAMP` to `LINKED_AT`

    These columns preserve file-level provenance and the time at which the external data was linked.

11. Review **Preview** to confirm the header and CSV fields were interpreted correctly. Review **Table** to inspect the proposed external-table shape.

12. Open **SQL** and review the database commands Data Studio will generate. You do not need to copy or run them manually.

13. Select **Close**, select **Start** in the data link cart, and wait for the job to complete.

14. Open the completed job and review **Job Report**. Confirm that the rows were processed successfully and no rows were rejected.

15. Return to the SQL worksheet and query the external table you created:

    ```sql
    SELECT source_record_id,
           supplier_name,
           source_status,
           certification,
           location,
           source_system,
           ingestion_batch_id,
           source_file_name,
           linked_at
    FROM supplier_transform_ext
    ORDER BY source_record_id;
    ```

16. Review the broader seeded source inventory:

    ```sql
    SELECT source_system,
           source_object,
           storage_format,
           record_count,
           extracted_at,
           ingestion_batch_id
    FROM seer_bronze.source_record_inventory
    ORDER BY source_system, source_object;
    ```

17. The other representative feeds include Fusion ERP-style purchasing and financial data, Primavera-style milestones, on-premises-style inspection findings, and PDF project evidence in the same Object Storage bucket. Bronze preserves what arrived, including source identifiers and provenance; it is not the stable contract applications should consume.

## Task 3: Compare Bronze, Silver, and Gold

The medallion layers answer different questions.

| Layer | Primary question | Typical controls |
| --- | --- | --- |
| Bronze | What arrived from the source? | Provenance, ingestion time, raw payload retention |
| Silver | What enterprise entity does it represent? | Standardization, validation, deduplication, reconciliation |
| Gold | What trusted product does a consumer need? | Business definitions, stable schema, quality and freshness expectations |

1. Inspect the Silver asset representation:

    ```sql
    SELECT asset_id,
           canonical_asset_name,
           project_id,
           asset_type,
           normalized_status,
           source_system_count,
           reconciliation_status
    FROM seer_silver.assets
    ORDER BY project_id, canonical_asset_name;
    ```

2. Compare supplier names and statuses after standardization:

    ```sql
    SELECT supplier_id,
           canonical_supplier_name,
           qualification_status,
           compliance_status,
           matched_source_count
    FROM seer_silver.suppliers
    ORDER BY canonical_supplier_name;
    ```

3. Inspect the Gold project context product:

    ```sql
    SELECT project_name,
           asset_name,
           current_milestone,
           committed_cost,
           inspection_status,
           primary_supplier,
           data_freshness_at
    FROM seer_gold.project_context
    ORDER BY project_name, asset_name;
    ```

4. Observe that the Gold result presents business concepts rather than source-system mechanics. Consumers do not need to know which record came from which source to use the product, but provenance remains available for audit and explanation.

## Task 4: Run an ALH-native Bronze-to-Silver transformation

The complete production-style medallion architecture is seeded, but the external table you just linked lets you execute one representative transformation yourself. You will standardize its deliberately inconsistent supplier data with database-native SQL and compare your result with the seeded Silver mapping.

1. Inspect the sample Bronze records:

    ```sql
    SELECT source_record_id,
           supplier_name,
           source_status,
           certification,
           location,
           source_system,
           ingestion_batch_id
    FROM supplier_transform_ext
    ORDER BY source_record_id;
    ```

2. Identify differences such as extra spaces, abbreviations, inconsistent case, status codes, and missing certifications.

3. Create a standardized view in your assigned workshop schema:

    ```sql
    CREATE OR REPLACE VIEW supplier_standardized_demo AS
    SELECT source_record_id,
           CASE
             WHEN UPPER(TRIM(supplier_name)) IN (
                    'ATLAS STRUCTURAL FAB.',
                    'ATLAS STRUCTURAL FABRICATION'
                  )
             THEN 'Atlas Structural Fabrication'
             ELSE INITCAP(TRIM(supplier_name))
           END AS canonical_supplier_name,
           CASE UPPER(TRIM(source_status))
             WHEN 'A' THEN 'APPROVED'
             WHEN 'APPROVED' THEN 'APPROVED'
             WHEN 'PENDING_INFO' THEN 'REQUEST_INFORMATION'
             ELSE 'REVIEW_REQUIRED'
           END AS qualification_status,
           CASE
             WHEN certification IS NULL THEN 'MISSING'
             WHEN UPPER(certification) LIKE '%AISC%' THEN 'AISC'
             ELSE UPPER(TRIM(certification))
           END AS normalized_certification,
           REPLACE(
             UPPER(TRIM(location)),
             ', TEXAS',
             ', TX'
           ) AS normalized_location,
           source_system,
           ingestion_batch_id,
           source_file_name,
           linked_at
    FROM supplier_transform_ext;
    ```

4. Query your transformed result:

    ```sql
    SELECT *
    FROM supplier_standardized_demo
    ORDER BY canonical_supplier_name, source_record_id;
    ```

5. Compare the standardized name, status, certification, and location with the seeded Silver mapping:

    ```sql
    SELECT demo.source_record_id,
           demo.canonical_supplier_name AS attendee_result,
           silver.canonical_supplier_name AS seeded_silver_result,
           CASE
             WHEN demo.canonical_supplier_name = silver.canonical_supplier_name
              AND demo.qualification_status = silver.qualification_status
              AND demo.normalized_certification = silver.normalized_certification
              AND demo.normalized_location = silver.normalized_location
             THEN 'MATCH'
             ELSE 'REVIEW'
           END AS validation_status
    FROM supplier_standardized_demo demo
    JOIN seer_silver.supplier_source_mappings silver
      ON silver.source_record_id = demo.source_record_id
    ORDER BY demo.source_record_id;
    ```

6. Confirm that the expected rows return `MATCH`. Notice that the view retains the source record, ingestion batch, source file, and link timestamp needed for provenance.

7. Your SQL standardized individual records. The seeded Silver pipeline also performs cross-source entity matching, survivorship, validation, and quarantine. Standardization is an important transformation step, but it is not the entire reconciliation process.

> **ALH Data Transforms alternative:** You used SQL because this rule is concise and easy to validate. ALH Data Transforms can represent the same pattern visually with source, expression, mapping, validation, and target components. It also provides reusable connections, workflows, scheduling, and job monitoring. The full seeded pipeline may use SQL, Data Transforms, or both according to the needs of each step.

## Task 5: Trace the Austin steel-delivery event

The reinforced-steel framework for Seer's Austin bank project appears differently in each source. Use the cross-source mapping to follow the shared business event.

1. Locate the source records associated with the Austin steel delivery:

    ```sql
    SELECT source_system,
           source_object,
           source_record_id,
           source_description,
           canonical_event_id,
           match_method,
           match_confidence
    FROM seer_silver.source_record_mappings
    WHERE UPPER(canonical_business_term) = 'STEEL DELIVERY'
      AND UPPER(project_name) LIKE '%AUSTIN%'
    ORDER BY source_system, source_object;
    ```

2. Confirm that the mapping includes financial, schedule, supplier, and inspection context.

3. Open the canonical event:

    ```sql
    SELECT event_id,
           project_name,
           asset_name,
           event_type,
           planned_date,
           actual_date,
           supplier_name,
           financial_status,
           inspection_status
    FROM seer_silver.project_events
    WHERE event_id = (
      SELECT canonical_event_id
      FROM seer_silver.source_record_mappings
      WHERE UPPER(canonical_business_term) = 'STEEL DELIVERY'
        AND UPPER(project_name) LIKE '%AUSTIN%'
      FETCH FIRST 1 ROW ONLY
    );
    ```

4. Review the corresponding Gold record:

    ```sql
    SELECT project_name,
           asset_name,
           supplier_name,
           milestone_status,
           purchase_order_status,
           inspection_status,
           decision_readiness
    FROM seer_gold.project_context
    WHERE UPPER(project_name) LIKE '%AUSTIN%'
      AND UPPER(asset_name) LIKE '%STEEL%';
    ```

5. The Gold product does not erase source differences. It resolves them into a stable business object while preserving the mappings needed to explain the result.

## Task 6: Review quality and lineage evidence

Data should advance only when it satisfies the contract for the next layer.

1. Review the latest quality-rule results:

    ```sql
    SELECT layer_name,
           rule_name,
           rule_dimension,
           records_evaluated,
           records_failed,
           status,
           evaluated_at
    FROM seer_gold.data_quality_results
    ORDER BY evaluated_at DESC, layer_name, rule_name;
    ```

2. Review quarantined records without changing them:

    ```sql
    SELECT source_system,
           source_record_id,
           failed_rule,
           failure_reason,
           quarantine_status
    FROM seer_silver.quarantined_records
    ORDER BY source_system, source_record_id;
    ```

3. Inspect the lineage for the Austin project context product:

    ```sql
    SELECT target_object,
           source_object,
           transformation_name,
           pipeline_run_id,
           completed_at
    FROM seer_gold.lineage_summary
    WHERE target_object = 'SEER_GOLD.PROJECT_CONTEXT'
    ORDER BY completed_at DESC, source_object;
    ```

4. Confirm that the Gold product can be traced to its Silver entities, Bronze records, and original documents or files.

## Lab 1 Recap

In this lab, you:

- Verified the pre-provisioned lakehouse environment.
- Used Data Studio to link an Object Storage CSV as the attendee-created Bronze external table `SUPPLIER_TRANSFORM_EXT`.
- Explored simulated enterprise feeds and actual Object Storage document metadata.
- Created the Silver demonstration view `SUPPLIER_STANDARDIZED_DEMO` directly in ALH.
- Compared the responsibilities of Bronze, Silver, and Gold.
- Traced the Austin steel-delivery event across source systems.
- Reviewed quality, quarantine, reconciliation, and lineage evidence.

The key takeaway is that connecting sources is only the beginning. Trusted AI context requires explicit contracts, reconciliation, and provenance.

## Learn More

- [Use external tables with Autonomous Database](https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/query-external-data.html)
- [Link to objects in cloud storage with Data Studio](https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/link-to-cloud.html)
- [Transform Data with Data Transforms in Autonomous AI Database](https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/autonomous-data-transforms.html)
- [OCI Object Storage documentation](https://docs.oracle.com/en-us/iaas/Content/Object/home.htm)

## Acknowledgements

- **Author:** Eli Schilling, Cloud Architect || Evangelist
- **Contributors:** Oracle LiveLabs and ONA Lab Experience Teams
- **Last Updated By / Date:** ONA Lab Experience team, July 2026
