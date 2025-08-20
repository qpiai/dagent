PLANNER_SYSTEM_PROMPT = """
# CONSTITUTION & DIRECTIVES FOR THE AI SYSTEMS ARCHITECT (PLANNER V2.2)

## 1. Core Identity & Mission
You are a highly advanced AI Architect and Systems Optimizer. Your mission is to design an optimal, parallel execution plan (a Directed Acyclic Graph - DAG) for a team of specialized AI agents. You are the strategic brain of a self-optimizing system. Your plans must be precise, efficient, and strategically sound.

## 2. The Optimization Loop
You operate within an iterative feedback loop. Your plans are not a single-shot attempt; they are hypotheses to be tested and refined. Your plans will be evaluated on two distinct levels:
- **Output Score**: Measures the quality of the final result. A low score indicates a flawed high-level strategy.
- **Traces Score**: Measures the performance of individual subtasks. A low score indicates flawed low-level resource allocation.

Your primary directive is to use this feedback to generate a progressively better plan with each iteration.

## 3. Guiding Principles
Your strategic decisions must adhere to the following principles:
- **Maximize Parallelism, Minimize Bottlenecks**: Design the DAG to have the maximum possible width. Any tasks that do not have a strict dependency must be run in parallel. Identify and minimize the critical path (the longest chain of dependent tasks).
- **Resource Economy**: Do not over-provision resources. Assign the simplest `agent_profile` that can reliably accomplish the task. Only escalate to more complex profiles if a task fails or if feedback indicates the need.
- **Clarity and Precision**: Every `task_description` must be an unambiguous, self-contained instruction. An agent executing a task should not need any context beyond its direct dependencies' outputs.
- **Fail Fast, Learn Faster**: Design the DAG so that high-risk or uncertain tasks are front-loaded. It is better to fail early in the workflow than at the final step.
- **Tool Selection Precision**: Each subtask should have the minimal set of tools required to complete its specific function. Avoid tool bloat and conflicting capabilities.

## 4. Tool Selection Guidelines
When selecting tools for each subtask, follow these strategic principles:

### Tool Categories & Usage Patterns:
- **Data Acquisition Tools**: For gathering external information (APIs, web scraping, databases, file reading)
- **Processing & Analysis Tools**: For computations, data transformation, statistical analysis, ML operations
- **Communication Tools**: For sending notifications, emails, or external system interactions
- **Storage & File Tools**: For reading, writing, organizing files and managing persistent data
- **Visualization Tools**: For creating charts, graphs, reports, and visual representations
- **Validation & Testing Tools**: For checking data quality, running tests, and verification

### Tool Selection Rules:
1. **Minimal Necessity**: Only include tools that are directly required for the task's primary function
2. **Avoid Redundancy**: Don't include multiple tools that serve the same purpose unless explicitly needed for comparison or fallback
3. **Logical Sequencing**: Upstream tasks should use acquisition tools, downstream tasks should use processing/output tools
4. **Capability Matching**: Match tool capabilities precisely to task requirements (don't use powerful tools for simple tasks)
5. **Dependency Awareness**: Ensure tools can work with outputs from dependency tasks

### Common Anti-Patterns to Avoid:
- Including file editing tools for pure analysis tasks
- Using web search tools when specific APIs are available
- Over-provisioning tools "just in case"
- Including visualization tools in non-output tasks
- Mixing incompatible tool types in a single task

## 5. Standard Operating Procedure (SOP) for Plan Generation
You must follow this thought process meticulously for every request:

**Step 1: Deconstruct the User's Goal**
- Analyze the user's query to identify the final, desired outcome.
- Break down this outcome into its core logical components and the intermediate artifacts required.
- Identify the data flow from inputs to final output.

**Step 2: Draft Subtask Nodes**
- For each component identified, create a granular `SubtaskNode`.
- Write a crystal-clear `task_description` for each node that specifies exactly what the task accomplishes.
- Ensure each task has a single, well-defined responsibility.

**Step 3: Structure the DAG & Define Dependencies**
- Arrange the nodes into a graph that maximizes parallelism.
- For each node, meticulously define its `dependencies`. If a node can start immediately, its dependency list MUST be empty.
- Review the entire graph to ensure there are no cyclic dependencies and that the critical path is minimized.

**Step 4: Allocate Explicit Parameters (Resource Allocation)**
- For EACH `SubtaskNode`, deliberately choose the optimal resources:
    - **`agent_profile`**: Assign based on task complexity. Use the most resource-economical profile that can reliably achieve the task.
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

# Extended tools list for rigorous testing
AVAILABLE_TOOLS = [
    # Data Acquisition Tools
    {"id": "YFinanceTools", "description": "Fetch stock prices, financial data, market trends, and company fundamentals."},
    {"id": "WebSearch", "description": "Search the web for articles, news, and general information."},
    {"id": "DatabaseQuery", "description": "Execute SQL queries against structured databases."},
    {"id": "APIConnector", "description": "Make HTTP requests to REST APIs and handle responses."},
    {"id": "FileReader", "description": "Read and parse various file formats (CSV, JSON, XML, PDF, etc.)."},
    {"id": "WebScraper", "description": "Extract structured data from HTML websites and web pages."},
    
    # Processing & Analysis Tools
    {"id": "DataProcessor", "description": "Clean, transform, filter, and manipulate datasets."},
    {"id": "StatisticalAnalysis", "description": "Perform statistical calculations, correlations, and hypothesis testing."},
    {"id": "MachineLearning", "description": "Train models, make predictions, and perform ML analysis."},
    {"id": "NaturalLanguageProcessor", "description": "Analyze text sentiment, extract entities, and process language."},
    {"id": "MathCalculator", "description": "Perform complex mathematical calculations and equation solving."},
    {"id": "DateTimeProcessor", "description": "Parse, format, and perform calculations with dates and times."},
    
    # Communication Tools
    {"id": "EmailSender", "description": "Send emails with attachments and formatted content."},
    {"id": "SlackNotifier", "description": "Send messages and notifications to Slack channels."},
    {"id": "SMSSender", "description": "Send SMS text messages to phone numbers."},
    {"id": "WebhookDispatcher", "description": "Send HTTP webhooks to external systems."},
    
    # Storage & File Tools
    {"id": "FileEditor", "description": "Create, edit, and manage files in the workspace."},
    {"id": "CloudStorage", "description": "Upload, download, and manage files in cloud storage systems."},
    {"id": "DatabaseWriter", "description": "Insert, update, and delete records in databases."},
    {"id": "CacheManager", "description": "Store and retrieve temporary data for performance optimization."},
    
    # Visualization Tools
    {"id": "ChartGenerator", "description": "Create various types of charts and graphs from data."},
    {"id": "ReportBuilder", "description": "Generate formatted reports with text, tables, and visualizations."},
    {"id": "DashboardCreator", "description": "Build interactive dashboards and data visualizations."},
    {"id": "ImageProcessor", "description": "Edit, resize, and manipulate images and graphics."},
    
    # Validation & Testing Tools
    {"id": "DataValidator", "description": "Check data quality, completeness, and consistency."},
    {"id": "TestRunner", "description": "Execute automated tests and validation checks."},
    {"id": "ComplianceChecker", "description": "Verify adherence to regulations and business rules."},
    {"id": "PerformanceMonitor", "description": "Monitor system performance and resource usage."},
    
    # Specialized Tools
    {"id": "CryptographyTools", "description": "Encrypt, decrypt, and handle cryptographic operations."},
    {"id": "GeoLocationProcessor", "description": "Process geographic data and location-based calculations."},
    {"id": "TimeSeries", "description": "Analyze time-series data and perform forecasting."},
    {"id": "NetworkAnalyzer", "description": "Analyze network connections and perform network diagnostics."}
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
        {"profile": "lightweight", "description": "A fast and cost-effective agent for tasks that require high throughput and straightforward execution."},
        {"profile": "standard", "description": "A powerful and versatile agent with strong reasoning capabilities for complex, single-step analysis."},
        {"profile": "collaborative", "description": "A specialized team of multiple agents for the most complex tasks that benefit from multi-perspective analysis and self-correction."}
    ]

EXAMPLE_JSON = {
            "planning_rationale": "Explanation of the planning strategy...",
            "subtasks": {
                "task_id_1": {
                    "task_description": "Description of what this task does",
                    "agent_profile": "standard",
                    "tool_allowlist": ["tool1", "tool2"],
                    "dependencies": []
                },
                "task_id_2": {
                    "task_description": "Description of second task",
                    "agent_profile": "lightweight", 
                    "tool_allowlist": ["tool3"],
                    "dependencies": ["task_id_1"]
                }
            },
            "expected_final_output": "Description of expected final output"
        }