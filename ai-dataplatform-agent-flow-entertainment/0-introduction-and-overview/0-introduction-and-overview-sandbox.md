# Lab 1: Introduction and Overview

## Introduction

This lab sets the foundation for the entire workshop. We'll start with the entertainment industry's data challenge — why analyzing movie and TV show performance across marketing, finance, and distribution is so painful today. We'll then introduce Oracle AI Data Platform conceptually, walk through its medallion architecture using a movie release scenario, and orient you in the AIDP Workbench environment you'll use for the remainder of the workshop.

By the end of this lab, you'll understand the problem we're solving, the platform architecture that solves it, and the tools you'll use hands-on to build a Release & Performance Analyst Agent powered by RAG and SQL.

**Estimated Time:** 25 Minutes

### Objectives

In this lab you will:

1. Understand the entertainment-specific data challenges that Oracle AI Data Platform addresses
2. Learn what Oracle AI Data Platform is, its four value pillars, and how it maps to entertainment roles
3. Walk through the medallion architecture (bronze → silver → gold) using a movie release performance scenario
4. Orient yourself in the AIDP Workbench environment — Master Catalog, Workspaces, Notebooks, Compute, and Agent Flows

### Prerequisites

This lab assumes you have:

* An Oracle Cloud Infrastructure (OCI) account with access to an AI Data Platform Workbench instance provisioned for this workshop
* A modern web browser (Chrome, Firefox, or Edge recommended)
* The Workbench URL provided by your workshop facilitator

## Task 1: The Entertainment Data Challenge

In this task, we set the stage by discussing why entertainment companies struggle to get a unified view of title performance and marketing ROI. This section is discussion-based — no tools required yet.

1. Consider the data explosion around a single movie or TV show release. A title generates data across dozens of systems: box office and streaming metrics, media spend by channel, social sentiment, audience demographics, licensing revenue, talent contracts, post-mortem reports, and more. Most of it lives in silos.

2. Think about the cross-team pain. Marketing wants to know which campaigns drove viewership. Finance wants to know cost-per-acquisition and ROI by title. Distribution wants to know performance by platform. Everyone is pulling from different sources, at different cadences, with different definitions of "success."

3. Recognize the stitching problem. Teams glue together 5–10 tools for reporting, attribution, forecasting, and analysis — creating fragile pipelines, conflicting numbers, and slow time-to-insight on releases that have a narrow performance window.

4. Frame the question we're exploring in this workshop: *What does it look like when all of that data is unified in a single platform — and an AI agent can answer questions from marketing, finance, and distribution in real time?*

    > **Discussion prompt**: "How many distinct tools or platforms does your team use to analyze a title's performance? What's the hardest question to answer after a movie or show launches?"

## Task 2: Oracle AI Data Platform — The Big Picture

In this task, we introduce Oracle AI Data Platform at a conceptual level before getting hands-on in later tasks.

1. **What it is**: Oracle AI Data Platform (AIDP) is a unified, governed environment that brings together data lakehouse capabilities, AI/ML tooling, analytics, and generative AI services — all on Oracle Cloud Infrastructure. It was announced at Oracle AI World in October 2025 and is generally available, with $1.5B+ in partner investment commitments and over 8,000 practitioners already trained.

2. **The four value pillars**:

    - **Turn data into intelligence** — Unify raw data into actionable insights via a single platform. *Entertainment example*: Box office, streaming, ad spend, and internal docs all flow into one governed lakehouse instead of separate systems.
    - **Accelerate innovation across teams** — Shared workbench for engineers, scientists, and analysts. *Entertainment example*: Data engineers build the pipeline, data scientists train viewership models, and marketing analysts build dashboards — all in the same environment.
    - **Automate & scale with AI agents** — Go beyond dashboards; orchestrate workflows and trigger actions. *Entertainment example*: An AI agent monitors release performance and proactively answers questions about ROI, box office trends, and streaming health — in real time.
    - **Enterprise-ready from day one** — Built on OCI with governance, security, and multi-cloud support baked in. *Entertainment example*: Role-based access ensures marketing sees campaign data while finance sees full P&L with cost details — automatically enforced.

3. **Who it's for in entertainment**:

    - *Marketing teams*: Campaign performance analysis, attribution modeling, audience insights, media mix optimization
    - *Finance teams*: Title-level P&L, marketing ROI computation, revenue forecasting, budget allocation
    - *Data engineers*: Pipeline design, ingestion from streaming platforms / box office / ad systems, data quality
    - *Content strategy*: Release window planning, territory prioritization, franchise health checks
    - *Distribution / strategy*: Platform performance comparison, windowing analysis, licensing insights

    > **Discussion prompt**: "Which of those four pillars resonates most with what your team needs for the next release cycle?"

## Task 3: The Medallion Architecture

In this task, we walk through the architectural model that organizes data inside AIDP. This is the conceptual foundation for everything you'll build in later labs.

1. Understand the three medallion layers. AIDP organizes data in progressive layers — each one increasing in quality, governance, and business readiness:

    | Layer | What It Holds | Entertainment Examples | Who Works Here |
    |---|---|---|---|
    | **Bronze** | Raw, unprocessed data exactly as received from source systems | Box office daily feeds, streaming API pulls, ad platform exports, social listening dumps, raw Nielsen data, internal campaign briefs (PDFs/docs) | Data engineers |
    | **Silver** | Cleaned, validated, transformed data; ML models can be trained here | Standardized title-level metrics, unified campaign spend, audience segments, viewership prediction models, documents chunked and embedded for vector search | Data engineers + data scientists |
    | **Gold** | Curated, business-ready data products; query-optimized | Title P&L views, marketing ROI by campaign, audience overlap matrices, release performance scorecards — all in Autonomous AI Database | Marketing, finance, analysts, AI agents |

