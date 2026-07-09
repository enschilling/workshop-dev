# Unify the Data Layer with Oracle Autonomous AI Lakehouse

This repository contains the first-draft Oracle LiveLabs workshop **Unify the Data Layer with Oracle Autonomous AI Lakehouse**.

The workshop follows a 75-minute, three-lab structure:

1. Explore the Unified Lakehouse Foundation
2. Unify Data for AI Applications
3. Deliver Trusted Data Products

The attendee environment is expected to be pre-provisioned. Representative Fusion ERP, Primavera, CRM, and on-premises data is supplied as simulated source extracts. Contracts, engineering specifications, and inspection documents are stored in OCI Object Storage. The workshop does not require access to the source enterprise applications.

## Workshop entry point

Open `workshops/tenancy/index.html` through the LiveLabs publishing workflow. The adjacent `manifest.json` defines the tutorial order and points to the shared Markdown files at the repository root.

## Draft data contracts

The first draft assumes these schemas and products:

- `SEER_BRONZE`: faithful source extracts and ingestion metadata
- `SEER_SILVER`: standardized and reconciled enterprise entities
- `SEER_GOLD`: governed, consumer-ready data products
- `SEER_GOLD.PROJECT_CONTEXT`
- `SEER_GOLD.SUPPLIER_RECOMMENDATIONS`
- `SEER_GOLD.SUPPLIER_PROFILE`
- `SEER_GOLD.DOCUMENT_CHUNKS`

The names are design contracts for the sample-data and environment build. They must be verified during implementation and end-to-end validation.

## Content status

This is a narrative and instructional first draft. Exact AIDP and Autonomous AI Lakehouse UI labels, screenshots, SQL output, resource names, and timings must be validated against the final workshop environment before publication.

