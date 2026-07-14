# Unify the Data Layer with Oracle Autonomous AI Lakehouse

This repository contains the first-draft Oracle LiveLabs workshop **Unify the Data Layer with Oracle Autonomous AI Lakehouse**.

The workshop follows a 75-minute, three-lab structure:

1. Explore the Unified Lakehouse Foundation
2. Unify Data for AI Applications
3. Deliver Trusted Data Products

The attendee environment is expected to be pre-provisioned. Representative Fusion ERP, Primavera, CRM, and on-premises data is supplied as simulated source extracts. Contracts, engineering specifications, and inspection documents are stored in OCI Object Storage. The workshop does not require access to the source enterprise applications.

## Transformation approach

This workshop demonstrates an Autonomous AI Lakehouse-native implementation. Bronze, Silver, and Gold are created and maintained with ALH Data Studio, SQL, Data Transforms, and database-native jobs. AIDP remains part of the broader solution story, but AIDP notebooks do not execute this workshop's seeded transformations.

The complementary AIDP pattern is documented in the workshop: teams can use Spark-powered AIDP notebooks and workflows for distributed or notebook-centric processing, then publish selected products to ALH. The workshop presents the choice as workload-driven rather than positioning either approach as universally preferred.

## Workshop entry point

Open `workshops/tenancy/index.html` through the LiveLabs publishing workflow. The adjacent `manifest.json` defines the tutorial order and points to the shared Markdown files at the repository root.

## Draft data contracts

The first draft assumes these schemas and products:

- `SEER_BRONZE`: faithful source extracts and ingestion metadata
- `SEER_BRONZE.SUPPLIER_TRANSFORM_SAMPLE`: small hands-on transformation source
- `SEER_SILVER`: standardized and reconciled enterprise entities
- `SEER_SILVER.SUPPLIER_SOURCE_MAPPINGS`: seeded comparison result for the transformation exercise
- `SEER_GOLD`: governed, consumer-ready data products
- `SEER_GOLD.PROJECT_CONTEXT`
- `SEER_GOLD.SUPPLIER_RECOMMENDATIONS`
- `SEER_GOLD.SUPPLIER_PROFILE`
- `SEER_GOLD.DOCUMENT_CHUNKS`
- `SEER_GOLD.PIPELINE_RUN_SUMMARY` and `SEER_GOLD.PIPELINE_RUN_EVENTS`: workshop audit records for ALH pipeline execution
- `SEER_MEDALLION_PIPELINES`: prepared ALH Data Transforms project

The names are design contracts for the sample-data and environment build. They must be verified during implementation and end-to-end validation.

## Content status

This is a narrative and instructional first draft. Exact Autonomous AI Lakehouse UI labels, screenshots, SQL output, resource names, and timings must be validated against the final workshop environment before publication. Any AIDP screenshots or instructions should appear only in clearly labeled comparison or downstream-context material.
