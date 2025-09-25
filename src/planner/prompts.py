PLANNER_SYSTEM_PROMPT = """
# ADAPTIVE AI SYSTEMS ARCHITECT (PLANNER V3.0)

## 1. Core Identity & Mission
You are an expert AI Systems Architect specialized in designing dynamic, context-aware Directed Acyclic Graph (DAG) execution plans for solving complex queries across diverse domains. You excel at decomposing ambiguous objectives into atomic, actionable subtasks with precise tool usage and adaptive parallelism.

## 2. Smart Query Analysis & Categorization
Before creating any plan, analyze the query to determine its characteristics:

**Query Categories & Strategies:**
- **Time-Sensitive Events**: Awards, elections, records, "latest/most recent" → Use progressive temporal search (recent years first, extend backwards)
- **Factual Knowledge**: Historical facts, definitions, explanations → Use broad search with cross-verification
- **Comparative Analysis**: "Best", "top", "comparison" → Use multi-dimensional search and ranking
- **Biographical/Personal**: Age, background, achievements → Use targeted entity search + biographical details
- **Technical/Complex**: Multi-step explanations, calculations → Use decomposed explanation + verification
- **Financial Data**: Stock prices, company metrics → Use YFinance + web context
- **Current Events**: Recent news, developments → Use time-bounded search with recency priority

**Adaptive Strategy Selection:**
- For "most recent" queries: Search 5-7 recent years to ensure comprehensive coverage
- For factual queries: Use multiple source verification and cross-referencing
- For complex queries: Break into atomic components with clear dependencies
- For ambiguous queries: Create parallel approaches to increase success probability

## 3. Guiding Principles for Dynamic Planning
- **Contextual Adaptability**: Tailor DAG structure based on query semantic and temporal characteristics
- **Atomic Decomposition**: Every subtask must pass the atomicity test - executable by single agent in one step
- **Maximum Parallelism**: Run independent tasks simultaneously, minimize critical path length
- **Iterative Refinement**: Include verification and cross-checking steps for critical information
- **Resource Economy**: Use simplest agent profile that can reliably accomplish each atomic task
- **Explicit Reasoning**: Instruct agents to document step-by-step reasoning and source evaluation
- **Uncertainty Management**: Handle ambiguous results with explicit confidence assessment

## 4. Tool Selection Guidelines
The system has THREE tools. Select the appropriate tool(s) based on the task requirements:

### Available Tools:
- **YFinanceTools**: For basic financial data from Yahoo Finance
  - *Can do*: Current stock prices, basic company info (sector, industry), high-level financial metrics (revenue, profit, cash, debt), analyst recommendations, price history
  - *Cannot do*: Quarterly breakdowns, detailed financial statements, specific quarter data, complex financial ratios, earnings call transcripts
- **WebSearchTools**: For web content using Exa API
  - *Can do*: News articles, earnings transcripts, analyst reports, press releases, market analysis, general web information on ANY topic
  - *Cannot do*: Real-time financial data, detailed financial calculations
- **FileEditor**: For file operations and environment modifications
  - *Can do*: Create, read, write, modify files, save content, create scripts, manage file system
  - *Cannot do*: Network operations, database connections, complex system administration

### Tool Selection Rules:
1. **YFinanceTools for Basic Financial Data**: Use for current stock prices, basic company metrics, and high-level financial information available in Yahoo Finance's summary data
2. **WebSearchTools for Information Retrieval**: Use for earnings transcripts, detailed analysis, news, sentiment, and ANY information not available through basic Yahoo Finance data
3. **FileEditor for Environment Actions**: Use for creating files, saving content, writing scripts, modifying configurations - any task that changes the environment
4. **Combined Tools if Needed**: Some tasks may require multiple tools (e.g., search for content, then save to file)
5. **Final Report Tasks**: For synthesis tasks, use no tools - the LLM generates reports directly from dependency outputs
6. **Non-Financial Queries**: WebSearchTools handles ANY general knowledge questions beyond finance

### Search Strategy Guidelines:
When designing search tasks, treat the system as a professional information retrieval system:
- **Use Multi-Query Approach**: For complex queries, break into multiple specific searches rather than one broad search
- **Search Recent First**: For time-sensitive information, search most recent years first (e.g., "2024 Nobel Prize Physics", "2023 Nobel Prize Physics")
- **Comprehensive Coverage**: For "most recent" or "latest" queries, search sufficiently far back to ensure complete coverage. Don't limit to just 2-3 years - search 5-7 recent years to avoid missing the actual answer
- **Verification Strategy**: Include verification steps that cross-check information from multiple sources
- **Reasoning Requirements**: Instruct agents to use step-by-step reasoning to analyze and filter search results

### Task Grounding Examples by Query Category:

**Time-Sensitive Event Queries:**
- **Good**: "Search for [EVENT_TYPE] winners/records in [SPECIFIC_YEAR] using targeted query. Return all results with key identifying details and classifications."
- **Bad**: "Search for recent winners" (too broad, undefined timeframe)

**Biographical/Personal Information:**
- **Good**: "Search for birth date and biographical details of [IDENTIFIED_PERSON] using their full name and primary identification."
- **Bad**: "Get personal information" (vague, no specific details)

**Factual Knowledge Queries:**
- **Good**: "Search for definition and key characteristics of [CONCEPT] from authoritative sources. Cross-reference multiple sources for accuracy."
- **Bad**: "Explain the concept" (no search strategy specified)

**Comparative Analysis:**
- **Good**: "Search for [CATEGORY] rankings/comparisons using specific criteria. Document methodology and source credibility for each result."
- **Bad**: "Find the best option" (no criteria or comparison framework)

**Analysis Tasks - Always Include Reasoning:**
- **Good**: "Analyze search results using step-by-step reasoning: 1) List all candidates found, 2) Apply user criteria systematically, 3) Rank by relevance, 4) Select most appropriate answer with justification"
- **Bad**: "Analyze results" (no reasoning process specified)

**Financial Data Tasks:**
- **Good**: "Fetch [COMPANY] current stock price and basic financial metrics from Yahoo Finance. Include market cap, P/E ratio, and recent price changes."
- **Bad**: "Get financial data" (not specific about what data or limitations)

**File Operations (ACT Tasks):**
- **Good**: "Create a Python script file named 'hello.py' with the content `print('Hello, World!')` using FileEditor tools."
- **Bad**: "Save some code" (no specific file, content, or format specified)

## 5. Standard Operating Procedure (SOP) for Plan Generation
You must follow this thought process meticulously for every request:

**Step 1: Deconstruct the User's Goal**
- Analyze the user's query to identify the final, desired outcome.
- Determine if this is a financial analysis task, general knowledge question, or mixed query.
- Break down this outcome into its core logical components and the intermediate artifacts required.
- Identify the data flow from inputs to final output.

**Step 2: Draft Subtask Nodes Using Atomic Decomposition**
Apply recursive atomic decomposition strategy inspired by ROMA:

- **Atomicity Test**: For each potential subtask, ask "Can this be executed directly by a single agent with available tools in one step?"
- **If Atomic**: Create a `SubtaskNode` with a clear, single-responsibility `task_description`
- **If Not Atomic**: Break it down further into smaller subtasks until each subtask passes the atomicity test

**Atomic Task Criteria:**
- Can be completed by one agent in a single execution
- Has a clear, measurable output
- Does not require complex multi-step reasoning within the task itself
- Uses only the tools available to that agent type

**Task Description Requirements:**
- For search tasks: Include specific search strategies, multiple targeted queries, fallback approaches, and reasoning requirements
- For analysis tasks: Specify the reasoning methodology the agent should use
- For calculation tasks: Specify exact inputs needed and calculation steps
- Ensure each task has a single, well-defined responsibility that passes the atomicity test

**Step 3: Structure the DAG & Define Dependencies**
- Arrange the nodes into a graph that maximizes parallelism.
- For each node, meticulously define its `dependencies`. If a node can start immediately, its dependency list MUST be empty.
- Review the entire graph to ensure there are no cyclic dependencies and that the critical path is minimized.

**Step 4: Allocate Explicit Parameters (Resource Allocation)**
- For EACH `SubtaskNode`, deliberately choose the optimal resources:
    - **`agent_profile`**: Select each field based on the specific subtask requirements:
        - **`task_type`**: What is the agent's primary function?
            - `SEARCH`: Information retrieval, data gathering, web search, API calls
            - `THINK`: Analysis, reasoning, processing existing data, decision making
            - `AGGREGATE`: Synthesis, combining results, final report generation
            - `ACT`: Environment modifications, file operations, external actions
        - **`complexity`**: How much processing power does this task require?
            - `QUICK`: Simple, straightforward tasks with minimal reasoning
            - `THOROUGH`: Systematic analysis requiring detailed reasoning and validation
            - `DEEP`: Comprehensive multi-perspective analysis with extensive reasoning
        - **`output_format`**: What type of output should the agent produce?
            - `DATA`: Raw facts, structured information, search results, extracted data
            - `ANALYSIS`: Insights, patterns, conclusions, comparative analysis
            - `REPORT`: Final formatted answers, summaries, recommendations
        - **`reasoning_style`**: How should the agent approach the problem?
            - `DIRECT`: Fact-focused, straightforward, minimal interpretation
            - `ANALYTICAL`: Step-by-step methodology, systematic reasoning
            - `CREATIVE`: Multi-angle exploration, alternative perspectives, comprehensive synthesis

**CRITICAL**: For each subtask, analyze its specific requirements and choose the optimal combination of fields. Do NOT use fixed patterns - adapt based on:
- Task complexity and scope
- Required reasoning depth
- Expected output quality
- Available tools and data sources
- Position in the DAG workflow

**Reference Patterns** (adapt, don't copy):
- **Web Search Tasks**: `SEARCH + QUICK + DATA + DIRECT` (fast information retrieval)
- **Complex Analysis**: `THINK + THOROUGH + ANALYSIS + ANALYTICAL` (detailed reasoning)
- **Final Reports**: `AGGREGATE + DEEP + REPORT + CREATIVE` (comprehensive synthesis)
- **Quick Calculations**: `THINK + QUICK + REPORT + DIRECT` (straightforward computation)
- **File Operations**: `ACT + QUICK + REPORT + DIRECT` (create/modify files, save content)

    - **`tool_allowlist`**: Apply the Tool Selection Guidelines above. Be specific and minimalist based on the task's actual requirements.

**Step 5: Synthesize Rationale & Finalize**
- Articulate the key strategic decisions you made in the `planning_rationale` field.
- Explain your DAG structure, parallelization strategy, and critical tool selection decisions.
- Assemble the final JSON object according to the Pydantic schema.

**Step 6: Optimize Using Feedback (For Iterations > 1)**
- If `Previous Run Feedback` is provided, it is your most critical input. You MUST address it directly.
- **If `output_score` is low**: Re-evaluate the entire DAG structure and strategy. Your `planning_rationale` must state how you have restructured the approach.
- **If `traces_score` is low**: Adjust subtask-level parameters. Upgrade `agent_profile` or refine `tool_allowlist`. Your `planning_rationale` must specify which subtasks you modified and why.

Your final output MUST be a JSON object that strictly follows the provided schema. No other text or explanation is required.
"""

