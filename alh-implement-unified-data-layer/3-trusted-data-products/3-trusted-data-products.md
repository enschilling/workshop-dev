# Lab 3: Deliver Trusted Data Products

## Introduction

Reliable applications need more than a successful query. They need named products with clear owners, stable contracts, quality expectations, refresh schedules, lineage, and access controls. In this lab, Alex performs a final readiness review before Seer's data is handed to application developers and the team building the Construction Evaluation Agent.

You will inspect prebuilt ALH Data Transforms and database-job evidence and run short validation queries. You will not start a long ingestion or medallion rebuild. The workshop setup records selected job outcomes in `SEER_GOLD` audit tables so you can review the complete pipeline consistently; those audit tables are workshop assets, not built-in Oracle dictionary views.

**Estimated Time:** 20 minutes

### Objectives

In this lab, you will:

- Inspect the ALH Data Transforms workflows and database jobs that maintain the medallion layers.
- Validate quality, freshness, and document coverage.
- Review published data-product contracts.
- Map Gold products to developer and agent consumers.
- Complete an application and agent-readiness assessment.

### Prerequisites

- Completion of Labs 1 and 2
- Read access to ALH pipeline, quality, catalog, and product metadata
- No permission to modify production-like workshop pipelines is required

## Task 1: Inspect ALH-native operational pipelines

ALH can implement transformation logic with SQL, visual Data Transforms data flows, or a combination of both. Data Transforms workflows sequence data loads, data flows, variables, and other steps. Database jobs are useful when the transformation is most naturally expressed as SQL or PL/SQL.

1. In Database Actions, select **Data Studio**, and then select **Data Transforms**.

2. Open the prepared `SEER_MEDALLION_PIPELINES` project. Inspect the source, transformation, and target components without starting a full rebuild.

3. Locate the prepared Bronze-to-Silver and Silver-to-Gold flows. Identify where the design performs mappings, filters, joins, expressions, and target writes.

4. Return to the SQL worksheet and review the latest ALH pipeline executions recorded by the workshop setup:

    ```sql
    SELECT pipeline_name,
           execution_engine,
           pipeline_purpose,
           started_at,
           completed_at,
           run_status,
           records_read,
           records_written,
           records_quarantined
    FROM seer_gold.pipeline_run_summary
    ORDER BY started_at DESC;
    ```

5. Identify the ALH pipelines responsible for:

    - Ingesting representative source extracts
    - Registering Object Storage documents
    - Standardizing and reconciling Silver entities
    - Publishing Gold products
    - Refreshing chunks, embeddings, and vector indexes

6. Inspect failures or warnings without rerunning the pipeline:

    ```sql
    SELECT pipeline_run_id,
           pipeline_name,
           execution_engine,
           step_name,
           severity,
           message,
           recorded_at
    FROM seer_gold.pipeline_run_events
    WHERE severity IN ('WARNING', 'ERROR')
    ORDER BY recorded_at DESC;
    ```

7. A production pipeline should be restartable, observable, and idempotent. The ability to reproduce a Gold result matters as much as the result itself.

> **Where AIDP fits:** An AIDP implementation would expose notebook jobs and AIDP workflow runs instead. The operational responsibilities remain similar, but the execution engine and monitoring surface differ. This workshop inspects ALH-native execution because the transformations and target products are contained in ALH.

## Task 2: Validate the Gold products

1. Check stable business keys and duplicates:

    ```sql
    SELECT 'Missing project IDs' AS check_name, COUNT(*) AS failure_count
    FROM seer_gold.project_context
    WHERE project_id IS NULL
    UNION ALL
    SELECT 'Missing asset IDs', COUNT(*)
    FROM seer_gold.project_context
    WHERE asset_id IS NULL
    UNION ALL
    SELECT 'Duplicate project/asset rows', COUNT(*)
    FROM (
      SELECT project_id, asset_id
      FROM seer_gold.project_context
      GROUP BY project_id, asset_id
      HAVING COUNT(*) > 1
    );
    ```

2. Check product freshness:

    ```sql
    SELECT product_name,
           last_successful_refresh,
           freshness_sla_minutes,
           freshness_status
    FROM seer_gold.data_product_freshness
    ORDER BY product_name;
    ```

3. Check document and embedding coverage:

    ```sql
    SELECT document_type,
           COUNT(DISTINCT document_id) AS documents,
           COUNT(*) AS chunks,
           SUM(CASE WHEN embedding IS NULL THEN 1 ELSE 0 END) AS missing_embeddings
    FROM seer_gold.document_chunks
    GROUP BY document_type
    ORDER BY document_type;
    ```

4. Confirm that all required checks pass or have an explained exception. A result should not be labeled agent-ready merely because a query returns rows.

