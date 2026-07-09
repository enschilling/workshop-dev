# Lab 1: Explore the Unified Lakehouse Foundation

## Introduction

Alex has an approved business ontology, but an ontology alone does not make source data trustworthy. The underlying records still arrive with different identifiers, formats, quality levels, and update schedules. In this lab, you will inspect the representative source feeds prepared for Seer Construction Group and follow them through a prebuilt Bronze, Silver, and Gold medallion architecture.

The workshop uses simulated extracts from enterprise systems because the LiveLabs environment does not connect to live Fusion ERP, Primavera, CRM, or on-premises applications. OCI Object Storage and Oracle Autonomous AI Lakehouse are the real services used to store, organize, and query the workshop data.

**Estimated Time:** 20 minutes

### Objectives

In this lab, you will:

- Verify that the pre-provisioned workshop schemas and data are available.
- Inspect representative structured feeds and unstructured project documents.
- Explain what belongs in Bronze, Silver, and Gold.
- Trace a steel-delivery business event across multiple source extracts.
- Review data quality, reconciliation, and lineage evidence.

### Prerequisites

- Completion of the **Get Started** section
- Access to Database Actions or the SQL worksheet supplied with the environment
- Read access to `SEER_BRONZE`, `SEER_SILVER`, and `SEER_GOLD`
- Read access to the workshop Object Storage bucket or its registered catalog entries

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

## Task 2: Explore the representative source feeds

The Bronze layer preserves what arrived from each source, including the source's original identifiers and extraction metadata.

1. Review the source inventory:

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

2. Identify the representative feeds:

    - Fusion ERP-style purchase orders and financial assets
    - Primavera-style projects, activities, and milestones
    - CRM-style suppliers, contacts, and qualifications
    - On-premises-style inspections and compliance findings
    - Contracts, specifications, and inspection documents in OCI Object Storage

3. Inspect a sample of raw purchase orders:

    ```sql
    SELECT source_record_id,
           po_number,
           project_reference,
           supplier_reference,
           description,
           amount,
           currency_code,
           extracted_at
    FROM seer_bronze.erp_purchase_orders
    FETCH FIRST 10 ROWS ONLY;
    ```

4. Inspect the unstructured-document registry:

    ```sql
    SELECT document_name,
           document_type,
           object_uri,
           project_reference,
           asset_reference,
           version_label,
           source_modified_at
    FROM seer_bronze.document_registry
    ORDER BY document_type, document_name;
    ```

5. Notice that Bronze records retain source-specific identifiers. Bronze preserves evidence and replayability; it is not the layer applications should use as a stable business contract.

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

## Task 4: Trace the Austin steel-delivery event

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

## Task 5: Review quality and lineage evidence

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
           workflow_run_id,
           completed_at
    FROM seer_gold.lineage_summary
    WHERE target_object = 'SEER_GOLD.PROJECT_CONTEXT'
    ORDER BY completed_at DESC, source_object;
    ```

4. Confirm that the Gold product can be traced to its Silver entities, Bronze records, and original documents or files.

## Lab 1 Recap

In this lab, you:

- Verified the pre-provisioned lakehouse environment.
- Explored simulated enterprise feeds and actual Object Storage document metadata.
- Compared the responsibilities of Bronze, Silver, and Gold.
- Traced the Austin steel-delivery event across source systems.
- Reviewed quality, quarantine, reconciliation, and lineage evidence.

The key takeaway is that connecting sources is only the beginning. Trusted AI context requires explicit contracts, reconciliation, and provenance.

## Learn More

- [Use external tables with Autonomous Database](https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/query-external-data.html)
- [OCI Object Storage documentation](https://docs.oracle.com/en-us/iaas/Content/Object/home.htm)

## Acknowledgements

- **Author:** Oracle AI Data Platform and Autonomous AI Lakehouse Workshop Team
- **Contributors:** Oracle LiveLabs, database, analytics, and AI data platform teams
- **Last Updated By/Date:** Workshop development team, July 2026

