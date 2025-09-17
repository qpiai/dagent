# Implementation Guide: Minimal TravelPlanner System

This guide provides step-by-step instructions for the next Claude instance to build a working TravelPlanner system using the existing foundation.

## Phase 1: Tool Execution (Priority 1)

### Create `src/tools.py`

```python
"""
Simple tool executors for TravelPlanner tasks.
Each function takes reference data and makes LLM-powered selections.
"""

class SimpleTravelTools:
    def __init__(self):
        # Simple LLM agent for all tool calls
        self.agent = Agent(
            model=OpenAILike(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
            description="Travel planning assistant"
        )
    
    async def execute_flights(self, task_node, flight_data, context):
        """Select flight from available options."""
        # Simple prompt with flight options
        # Return: {'selection': flight_info, 'cost': price, 'reasoning': why}
    
    async def execute_hotels(self, task_node, hotel_data, context):
        """Select accommodation from available options."""  
        # Simple prompt with hotel options
        # Return: {'selection': hotel_info, 'cost': price, 'reasoning': why}
    
    async def execute_attractions(self, task_node, attraction_data, context):
        """Select attractions from available options."""
        # Simple prompt with attraction options  
        # Return: {'selection': attractions_list, 'cost': total, 'reasoning': why}
    
    async def execute_restaurants(self, task_node, restaurant_data, context):
        """Select restaurants from available options."""
        # Simple prompt with restaurant options
        # Return: {'selection': restaurants_by_meal, 'cost': total, 'reasoning': why}
```

**Key Points:**
- Use direct LLM prompts, no complex coordination
- Include budget constraints in prompts
- Return consistent format from all tools
- Keep prompts simple but include relevant context

### Reference Data Filtering
```python
def filter_reference_data(reference_data, tool_name):
    """Simple filtering of reference data by tool type."""
    tool_mapping = {
        'flights': 'Flight',
        'accommodations': 'Accommodation',
        'attractions': 'Attraction', 
        'restaurants': 'Restaurant'
    }
    return [item for item in reference_data if item.get('type') == tool_mapping.get(tool_name)]
```

## Phase 2: Result Aggregation (Priority 2)

### Create `src/simple_aggregator.py`

```python
"""
Simple aggregation of tool results into TravelPlanner format.
NO complex LLM aggregation - just format the data correctly.
"""

def aggregate_to_travelplanner(query, tool_results, budget):
    """Convert tool results to exact TravelPlanner schema."""
    
    # Extract metadata from query
    metadata = {
        'org': extract_origin(query),
        'dest': extract_destination(query), 
        'days': extract_days(query),
        'people_number': extract_people(query),
        'budget': budget,
        'query': query,
        'level': 'easy'  # Default
    }
    
    # Build daily itinerary
    daily_plan = build_daily_itinerary(tool_results, metadata['days'])
    
    # Return exact TravelPlanner format
    return [
        metadata,           # Index 0
        daily_plan,         # Index 1  
        {}, {}, {}, {}, {}, {}  # Indices 2-7 (required padding)
    ]

def build_daily_itinerary(tool_results, num_days):
    """Build day-by-day itinerary from tool results."""
    # Key: Handle the exact format requirements
    # - 'days' field (not 'day')
    # - 'current_city' patterns: 'from A to B', 'B', 'from B to A'
    # - Attraction format: 'Name, City;Name2, City;' (semicolon-separated)
    # - Use '-' for missing items
```

**Critical Format Details:**
- Day 1: `'current_city': 'from Origin to Destination'`
- Middle days: `'current_city': 'Destination'` 
- Last day: `'current_city': 'from Destination to Origin'`
- Attractions: Always end with semicolon: `'Attraction 1, City;Attraction 2, City;'`
- Missing meals: Use `'-'` not empty strings

## Phase 3: Main Execution (Priority 3)

### Create `main.py`