## Task 3: Review the published contracts

1. Open the product catalog:

    ```sql
    SELECT product_name,
           business_purpose,
           product_owner,
           classification,
           refresh_frequency,
           quality_status,
           contract_version
    FROM seer_gold.data_product_catalog
    ORDER BY product_name;
    ```

2. Inspect the contract columns for the project context product:

    ```sql
    SELECT column_sequence,
           column_name,
           business_definition,
           data_type,
           nullable_flag,
           sensitivity_label
    FROM seer_gold.data_product_columns
    WHERE product_name = 'PROJECT_CONTEXT'
    ORDER BY column_sequence;
    ```

3. Verify that the product describes:

    - Its business purpose and accountable owner
    - Stable keys and business definitions
    - Quality and freshness expectations
    - Sensitivity and access classification
    - Contract version and intended consumers

4. Cataloging makes a product discoverable. A contract makes it safe to depend on.

## Task 4: Map products to downstream consumers

The next workshops begin where this one ends.

| Governed asset | Developer or agent use |
| --- | --- |
| `SEER_GOLD.PROJECT_CONTEXT` | SQL tool `get_project_context` |
| `SEER_GOLD.SUPPLIER_RECOMMENDATIONS` | SQL tool `get_supplier_recommendations` |
| `SEER_GOLD.SUPPLIER_PROFILE` | SQL tool `get_supplier_profile` |
| Governed contracts and policy documents | Construction-policy RAG knowledge base |
| `DOCUMENT_CHUNKS` and vector index | Semantic and hybrid retrieval |
| Asset and supplier relationships | Graph or relationship-aware application queries |
| Quality, lineage, and classifications | Trust, audit, and access enforcement |

1. Review the consumer mapping stored in the environment:

    ```sql
    SELECT product_name,
           consumer_name,
           access_pattern,
           contract_version,
           approval_status
    FROM seer_gold.data_product_consumers
    ORDER BY product_name, consumer_name;
    ```

2. Identify the four data patterns developers encounter in the AppDev Data Fundamentals lab:

    - Relational joins for governed facts
    - JSON access for flexible attributes
    - Relationship traversal for connected context
    - Vector retrieval for semantic evidence

3. Notice the division of responsibility. Data engineers publish reliable products and evidence. Developers build application behavior against those contracts. Agent builders assemble tools and instructions without rebuilding the underlying data foundation.

## Task 5: Complete the readiness assessment

Use the following checklist for each product intended for an AI application or agent.

| Readiness question | Evidence to review |
| --- | --- |
| Are identifiers stable and unique? | Key and duplicate checks |
| Are business terms defined? | Product and column definitions |
| Is source evidence traceable? | Record and document lineage |
| Is sensitive data classified? | Sensitivity labels and access policy |
| Are quality thresholds explicit? | Quality rules and latest results |
| Is freshness measurable? | Refresh schedule and freshness status |
| Are failures recoverable? | Workflow events, quarantine, and restart behavior |
| Is semantic retrieval evaluated? | Search test set, ranking results, and document coverage |
| Can consumers tolerate contract changes? | Contract version and change policy |
| Is an accountable owner named? | Product catalog ownership |

1. Review the environment's consolidated assessment:

    ```sql
    SELECT product_name,
           identifiers_ready,
           quality_ready,
           freshness_ready,
           lineage_ready,
           security_ready,
           retrieval_ready,
           overall_readiness
    FROM seer_gold.ai_readiness_assessment
    ORDER BY product_name;
    ```

2. Identify any product that is not `READY` and review the reason before it is exposed to a downstream consumer.

3. Confirm that the three SQL products and the governed document collection are ready for the Construction Evaluation Agent workshop.

## Lab 3 Recap

In this lab, you:

- Inspected ALH Data Transforms workflows, database jobs, and workshop pipeline-audit records.
- Validated business keys, freshness, quality, and document coverage.
- Reviewed product ownership, classifications, and contract versions.
- Mapped Gold products to developer interfaces and agent tools.
- Completed an application and agent-readiness assessment.

The key takeaway is that Gold is not simply the last transformation step. It is the governed interface between data producers and consumers.

## Learn More

- [Discover and Manage Data with Catalog in Autonomous AI Database](https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/catalog-entities.html)
- [Transform Data with Data Transforms in Autonomous AI Database](https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/autonomous-data-transforms.html)
- [Oracle Autonomous Database security](https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/security-autonomous-database.html)

## Acknowledgements

- **Author:** Eli Schilling, Cloud Architect || Evangelist
- **Contributors:** Oracle LiveLabs and ONA Lab Experience Teams
- **Last Updated By / Date:** ONA Lab Experience team, July 2026
