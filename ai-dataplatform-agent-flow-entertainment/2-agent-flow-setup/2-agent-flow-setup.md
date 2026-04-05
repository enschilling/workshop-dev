# Lab 2: Agent Flow Setup

## Introduction

With the data environment in place — a Knowledge Base for RAG and Oracle AI Database tables for SQL — it's time to build the agent itself. In this lab, you'll create the AI Compute that powers the agent, design the agent flow on the visual canvas, configure the agent node with detailed instructions, and wire up all the tools: one RAG tool connected to the Knowledge Base and seven SQL tools that query box office, streaming, and marketing data.

By the end of this lab, you'll have a fully configured Entertainment Release & Performance Analyst Agent ready for testing.

**Estimated Time:** 25 Minutes

### Objectives

In this lab you will:

1. Create an agent flow and attach it to the AI Compute instance
2. Configure the agent node with a model and detailed agent instructions
3. Add a RAG tool connected to the Knowledge Base you created in Lab 1
4. Add seven SQL tools that query box office, streaming, and marketing data from the Oracle AI Database

### Prerequisites

This lab assumes you have:

* Completed Lab 1 (Data Environment Setup)
* A Knowledge Base (`entertainment_analyst_kb`) in Active status with documents ingested
* Access to the Oracle AI Database with entertainment performance tables
* Extracted the `agent_instructions.txt` file from the Zip archive in Lab 1

## Task 1: Create the Agent Flow

With the AI Compute instance created in Lab 1 (should be **Active** now), you can now create the agent flow — the visual canvas where you design the agent's behavior, tools, and configuration.

1. Navigate to your workspace and click on **Agent Flows**. Click the **+** button to create a new agent flow.

2. Enter a name and description:

    **Name**
    ```
    <copy>
    entertainment_analyst
    </copy>
    ```
    
    **Description**
    ```
    <copy>
    This is an internal analytics and decision-support agent for an entertainment studio or streaming platform.
    </copy>
    ```

    ![Create dialogue for new Agent Flow](images/02-agent-flows-create.png " ")

3. You will be directed to the **agent flow canvas** — a visual design environment where you'll drag and configure agent nodes and tools.

4. Attach the agent flow to the AI Compute you just created. In the upper right corner, click **Compute** → **Attach to AI Compute**, then select the AI Compute you created in Task 1.

    ![Attach AI Compute to Agent flow using the menu](images/02-agent-flows-attach-compute.png " ")

## Task 2: Configure the Agent Node

The agent node is the core of your flow. It defines the LLM model, the system instructions that govern the agent's behavior, and the reasoning approach.

1. Drag an **Agent node** onto the canvas, then click on the entity frame that appears on the Canvas.

2. Click the *Agent Name* and *Agent Description* to edit both. Assign more detailed values.

    **Name**
    ```
    <copy>
    Analyst Agent
    </copy>
    ```
    
    **Description**
    ```
    <copy>
    This is an internal analytics and decision-support agent for an entertainment studio or streaming platform.
    </copy>
    ```

3. In the **Configuration** tab, set the following:

    ```
    Region: us-phoenix-1
    Model: xai.grok-4-fast-reasoning
    ```

4. For the **Agent Instructions** field, you'll need the detailed instructions that define the agent's behavior, reasoning flow, and response style. These instructions tell the agent:

    - Its role (internal analytics and decision-support for entertainment teams)
    - When to use RAG vs. SQL tools
    - The reasoning sequence: classify the question → retrieve knowledge → query data → synthesize → respond
    - Response style guidelines (concise, analytical, structured)
    - What it must NOT do (no guessing metrics, no bypassing SQL tools, no fabricating data)

5. Open the **`agent_instructions.txt`** file that was in the Zip archive you extracted earlier.

6. Delete the instructions in the **Agent Instructions** box and copy the entire content of **`agent_instructions.txt`** into the **Agent Instructions** box in the Configuration tab.

    ![Agent configuration dialog with all parameters entered](images/02-agent-flows-create-agent-details.png " ")

