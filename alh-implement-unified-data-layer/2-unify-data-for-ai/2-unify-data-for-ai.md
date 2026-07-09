# Lab 2: Unify Data for AI Applications

## Introduction

Gold data products make structured project facts easier to consume, but AI applications also need the detailed evidence stored in contracts, specifications, inspection reports, and compliance documents. In this lab, you will explore how Oracle Autonomous AI Lakehouse keeps structured and unstructured context together, then use vector search to find the section of an engineering specification that is relevant to the Austin structure.

The graph, chunks, embeddings, and vector index are already built. Your task is to understand and use them, not wait for them to be created.

**Estimated Time:** 20 minutes

### Objectives

In this lab, you will:

- Inspect the Gold products intended for applications and agents.
- Compare relational, JSON, relationship, and vector representations.
- Review how project documents were prepared for semantic retrieval.
- Run a vector search for Austin structural specifications.
- Combine retrieved evidence with structured project context and provenance.

### Prerequisites

- Completion of Lab 1
- Read access to `SEER_GOLD`
- The `ALL_MINILM_L12_V2` embedding model or the final workshop model loaded in the database
- Precomputed embeddings and a valid vector index on `SEER_GOLD.DOCUMENT_CHUNKS`

## Task 1: Inspect the consumer-ready Gold products

1. Review the Gold products and their intended consumers:

    ```sql
    SELECT product_name,
           business_purpose,
           product_owner,
           refresh_frequency,
           quality_status,
           intended_consumers
    FROM seer_gold.data_product_catalog
    ORDER BY product_name;
    ```

2. Locate the three products that align to the downstream Construction Evaluation Agent:

    - `PROJECT_CONTEXT`
    - `SUPPLIER_RECOMMENDATIONS`
    - `SUPPLIER_PROFILE`

3. Inspect the supplier recommendation product:

    ```sql
    SELECT project_name,
           supplier_name,
           fit_score,
           risk_level,
           recommendation_status,
           missing_information
    FROM seer_gold.supplier_recommendations
    ORDER BY project_name, fit_score DESC;
    ```

4. Notice that the product exposes a stable decision-support contract. It does not expose raw ingestion fields or require the consumer to reconstruct the source joins.

## Task 2: Compare the data shapes

Oracle Database can project the same governed entities through several data models without creating separate, unsynchronized stores.

1. Query relational project facts:

    ```sql
    SELECT project_name, asset_name, current_milestone, inspection_status
    FROM seer_gold.project_context
    WHERE UPPER(project_name) LIKE '%AUSTIN%';
    ```

2. Inspect flexible attributes stored as JSON:

    ```sql
    SELECT asset_name,
           specifications.material_grade AS material_grade,
           specifications.design_standard AS design_standard,
           specifications.fire_rating_minutes AS fire_rating_minutes
    FROM seer_gold.asset_profiles
    WHERE UPPER(project_name) LIKE '%AUSTIN%';
    ```

3. Explore the prebuilt relationship projection:

    ```sql
    SELECT from_entity_name,
           relationship_type,
           to_entity_name,
           relationship_source
    FROM seer_gold.asset_relationships
    WHERE UPPER(from_entity_name) LIKE '%AUSTIN%'
       OR UPPER(to_entity_name) LIKE '%AUSTIN%'
    ORDER BY from_entity_name, relationship_type;
    ```

4. These relationships can be projected as a property graph for application queries. This workshop uses a prepared relationship view so the focus remains on data-engineering intent rather than graph-definition syntax.

## Task 3: Inspect the document preparation pipeline

1. Review the registered project documents:

    ```sql
    SELECT document_id,
           document_name,
           document_type,
           project_name,
           asset_name,
           version_label,
           object_uri,
           classification
    FROM seer_gold.document_catalog
    ORDER BY project_name, document_type, document_name;
    ```

2. Inspect the prepared chunks for the Austin project:

    ```sql
    SELECT document_name,
           section_title,
           chunk_sequence,
           character_count,
           embedding_model,
           embedding_status
    FROM seer_gold.document_chunks
    WHERE UPPER(project_name) LIKE '%AUSTIN%'
    ORDER BY document_name, chunk_sequence;
    ```

