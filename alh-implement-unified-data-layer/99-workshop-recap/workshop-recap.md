# Workshop Recap

## Introduction

You began with source systems and documents that described the same projects, suppliers, assets, and events in different ways. You finished with governed products that applications and agents can consume without reconstructing the enterprise data estate themselves.

**Estimated Time:** 10 minutes

### Objectives

In this recap, you will:

- Review what you accomplished in each lab.
- Reconnect the medallion layers to application and agent outcomes.
- Identify production considerations beyond the workshop.
- Understand the handoff to the AppDev and Construction Evaluation Agent workshops.

### Prerequisites

- Completion of Labs 1 through 3

## What you accomplished

### Lab 1: Explore the Unified Lakehouse Foundation

You inspected representative Fusion ERP-, Primavera-, CRM-, and on-premises-style source extracts, together with actual project documents registered from OCI Object Storage. You traced the Austin steel-delivery event from source-specific records to a canonical Silver entity and a consumer-ready Gold product.

### Lab 2: Unify Data for AI Applications

You explored relational, JSON, relationship, and vector representations of the governed data. You searched for Austin structural specifications by meaning and combined the retrieved passage with purchasing, schedule, supplier, and inspection context.

### Lab 3: Deliver Trusted Data Products

You reviewed workflow execution evidence, validated quality and freshness, inspected product contracts, and mapped the Gold products to developer interfaces and the downstream Construction Evaluation Agent.

## The completed data journey

```text
Simulated source feeds and real project documents
                       |
     Catalog, classifications, and provenance
                       |
        Bronze: faithful source capture
                       |
    Silver: standardize, validate, reconcile
                       |
        Gold: trusted data products
                       |
 SQL | JSON | relationships | vectors | RAG
                       |
     Applications and governed AI agents
```

## Key takeaways

- AI readiness begins with data-engineering discipline.
- Bronze, Silver, and Gold represent different contracts and responsibilities.
- Structured facts and unstructured evidence can share one governed foundation.
- Semantic retrieval depends on chunking, metadata, provenance, and evaluation quality.
- Gold products establish the interface between data engineers and developers.
- Agents should consume governed products instead of raw source data.

## Business value for Seer

### Faster project and supplier decisions

Teams can evaluate project requirements, supplier qualifications, schedule status, and engineering evidence without manually reconciling systems for every question.

### Reduced compliance and delivery risk

Inspection findings, certifications, nonconformance records, contracts, and specifications remain connected to the assets and suppliers they govern.

### Reusable application foundation

The same products can support analytics, application APIs, semantic search, and multiple agents. Teams do not need to build a separate data pipeline for every interface.

### Governance without losing context

Lineage, classifications, ownership, and source-document references remain part of the product. Consumers can explain where an answer came from.

## Production considerations

The workshop uses a compact, pre-provisioned environment. A production implementation should also address:

- Pipeline monitoring, restart, and incident response
- Quality and freshness service-level objectives
- Schema and data-product contract evolution
- Partitioning, caching, and workload optimization
- Embedding-model and vector-index lifecycle management
- Retrieval evaluation and regression testing
- Retention, legal hold, and document-version policy
- Least-privilege access, masking, auditing, and separation of duties
- Governed sharing across organizations or clouds

Oracle can incorporate data from storage and database services in other clouds, including Amazon S3, Azure Blob Storage, and Oracle Database deployments outside OCI. Those integrations are architectural options, not hands-on exercises in this workshop.

## What's next

### Data Fundamentals for AI Application Development

Developers explore how relational SQL, JSON, property graphs, and vector search can be combined in Oracle AI Database. They begin with curated data that the data-engineering team has already prepared.

### Assemble and Deploy an AI Agent using RAG and SQL

Agent builders configure a governed document knowledge base and create the Construction Evaluation Agent. The agent uses:

- `get_project_context`
- `get_supplier_recommendations`
- `get_supplier_profile`
- Construction policy and guidance documents through RAG

This workshop prepared the trusted foundation those tools depend on.

## Learn More

- [Oracle Autonomous AI Lakehouse](https://www.oracle.com/autonomous-database/autonomous-data-warehouse/)
- [Oracle AI Vector Search](https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/)
- [OCI Object Storage](https://docs.oracle.com/en-us/iaas/Content/Object/home.htm)
- [OCI Data Catalog](https://docs.oracle.com/en-us/iaas/data-catalog/home.htm)

## Acknowledgements

- **Author:** Oracle AI Data Platform and Autonomous AI Lakehouse Workshop Team
- **Contributors:** Oracle LiveLabs, database, analytics, and AI data platform teams
- **Last Updated By/Date:** Workshop development team, July 2026