2. Walk through the supporting infrastructure:

    - **Unified Catalog (Master Catalog)**: A "catalog of catalogs" providing a single view of all data and AI assets across layers. Tracks lineage, enforces governance, supports discovery.
    - **Apache Spark**: Powers the compute layer for distributed data processing across bronze → silver → gold.
    - **Open Formats**: Delta Lake, Apache Iceberg, and Parquet — no vendor lock-in for data storage.
    - **Zero-ETL / Zero-Copy**: Connect to Oracle Fusion application data without moving it.

3. Follow a title release through all three layers:

    > **Movie release performance scenario**:
    >
    > **Bronze** — Raw data lands from multiple sources: daily box office receipts (CSV), streaming viewership API pulls (JSON), ad platform exports from Google/Meta/TikTok campaigns (CSV), social media sentiment feeds, and internal documents like the Content Strategy Playbook, Marketing Measurement Guidelines, and Distribution Window Rules (PDFs stored in Object Storage). All of this lands untouched in the bronze layer.
    >
    > **Silver** — Spark notebooks clean and standardize the data: normalizing date formats, mapping campaign IDs to title IDs, deduplicating audience records, computing derived metrics (cost-per-view, ROI, completion rates). Internal documents are chunked, embedded as vectors, and indexed in a knowledge base — enabling RAG. Everything is stored in Delta Lake / Iceberg tables.
    >
    > **Gold** — The curated data lands in Oracle Autonomous AI Database as query-ready tables: `titles`, `box_office_weekend`, `streaming_weekly`, `marketing_campaigns`, `marketing_daily_spend`, `markets`. An AI agent can answer natural language questions by combining SQL queries against these tables with RAG lookups against the knowledge base.

    > **Discussion prompt**: "Think about the last title your team launched. Which of these data sources do you already have flowing? Which ones are still manual or siloed?"

## Task 4: Orientation — The AIDP Workbench

Now let's briefly orient ourselves in the environment you'll use for the rest of the workshop. In this task, you'll log in and survey the key areas of the Workbench interface.

1. Open your web browser and navigate to the AIDP Workbench URL provided by your facilitator. If accessing via the OCI Console, navigate to **Analytics & AI** → **AI Data Platform** → **AI Data Platform Workbenches**, and click on the Workbench instance provisioned for this workshop.

2. Once the Workbench loads, you'll land on the **Home Page**. This is your central hub. Take a moment to orient yourself. From here, you can access:

    - **Master Catalog** — Where all your data and AI assets are registered, discovered, and governed. You'll explore this in detail in Lab 2.
    - **Workspaces** — Where your notebooks, files, and development work happen. Each workspace is a collaborative environment with role-based permissions.
    - **Compute** — Where Spark clusters (for data processing) and AI Compute (for agent flows) are managed.
    - **Agent Flows** — The visual design environment for building AI agents. This is where you'll build the Entertainment Analyst agent in Labs 3–5.

3. For the rest of this workshop, here's how each Workbench component maps to what you'll build:

    | Workbench Component | What You'll Do With It |
    |---|---|
    | **Master Catalog** | Browse the pre-configured catalog and volume; create a Knowledge Base for RAG |
    | **Workspaces** | Access your workspace for agent flow development |
    | **Compute (AI Compute)** | Create and attach AI Compute to power your agent flow |
    | **Agent Flows** | Build the Entertainment Analyst agent with RAG + SQL tools; test in the Playground; deploy |

    > **Key takeaway**: The Master Catalog holds your governed data and knowledge bases. Workspaces hold your development work. AI Compute powers your agents. Agent Flows is where you design, test, and deploy them. In the next lab, we'll start setting up the data environment.

## Lab 1 Recap

In this lab, you covered the conceptual foundation for the entire workshop:

- **The problem**: Entertainment data is fragmented across systems, teams pull from different sources, and the current multi-tool approach creates conflicting numbers and slow time-to-insight.
- **The platform**: Oracle AI Data Platform unifies data lakehouse, AI/ML, analytics, and governance in a single environment on OCI.
- **The architecture**: The medallion model (bronze → silver → gold) provides a structured path from raw data to business-ready insights and AI-powered answers.
- **The environment**: You oriented yourself in the AIDP Workbench and understand which components you'll use in the hands-on labs that follow.

In the next lab, you'll set up the data environment — exploring the pre-configured catalog and documents, creating a Knowledge Base for RAG, and verifying the database tables that power the SQL tools.

## Learn More

* [Oracle AI Data Platform — Product Page](https://www.oracle.com/ai-data-platform/)
* [Oracle AI Data Platform Workbench — Product Page](https://www.oracle.com/ai-data-platform/workbench/)
* [What Is the AI Data Platform? — Oracle Blog](https://blogs.oracle.com/ai-data-platform/what-is-the-ai-data-platform)
* [Getting Started on Your Oracle AI Data Platform Journey — Oracle Blog](https://blogs.oracle.com/ai-data-platform/getting-started-on-your-oracle-ai-data-platform-journey)
* [Oracle AI Data Platform — Documentation](https://docs.oracle.com/en/cloud/paas/ai-data-platform/)
* [Oracle AI Data Platform — Sample Notebooks on GitHub](https://github.com/oracle-samples/oracle-aidp-samples)

## Acknowledgements

* **Author(s)** - [Your Name]
* **Contributors** - [Contributor Names]
* **Last Updated By/Date** - Published March 2026