7. Leave the **Model Parameters** and **Safety Guardrails** settings as-is for now.

8. The **Agent flows** canvas auto-saves your input as you work. Now you're ready to move to the next task.

## Task 3: Add the RAG Tool

The RAG tool connects the agent to the Knowledge Base you created in Lab 1. When users ask about definitions, policies, thresholds, or interpretation rules, the agent uses this tool to retrieve relevant passages from the internal documents.

1. Drag a **RAG tool** onto the canvas.

    ![Agent flows canvas - attach RAG tool](images/02-agent-flows-attach-rag.png " ")

2. Enter a name:

    **Name**
    ```
    <copy>
    internal_knowledge_sources_rag
    </copy>
    ```
    
3. In the **Configuration** tab, select the Knowledge Base you created in Lab 1 (`entertainment_analyst_kb`).

    ![RAG tool configuration - select knowledge base](images/02-agent-flows-rag-select-kbase.png " ")

4. Enter a description. The **`Description`** field comes pre-populated with instructions on how to use the field. You'll want to delete all contents before pasting the above description.

    **Description**
    ```
    <copy>
    You have access to the following authoritative internal documents via a RAG tool: 
        - Content Strategy & Release Operations Playbook
        - Marketing Measurement & Attribution Guidelines
        - Distribution Window & Territory Rules
    </copy>
    ```

5. Set the document retrieval limit to **5**. This is the number of chunks returned by the Knowledge Base for each query.

6. Leave the **Query** field intact.

7. Optionally, click the **Test** tab to verify the RAG tool is working. Enter the following test query and click **[Submit]**:

    ```
    <copy>
    Territory priorities for releases
    </copy>
    ```

8. You should see relevant passages returned from the release playbook documents. This confirms the Knowledge Base is properly connected and returning results.

    ![Screenshot showing rag tool validation](images/02-agent-flows-validate-rag.png " ")

## Task 4: Add the SQL Tools — Box Office and Streaming

Now we'll add the SQL tools. Each SQL tool executes a single, pre-defined, parameterized query against the Oracle AI Database. The agent selects which tool to call based on the user's question and populates the parameters automatically.

### Tool 1: Get box office weekend data

This tool returns weekend theatrical performance for a title in a given market.

1. Drag a **SQL tool** onto the canvas.

2. Enter the name and description:

    **Name**
    ```
    <copy>
    get_box_office_weekend
    </copy>
    ```
    
    **Description**
    ```
    <copy>
    Weekend theatrical performance for a title in a market.
    </copy>
    ```

3. Under **Catalog and Schema**, click the **Search** drop-down. Expand the **`aidatabase`** item and select the **`entertainment`** schema.

    ![Screenshot depicting the catalog and schema drop-down](images/02-agent-flows-sql-select-schema.png " ")

4. Enter the following SQL query:

    ```sql
    <copy>
    SELECT
      t.title_name,
      b.weekend_end_date,
      b.market_code,
      b.gross_usd_m,
      b.screens,
      b.rank
    FROM box_office_weekend b
    JOIN titles t ON t.title_id = b.title_id
    WHERE b.title_id = {{title_id}}
      AND b.market_code = {{market_code}}
    </copy>
    ```

5. The parameters `{{title_id}}` and `{{market_code}}` will appear in the right panel under **AI Tool Definition**. Enter descriptions for each:

    
    **{{title_id}}**
    ```
    <copy>
    The title ID of the movie. For example, T1002. If you are unsure, use the tool get_title_id. The last option is to ask the user.
    </copy>
    ```

    **{{market_code}}**
    ```
    <copy>
    Market code is a two letter code representing the country or region where the movie is released. These are documented in our internal policy documents. An example is Japan being JP.
    </copy>
    ```

    ![Screenshot depicting AI Tool definition description input](images/02-agent-flows-sql-ai-tool-definition.png " ")