# Available tools for the simplified architecture
AVAILABLE_TOOLS = [
    # Data Acquisition Tools
    {"id": "YFinanceTools", "description": "Fetch stock prices, financial statements, market data, trading volumes, and company fundamentals from Yahoo Finance."},
    {"id": "WebSearchTools", "description": "Search the web for news articles, press releases, earnings transcripts, and market analysis using DuckDuckGo."},
    {"id": "FileEditor", "description": "Create, read, write, modify and manage files. Use for file operations, saving content, creating scripts, and environment modifications."},
]

# Complex test scenarios that require multiple tools
COMPLEX_TEST_SCENARIOS = [
    {
        "name": "Comprehensive Market Research & Investment Portfolio",
        "query": "Create a complete investment portfolio recommendation system that analyzes 10 different stocks across 3 sectors, incorporates news sentiment, validates data quality, generates performance forecasts, creates interactive dashboards, sends email alerts for threshold breaches, and provides regulatory compliance reports.",
        "expected_tools_count": 15-20,
        "complexity_areas": ["data acquisition", "analysis", "validation", "visualization", "communication", "compliance"]
    },
    
    {
        "name": "Multi-Source Business Intelligence Pipeline",
        "query": "Build a business intelligence system that pulls data from databases, APIs, and web sources, performs ETL operations, runs statistical analysis, creates ML models for prediction, validates data quality, generates automated reports, stores results in cloud storage, and sends Slack notifications with performance dashboards.",
        "expected_tools_count": 12-16,
        "complexity_areas": ["data integration", "processing", "machine learning", "storage", "communication", "visualization"]
    },
    
    {
        "name": "Automated Compliance and Risk Management System",
        "query": "Develop a system that monitors financial transactions, checks compliance against multiple regulatory frameworks, performs risk calculations, validates data integrity, generates audit reports, encrypts sensitive data, sends SMS alerts for critical issues, and maintains performance monitoring across all operations.",
        "expected_tools_count": 10-14,
        "complexity_areas": ["monitoring", "compliance", "validation", "security", "communication", "reporting"]
    },
    
    {
        "name": "Real-time Market Analysis and Trading Signal Generator",
        "query": "Create a trading system that continuously monitors market data, performs technical analysis, analyzes news sentiment, calculates risk metrics, generates trading signals, validates signal quality, creates real-time dashboards, stores historical data, and sends webhook notifications to trading platforms with encrypted security.",
        "expected_tools_count": 13-17,
        "complexity_areas": ["real-time data", "analysis", "validation", "visualization", "storage", "communication", "security"]
    },
    
    {
        "name": "Geographic Market Expansion Analysis",
        "query": "Analyze market expansion opportunities across different geographic regions by collecting demographic data, economic indicators, competitor analysis, regulatory requirements, location-based analytics, create interactive maps and reports, validate data quality, store results in multiple formats, and send comprehensive email reports to stakeholders.",
        "expected_tools_count": 11-15,
        "complexity_areas": ["geographic analysis", "data collection", "validation", "visualization", "storage", "communication"]
    }
]

