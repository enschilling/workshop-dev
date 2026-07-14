# Workshop Introduction and Overview

## Introduction

Seer Construction Group manages complex projects through a technology estate that includes financial systems, project schedules, supplier records, inspection databases, and thousands of project documents. Each system describes the same physical assets and business events in a different way. A steel delivery might appear as a purchase order in a financial system, a milestone in a project schedule, a supplier commitment in a CRM extract, and an inspection result in a field-quality database.

In the experience immediately before this workshop, Alex used Oracle AI Data Platform (AIDP) to catalog these sources and approve an ontology that connects their shared business meaning. This workshop moves beneath that ontology and into Oracle Autonomous AI Lakehouse (ALH). You will see how representative source extracts and unstructured documents become governed, trustworthy data products through a Bronze, Silver, and Gold medallion architecture.

The workshop environment is pre-provisioned so you can focus on the design decisions and outcomes instead of waiting for a complete medallion build. The seeded transformations in this workshop were implemented with ALH-native SQL, Data Studio, Data Transforms, and database jobs. AIDP notebooks did not execute these transformations.

**Estimated Time:** 5 minutes

### Objectives

In this workshop, you will:

- Explain the responsibilities of Bronze, Silver, and Gold data layers.
- Distinguish an AIDP notebook implementation from an ALH-native implementation.
- Trace a shared construction business object across simulated source feeds.
- Explore relational, JSON, graph, document, and vector representations of project data.
- Retrieve an engineering specification by meaning and combine it with structured context.
- Evaluate whether governed data products are ready for developers and AI agents.

### Prerequisites

- Basic familiarity with SQL, data integration, and object storage concepts
- Access to the pre-provisioned Oracle LiveLabs environment
- Completion of the **Get Started** section
- No access to Fusion ERP, Primavera, CRM, or an on-premises database is required

## The Seer data challenge

Seer's source estate contains valuable context, but no source has a complete view of a project:

| Representative source | Workshop data | Business context |
| --- | --- | --- |
| Fusion ERP-style feed | Purchase orders, costs, assets | Financial commitment and asset value |
| Primavera-style feed | Activities, milestones, dates | Construction plan and schedule risk |
| CRM-style feed | Suppliers, contacts, qualifications | Supplier identity and relationship history |
| On-premises-style snapshot | Inspections, findings, compliance | Quality, safety, and regulatory evidence |
| OCI Object Storage | Contracts, specifications, inspection documents | Detailed unstructured project evidence |

The enterprise-system feeds in this workshop are realistic source extracts, not live connections. Each Bronze record retains provenance such as its source system, source object, source record identifier, extraction timestamp, and ingestion batch.

## Reference architecture

The workshop follows this data journey:

```text
Representative enterprise extracts       Contracts and engineering documents
                  \                         /
                   Catalog, metadata, and governed ingestion
                                   |
                  Bronze: faithful source capture
                                   |
               Silver: standardize and reconcile
                                   |
             Gold: trusted, consumer-ready products
                                   |
           SQL | JSON | Graph | Vector | RAG consumers
                                   |
           Applications and Construction Evaluation Agent
```

The approved ontology provides shared meaning. The medallion architecture provides the governed data implementation that makes that meaning reliable and consumable.

## Two valid transformation approaches

Oracle supports more than one implementation pattern for medallion architecture. The layer responsibilities remain consistent even when the execution engine changes.

| Consideration | AIDP Workbench approach | ALH-native approach |
| --- | --- | --- |
| Primary transformation engine | Spark compute | Oracle Database SQL and Data Transforms |
| Development experience | Python, SQL, or Scala notebooks | SQL worksheet and visual data flows |
| Orchestration | AIDP workflows and notebook jobs | Data Transforms workflows, schedules, and database jobs |
| Strong fit | Distributed processing, open lakehouse tables, Python libraries, and data-science collaboration | Database-centric integration, SQL transformations, governed serving, and multimodel or vector workloads |
| Typical data products | AIDP catalogs, volumes, open tables, and connected targets | ALH tables, views, external data, JSON, relationships, and vectors |

The approaches are complementary. A team can use AIDP to process large or distributed datasets with Spark and publish selected products to ALH. A team can also implement the full medallion pattern directly in ALH when the data is already in, or reachable from, the database and its consumers need database-native products.

### Why this workshop uses ALH

This workshop uses the ALH-native approach for four reasons:

- The final relational, JSON, relationship, document, and vector products reside in ALH.
- The sample transformations are SQL-centric and do not require distributed Spark processing.
- Object Storage data can be loaded or linked directly from ALH Data Studio.
- A self-contained ALH flow makes the path from source evidence to application-ready products clear within the 75-minute workshop.

The decision is architectural, not a statement that one product replaces the other. The **Getting Started with Oracle AI Data Platform Workbench - Data Engineering** workshop demonstrates the complementary AIDP pattern by running notebooks on AIDP compute, orchestrating them with AIDP workflows, and publishing selected Gold data to ALH through an external catalog.

## What is already prepared

The ALH workshop setup process has already:

- Loaded representative source extracts into the Bronze layer.
- Registered project documents stored in OCI Object Storage.
- Built Silver entities for projects, assets, suppliers, orders, milestones, and inspections with ALH SQL and Data Transforms.
- Created Gold project and supplier products inside ALH.
- Parsed and chunked selected documents inside the database environment.
- Generated embeddings and created a vector index in ALH.
- Created sample lineage, quality, and ALH pipeline-execution records.

You will inspect and validate these assets. You will not run the long medallion build notebooks during the workshop.

## Workshop flow

### Lab 1: Explore the Unified Lakehouse Foundation

Discover Seer's representative source feeds, run a small ALH-native transformation, compare Bronze, Silver, and Gold, and trace the Austin steel-delivery example through the data layers.

### Lab 2: Unify Data for AI Applications

Explore the Gold products and multiple data shapes, search for Austin structural specifications, and combine document evidence with structured project context.

### Lab 3: Deliver Trusted Data Products

Inspect ALH Data Transforms and database-job evidence, validate readiness, and map governed products to developer interfaces and the downstream Construction Evaluation Agent.

## Key concepts

- **Medallion architecture:** A layered design that preserves raw evidence, improves quality, and creates stable business products.
- **Data product:** A governed dataset with a defined purpose, owner, schema, quality expectations, and consumers.
- **Provenance:** Evidence describing where data came from and how it changed.
- **Vector embedding:** A numerical representation used to compare semantic meaning.
- **Retrieval-augmented generation:** A pattern that grounds model responses in retrieved enterprise context.

## Learn More

- [Oracle Autonomous AI Lakehouse](https://www.oracle.com/autonomous-database/autonomous-data-warehouse/)
- [Transform Data with Data Transforms in Autonomous AI Database](https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/autonomous-data-transforms.html)
- [Oracle AI Data Platform Workbench overview](https://docs.oracle.com/en/cloud/paas/ai-data-platform/aidug/overview-oracle-ai-data-platform.html)
- [Oracle AI Vector Search](https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/)
- [Query external data in Autonomous Database](https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/query-external-data.html)

## Acknowledgements

- **Author:** Eli Schilling, Cloud Architect || Evangelist
- **Contributors:** Oracle LiveLabs and ONA Lab Experience Teams
- **Last Updated By / Date:** ONA Lab Experience team, July 2026