6. Optionally, click the **Test** tab and assign values to validate:

    **title_id**
    ```
    <copy>T1001</copy>
    ```

    **market_code**
    ```
    <copy>US</copy>
    ```

    You should see two rows for Skyline Heist on 2025-09-14 and 2025-09-21.

    ![Screenshot depicting test results](images/02-agent-flows-sql-test-tool.png " ")

### Tool 2: Get streaming trend data

This tool returns weekly streaming health metrics (starts, hours, completion rate) for a title in a region.

1. Drag another **SQL tool** onto the canvas.

2. Enter the name and description:

    **Name**
    ```
    <copy>
    get_streaming_trend
    </copy>
    ```

    **Description**
    ```
    <copy>
    Weekly streaming health trend (starts, hours, completion) for a title in a region.
    </copy>
    ```

3. Select the same catalog and schema as the previous tool.

4. Enter the following SQL query:

    ```sql
    <copy>
    SELECT
      t.title_name,
      s.week_start_date,
      s.region_code,
      s.starts,
      s.hours_streamed_k,
      s.completion_rate
    FROM streaming_weekly s
    JOIN titles t ON t.title_id = s.title_id
    WHERE s.title_id = {{title_id}}
      AND s.region_code = {{region_code}}
    ORDER BY s.week_start_date ASC
    </copy>
    ```

5. Enter parameter descriptions:

    **{{title_id}}**
    ```
    <copy>
    The title ID of the movie. For example, T1002. If you are unsure, use the tool get_title_id. The last option is to ask the user.
    </copy>
    ```

    **{{region_code}}**
    ```
    <copy>
    A two letter code representing the country or region where the movie is released. These are documented in our internal policy documents. An example is Japan being JP.
    </copy>
    ```

## Task 5: Add the SQL Tools — Marketing

### Tool 3: Get campaign summary data

This tool returns the roll-up of spend, attributed revenue, and computed ROI for a marketing campaign.

1. Drag a **SQL tool** onto the canvas.

2. Enter the name and description:

    **Name**
    ```
    <copy>
    get_campaign_summary
    </copy>
    ```

    **Description**
    ```
    <copy>
    Roll up spend + attributed revenue + computed ROI for a campaign (all channels, all days).
    </copy>
    ```

3. Select the same catalog and schema.

4. Enter the following SQL query:

    ```sql
    <copy>
    SELECT
      c.campaign_id,
      c.campaign_name,
      c.title_id,
      t.title_name,
      c.start_date,
      c.end_date,
      SUM(d.spend_usd) AS total_spend_usd,
      SUM(d.attributed_revenue_usd) AS total_attributed_revenue_usd,
      CASE
        WHEN SUM(d.spend_usd) = 0 THEN NULL
        ELSE (SUM(d.attributed_revenue_usd) - SUM(d.spend_usd)) / SUM(d.spend_usd)
      END AS roi
    FROM marketing_campaigns c
    JOIN titles t ON t.title_id = c.title_id
    JOIN marketing_daily_spend d ON d.campaign_id = c.campaign_id
    WHERE c.campaign_id = {{campaign_id}}
    GROUP BY
      c.campaign_id, c.campaign_name, c.title_id, t.title_name, c.start_date, c.end_date
    </copy>
    ```

5. Enter the parameter description:

    **{{campaign_id}}**

    ```
    <copy>
    The ID of a marketing campaign associated with movies. For example: Z2001.
    </copy>
    ```

### Tool 4: Get campaign channel breakdown

This tool provides a breakdown of campaign spend and revenue by marketing channel.

1. Drag a **SQL tool** onto the canvas.

2. Enter the name and description:

    **Name**
    ```
    <copy>
    get_campaign_channel_breakdown
    </copy>
    ```

    **Description**
    ```
    <copy>
    Provides a breakdown of campaign spend and revenue by marketing channel.
    </copy>
    ```

3. Select the same catalog and schema.