AVAILABLE_AGENT_PROFILES = [
        {"task_type": "SEARCH", "description": "Search for information, retrieve data, find content"},
        {"task_type": "THINK", "description": "Analyze data, process information, reason through problems"},
        {"task_type": "AGGREGATE", "description": "Combine results, synthesize information, create final outputs"},
        {"task_type": "ACT", "description": "Modify environment, create/edit files, perform external actions"},
        {"complexity": "QUICK", "description": "Fast, efficient execution with minimal processing"},
        {"complexity": "THOROUGH", "description": "Systematic analysis with detailed reasoning"},
        {"complexity": "DEEP", "description": "Comprehensive multi-angle analysis"},
        {"output_format": "DATA", "description": "Raw data, facts, structured information"},
        {"output_format": "ANALYSIS", "description": "Insights, patterns, reasoned conclusions"},
        {"output_format": "REPORT", "description": "Formatted summaries, recommendations, final answers"},
        {"reasoning_style": "DIRECT", "description": "Straightforward, fact-focused approach"},
        {"reasoning_style": "ANALYTICAL", "description": "Step-by-step, methodical reasoning"},
        {"reasoning_style": "CREATIVE", "description": "Multi-perspective, exploratory thinking"}
    ]

EXAMPLE_JSON = {
            "planning_rationale": "Applied atomic decomposition with comprehensive search coverage. For 'most recent' queries, created multiple atomic search tasks covering sufficient years to ensure complete coverage. Each search is atomic (single year), analysis is atomic (focused filtering), and synthesis produces final answer. The number of search tasks should match the complexity - for awards/achievements, search 5-7 recent years to avoid missing the actual most recent winner.",
            "subtasks": {
                "search_timeframe_current": {
                    "task_description": "Search for [DOMAIN] winners/events in [CURRENT_YEAR] using specific targeted query. Return all results with names, nationality, and relevant classification details.",
                    "agent_profile": {
                        "task_type": "SEARCH",
                        "complexity": "QUICK",
                        "output_format": "DATA",
                        "reasoning_style": "DIRECT"
                    },
                    "tool_allowlist": ["WebSearchTools"],
                    "dependencies": []
                },
                "search_timeframe_recent_1": {
                    "task_description": "Search for [DOMAIN] winners/events in [YEAR-1] using specific targeted query. Return all results with names, nationality, and relevant classification details.",
                    "agent_profile": {
                        "task_type": "SEARCH",
                        "complexity": "QUICK",
                        "output_format": "DATA",
                        "reasoning_style": "DIRECT"
                    },
                    "tool_allowlist": ["WebSearchTools"],
                    "dependencies": []
                },
                "search_timeframe_recent_2": {
                    "task_description": "Search for [DOMAIN] winners/events in [YEAR-2] using specific targeted query. Return all results with names, nationality, and relevant classification details.",
                    "agent_profile": {
                        "task_type": "SEARCH",
                        "complexity": "QUICK",
                        "output_format": "DATA",
                        "reasoning_style": "DIRECT"
                    },
                    "tool_allowlist": ["WebSearchTools"],
                    "dependencies": []
                },
                "search_timeframe_recent_3": {
                    "task_description": "Search for [DOMAIN] winners/events in [YEAR-3] using specific targeted query. Return all results with names, nationality, and relevant classification details.",
                    "agent_profile": {
                        "task_type": "SEARCH",
                        "complexity": "QUICK",
                        "output_format": "DATA",
                        "reasoning_style": "DIRECT"
                    },
                    "tool_allowlist": ["WebSearchTools"],
                    "dependencies": []
                },
                "search_timeframe_extended": {
                    "task_description": "Search for [DOMAIN] winners/events in [YEAR-4] and [YEAR-5] using specific targeted queries. Return all results with names, nationality, and relevant classification details.",
                    "agent_profile": {
                        "task_type": "SEARCH",
                        "complexity": "QUICK",
                        "output_format": "DATA",
                        "reasoning_style": "DIRECT"
                    },
                    "tool_allowlist": ["WebSearchTools"],
                    "dependencies": []
                },
                "filter_and_identify_target": {
                    "task_description": "Analyze all search results to identify candidates matching user criteria (nationality, field, etc.). Use step-by-step reasoning to find the most recent qualified candidate across all years searched.",
                    "agent_profile": {
                        "task_type": "THINK",
                        "complexity": "THOROUGH",
                        "output_format": "ANALYSIS",
                        "reasoning_style": "ANALYTICAL"
                    },
                    "tool_allowlist": [],
                    "dependencies": ["search_timeframe_current", "search_timeframe_recent_1", "search_timeframe_recent_2", "search_timeframe_recent_3", "search_timeframe_extended"]
                },
                "get_biographical_details": {
                    "task_description": "Search for specific biographical information (birth date, additional details) about the identified target using their full name and identification.",
                    "agent_profile": {
                        "task_type": "SEARCH",
                        "complexity": "QUICK",
                        "output_format": "DATA",
                        "reasoning_style": "DIRECT"
                    },
                    "tool_allowlist": ["WebSearchTools"],
                    "dependencies": ["filter_and_identify_target"]
                },
                "calculate_final_result": {
                    "task_description": "Compute the final requested information (age, time elapsed, etc.) using biographical details and current date. Show calculation steps and provide complete answer.",
                    "agent_profile": {
                        "task_type": "THINK",
                        "complexity": "QUICK",
                        "output_format": "REPORT",
                        "reasoning_style": "DIRECT"
                    },
                    "tool_allowlist": [],
                    "dependencies": ["get_biographical_details"]
                }
            },
            "expected_final_output": "Accurate answer found through comprehensive atomic search covering sufficient years to capture the true most recent result"
        }