```python
"""
Main entry point - ties everything together using working components.
"""

async def execute_travel_query(query_data):
    """Execute single travel query using simple approach."""
    
    # Step 1: Use working planner
    planner = TravelPlanner()
    plan = await planner.create_plan(query_data.query, query_data.reference_information)
    
    # Step 2: Use working DAG for execution order
    dag = build_dag_from_plan(plan)  # This function exists
    execution_order = dag.get_execution_rounds()
    
    # Step 3: Execute tools in order
    tools = SimpleTravelTools()
    results = {}
    
    for round_tasks in execution_order:
        for task_id in round_tasks:
            task_node = plan.task_nodes[task_id]
            
            # Filter reference data for this tool
            tool_data = filter_reference_data(query_data.reference_information, task_node.tool_name)
            
            # Execute tool
            if task_node.tool_name == 'flights':
                result = await tools.execute_flights(task_node, tool_data, {})
            elif task_node.tool_name == 'accommodations':
                result = await tools.execute_hotels(task_node, tool_data, {})
            # ... etc
            
            results[task_id] = result
    
    # Step 4: Aggregate results
    final_output = aggregate_to_travelplanner(
        query_data.query, 
        results, 
        extract_budget(query_data.query)
    )
    
    return final_output

# Main execution
if __name__ == "__main__":
    # Load dataset using working loader
    loader = TravelPlannerDatasetLoader()
    queries = loader.load_dataset('validation', max_samples=1)
    
    # Execute first query
    result = await execute_travel_query(queries[0])
    
    # Save result
    with open('output.json', 'w') as f:
        json.dump(result, f, indent=2)
```

## Common Pitfalls to Avoid

### 1. TravelPlanner Schema Errors
- **Wrong field names**: Use `'days'` not `'day'`
- **Wrong city format**: Follow the 3 patterns exactly
- **Missing semicolons**: Attractions must end with `;`
- **Wrong array length**: Must be exactly 8 elements

### 2. Reference Data Issues  
- **Type field**: Reference data uses `'type': 'Flight'` etc.
- **Empty data**: Handle cases where no data available for a tool
- **Data format**: Reference data is list of dicts, not nested structure

### 3. LLM Response Handling
- **JSON parsing**: LLMs don't always return valid JSON
- **Error handling**: Tool execution can fail
- **Fallbacks**: Have default responses for failures

## Testing Strategy

### 1. Test Each Component
```python
# Test tool execution
tools = SimpleTravelTools()
result = await tools.execute_flights(task_node, flight_data, {})
print(f"Flight result: {result}")

# Test aggregation
final = aggregate_to_travelplanner(query, results, budget)
print(f"Final format valid: {validate_travelplanner_format(final)}")
```

### 2. Test Full Pipeline
- Load 1 validation query
- Execute end-to-end
- Verify output format
- Check against expected TravelPlanner schema

### 3. Debug with Prints
```python
print(f"Plan created: {len(plan.task_nodes)} tasks")
print(f"Execution order: {execution_order}")
print(f"Tool results: {list(results.keys())}")
print(f"Final output length: {len(final_output)}")
```

## Success Criteria

✅ **Working Pipeline**: Query → Plan → Execute → Output  
✅ **Valid Format**: Output matches TravelPlanner schema exactly  
✅ **No Errors**: Handles reference data and LLM responses gracefully  
✅ **Simple Code**: ~300 lines total, easy to understand and debug  

## File Structure After Implementation
```
src/
├── tools.py              ← NEW: Simple tool executors
├── simple_aggregator.py  ← NEW: Format results  
├── dag/dag.py            ← EXISTS: DAG structure
├── planner/planner.py    ← EXISTS: Plan creation
└── models.py             ← EXISTS: Schemas

main.py                   ← NEW: Main entry point
utils/dataset_loader.py   ← EXISTS: Data loading
```

This approach uses the working foundation and adds only the minimal necessary components to get TravelPlanner working.