4. Enter the following SQL query:

    ```sql
    <copy>
    SELECT
      d.channel,
      SUM(d.spend_usd) AS spend_usd,
      SUM(d.attributed_revenue_usd) AS attributed_revenue_usd,
      CASE
        WHEN SUM(d.spend_usd) = 0 THEN NULL
        ELSE (SUM(d.attributed_revenue_usd) - SUM(d.spend_usd)) / SUM(d.spend_usd)
      END AS roi
    FROM marketing_daily_spend d
    WHERE d.campaign_id = {{campaign_id}}
    GROUP BY d.channel
    ORDER BY spend_usd DESC
    </copy>
    ```

5. Enter the parameter description:

    **{{campaign_id}}**
    ```
    <copy>
    The marketing campaign ID of interest. For example: C2001.
    </copy>
    ```

## Task 6: Add the SQL Tools — Reference Lookups

These tools provide reference data that helps the agent resolve IDs and codes when users ask questions using title names, market names, or campaign names instead of IDs.

### Tool 5: Get title id

1. Drag a **SQL tool** onto the canvas.

2. Enter the name and description:

    **Name**
    ```
    <copy>
    get_title_id
    </copy>
    ```

    **Description**
    ```
    <copy>
    This tool returns a table of all title IDs and title names.
    </copy>
    ```

3. Select the same catalog and schema.

4. Enter the following SQL query:

    ```sql
    <copy>
    SELECT * FROM titles
    </copy>
    ```

5. This tool has **no parameters**.

### Tool 6: Get market code

1. Drag a **SQL tool** onto the canvas.

2. Enter the name and description:

    **Name**
    ```
    <copy>
    get_market_code
    </copy>
    ```

    **Description**
    ```
    <copy>
    Returns a table of market codes alongside market names and currency.
    </copy>
    ```

3. Select the same catalog and schema.

4. Enter the following SQL query:

    ```sql
    <copy>
    SELECT * FROM markets
    </copy>
    ```

5. This tool has **no parameters**.

### Tool 7: Get campaign code

1. Drag a **SQL tool** onto the canvas.

2. Enter the name and description:

    **Name**
    ```
    <copy>
    get_campaign_code
    </copy>
    ```

    **Description**
    ```
    <copy>
    Provides a mapping between campaign ID, the campaign name and the associated movie (the title ID).
    </copy>
    ```

3. Select the same catalog and schema.

4. Enter the following SQL query:

    ```sql
    <copy>
    SELECT * FROM marketing_campaigns
    </copy>
    ```

5. This tool has **no parameters**.

## Lab 2 Recap

In this lab, you built the complete agent flow for the Entertainment Release & Performance Analyst:

- You created the **agent flow** on the visual canvas and attached it to the AI Compute.
- You configured the **agent node** with the xai.grok-4-fast-reasoning model and detailed instructions that define the agent's reasoning flow, response style, and behavioral guardrails.
- You added a **RAG tool** connected to the Knowledge Base containing release playbooks and strategy documents.
- You added **seven SQL tools** covering box office performance, streaming health, campaign summaries, channel breakdowns, and reference lookups for titles, markets, and campaigns.

The agent now has everything it needs: a brain (the LLM), internal knowledge (RAG), and structured data access (SQL). In the next lab, you'll test it in the Playground.

## Learn More

* [Oracle AI Data Platform — Sample Agent Flows on GitHub](https://github.com/oracle-samples/oracle-aidp-samples/tree/main/ai/agent-flows)
* [Build Your Agentic Solution Using Oracle Autonomous AI Database Select AI Agent — Oracle Blog](https://blogs.oracle.com/machinelearning/build-your-agentic-solution-using-oracle-adb-select-ai-agent)
* [Oracle AI Data Platform — Documentation](https://docs.oracle.com/en/cloud/paas/ai-data-platform/)

## Acknowledgements

* **Author(s)** - Jean-Rene Gauthier [AIDP]
* **Contributors** - Eli Schilling - Cloud Architect, Gareth Nathan - SDE, GenAI
* **Last Updated By/Date** - Published March 2026
