# Dagent 🤖

A powerful multi-agent DAG (Directed Acyclic Graph) framework that intelligently breaks down complex queries into atomic tasks and orchestrates AI agents to solve them efficiently through parallel execution.

## 🚀 Key Features

- **🔄 DAG-based Parallel Execution** - Maximizes performance by running independent tasks simultaneously
- **🧠 Intelligent Planning** - Automatically decomposes queries into optimal atomic tasks
- **⚖️ Actor-Critic Architecture** - Built-in quality control with judge evaluation and retry logic
- **🎯 Dynamic Agent Profiles** - Generates specialized agent profiles based on task complexity and type
- **🔗 Smart Context Engineering** - Intelligently passes context between dependent tasks
- **🛠️ Multi-Tool Integration** - Financial data, web search, and file operations

## 📋 Quick Start

### Prerequisites
- Python 3.8+
- At least one AI provider API key (OpenAI or Google)

### Installation

```bash
git clone https://github.com/your-username/dagent.git
cd dagent
pip install -r requirements.txt
```

### Environment Setup

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Configure your API keys in `.env`:
```env
# AI Model Providers (need at least one)
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Web Search (required)
EXA_API_KEY=your_exa_api_key_here

# Optional: Tracing and observability
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

### Running Your First Query

```python
import asyncio
from src.framework import AgenticDAG

async def main():
    # Initialize the framework
    framework = AgenticDAG()

    # Execute a complex query
    result = await framework.execute(
        "Analyze Apple's stock performance over the last year and create a comprehensive report"
    )

    if result["success"]:
        print("✅ Task completed successfully!")
        print(f"📊 Summary: {result['summary']}")
    else:
        print(f"❌ Task failed: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🏗️ Architecture Deep Dive

### 1. DAG-based Parallel Execution
Dagent converts your query into a **Directed Acyclic Graph** where:
- **Nodes** represent atomic tasks (each handled by a specialized agent)
- **Edges** represent dependencies between tasks
- **Independent tasks run in parallel** to maximize throughput
- **Dependencies ensure correct execution order**

Example DAG flow:
```
[Search Financial Data] ──┐
                          ├─→ [Analyze Trends] ──┐
[Search News Articles] ───┘                     ├─→ [Generate Report] ──→ [Save to File]
                                                 │
[Get Analyst Reports] ──────────────────────────┘
```

### 2. Intelligent Planning System
The **Planner** analyzes your query and:
- **Categorizes query type** (financial, research, analysis, etc.)
- **Decomposes into atomic tasks** that can be executed independently
- **Selects optimal tools** for each task
- **Establishes dependencies** for logical execution flow
- **Chooses agent profiles** based on task complexity

### 3. Actor-Critic with Judge System
Each task goes through quality control:
- **Actor**: The primary agent executes the task
- **Critic (Judge)**: Evaluates output quality and provides feedback
- **Retry Logic**: Failed tasks retry with specific judge feedback
- **Quality Assurance**: Ensures high-quality outputs before proceeding

### 4. Dynamic Profile Generation
Agents are automatically configured with:
- **Task Type**: SEARCH, THINK, AGGREGATE, or ACT
- **Complexity Level**: QUICK, THOROUGH, or DEEP
- **Output Format**: DATA, ANALYSIS, or REPORT
- **Reasoning Style**: DIRECT, ANALYTICAL, or CREATIVE

### 5. Smart Context Engineering
- **Dependency Resolution**: Tasks receive relevant outputs from predecessors
- **Context Filtering**: Only relevant information is passed to avoid token waste
- **State Management**: Global context tracks file modifications and system state

## 🛠️ Available Tools

### YFinanceTools
- Stock prices and financial metrics
- Company fundamentals and analyst recommendations
- Historical data and market information

### WebSearchTools
- Web content retrieval via Exa API
- News articles and research papers
- Market analysis and sentiment data

### FileEditorTools
- Create, read, and modify files
- Generate scripts and reports
- Save analysis results

## 🎯 Agent Types Explained

### SEARCH Agents
- **Purpose**: Information retrieval and data gathering
- **Tools**: WebSearchTools, YFinanceTools
- **Output**: Structured data and search results

### THINK Agents
- **Purpose**: Analysis, reasoning, and interpretation
- **Tools**: None (pure reasoning)
- **Output**: Insights, analysis, and conclusions

### AGGREGATE Agents
- **Purpose**: Combine and synthesize information
- **Tools**: Minimal (data combination focused)
- **Output**: Comprehensive summaries and reports

### ACT Agents
- **Purpose**: File operations and system modifications
- **Tools**: FileEditorTools
- **Output**: Created files, modified system state

## 📊 Example Use Cases

### Financial Analysis
```python
result = await framework.execute(
    "Compare Tesla and Apple's Q4 performance, including stock trends, "
    "earnings analysis, and analyst sentiment. Create a detailed report."
)
```

### Market Research
```python
result = await framework.execute(
    "Research the latest AI chip market trends, identify key players, "
    "analyze competitive landscape, and project future growth."
)
```

### Data Analysis & Visualization
```python
result = await framework.execute(
    "Get NVIDIA's stock data for the past 2 years, create visualizations "
    "showing key trends, and generate an executive summary."
)
```

## 🔍 Monitoring & Debugging

### Generated Plans
Every execution creates `generated_plan.json` showing:
- Query decomposition rationale
- Task structure and dependencies
- Agent profile assignments
- Tool allocations

### Execution Flow
Watch real-time execution with:
- Round-by-round task execution
- Parallel task coordination
- Judge evaluations and retries
- Context flow between tasks

### Performance Metrics
Track execution with:
- Task completion times
- Success/failure rates
- Judge evaluation scores
- Total execution time

## 🚦 Best Practices

### Query Formulation
- **Be specific** about what you want
- **Include output format** preferences (report, analysis, data)
- **Mention key constraints** (time periods, data sources)

### Error Handling
- Check `result["success"]` before accessing data
- Review `generated_plan.json` if execution fails
- Use specific, actionable queries for better results

### Performance Optimization
- Queries with natural parallelism perform best
- Complex analysis benefits from DEEP complexity agents
- File operations should be explicit in your request

## 📁 Project Structure

```
dagent/
├── src/
│   ├── framework.py          # Main entry point
│   ├── planner/              # Query planning and decomposition
│   │   ├── planner.py        # Core planning logic
│   │   └── prompts.py        # Planning prompts and examples
│   ├── dag/                  # DAG construction and management
│   │   └── dag.py            # DAG building from plans
│   ├── kernel/               # Agent orchestration and execution
│   │   ├── kernel.py         # Main execution engine
│   │   ├── judge.py          # Quality evaluation system
│   │   └── profiles.py       # Agent profile generation
│   ├── tools/                # Available agent tools
│   │   ├── yfinance_tools.py # Financial data tools
│   │   ├── web_search.py     # Web search capabilities
│   │   └── file_editor.py    # File operation tools
│   └── utils/                # Utilities and helpers
│       └── model_factory.py  # AI model selection
├── main.py                   # Example usage
├── .env.example              # Environment template
└── requirements.txt          # Dependencies
```

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on how to contribute to Dagent.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Dagent**: Intelligent multi-agent orchestration for complex problem solving 🚀