3. Review the preparation stages:

    1. Register the original Object Storage object and version.
    2. Extract text while retaining page and section boundaries.
    3. Create chunks sized for coherent retrieval.
    4. Attach project, asset, supplier, classification, and provenance metadata.
    5. Generate embeddings inside the Oracle security boundary.
    6. Build or refresh the vector index.

4. Chunking is a data-quality decision. A technically valid embedding can still produce poor results when chunks omit headings, combine unrelated topics, or lose source metadata.

## Task 4: Search for Austin structural specifications

1. Run a semantic search using the workshop's in-database embedding model:

    ```sql
    SELECT document_name,
           section_title,
           page_number,
           chunk_text,
           VECTOR_DISTANCE(
             embedding,
             VECTOR_EMBEDDING(
               ALL_MINILM_L12_V2
               USING 'Austin structural specifications' AS DATA
             ),
             COSINE
           ) AS semantic_distance
    FROM seer_gold.document_chunks
    WHERE embedding IS NOT NULL
    ORDER BY semantic_distance
    FETCH APPROX FIRST 5 ROWS ONLY;
    ```

2. Confirm that a section from an Austin engineering specification ranks near the top even if it does not repeat the exact search phrase.

3. Record the document name, section, page number, and distance for the best result.

4. Compare semantic retrieval with a simple keyword filter:

    ```sql
    SELECT document_name, section_title, page_number, chunk_text
    FROM seer_gold.document_chunks
    WHERE UPPER(chunk_text) LIKE '%AUSTIN STRUCTURAL SPECIFICATIONS%';
    ```

5. Semantic search finds related meaning; keyword search finds exact text. Production retrieval may combine both approaches when exact project codes or contractual terms matter.

## Task 5: Combine document evidence with structured context

1. Use the best semantic matches as document evidence and join them to Gold project context:

    ```sql
    WITH ranked_chunks AS (
      SELECT document_id,
             document_name,
             section_title,
             page_number,
             project_id,
             asset_id,
             chunk_text,
             VECTOR_DISTANCE(
               embedding,
               VECTOR_EMBEDDING(
                 ALL_MINILM_L12_V2
                 USING 'Austin structural specifications' AS DATA
               ),
               COSINE
             ) AS semantic_distance
      FROM seer_gold.document_chunks
      WHERE embedding IS NOT NULL
      ORDER BY semantic_distance
      FETCH APPROX FIRST 3 ROWS ONLY
    )
    SELECT p.project_name,
           p.asset_name,
           p.current_milestone,
           p.purchase_order_status,
           p.inspection_status,
           r.document_name,
           r.section_title,
           r.page_number,
           r.chunk_text,
           r.semantic_distance
    FROM ranked_chunks r
    JOIN seer_gold.project_context p
      ON p.project_id = r.project_id
     AND p.asset_id = r.asset_id
    ORDER BY r.semantic_distance;
    ```

2. Review how the result brings together schedule, purchasing, inspection, and engineering evidence.

3. Verify the provenance of the selected chunk:

    ```sql
    SELECT document_name,
           object_uri,
           object_version,
           source_modified_at,
           extracted_at,
           chunking_policy,
           embedding_model,
           classification
    FROM seer_gold.document_provenance
    WHERE document_name = '<document name returned by your search>';
    ```

4. Replace the placeholder with the document name returned by your query. Confirm that the result can be traced to a specific source object and version.

## Lab 2 Recap

In this lab, you:

- Explored application-ready project and supplier products.
- Compared relational, JSON, relationship, and vector representations.
- Reviewed the prebuilt document-processing pipeline.
- Retrieved Austin engineering evidence by semantic meaning.
- Combined the evidence with structured project context and provenance.

The key takeaway is that structured facts and unstructured evidence can remain governed together. Applications and agents can retrieve richer context without sending sensitive project material to an unrelated external data store.

## Learn More

- [Oracle AI Vector Search User's Guide](https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/)
- [Generate vector embeddings in Oracle Database](https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/generate-vector-embeddings.html)
- [JSON in Oracle Database](https://docs.oracle.com/en/database/oracle/oracle-database/26/adjsn/)

## Acknowledgements

- **Author:** Eli Schilling, Cloud Architect || Evangelist
- **Contributors:** Oracle LiveLabs and ONA Lab Experience Teams
- **Last Updated By / Date:** ONA Lab Experience team, July 2026
