from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.openai import OpenAILike
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import os
import asyncio
from dotenv import load_dotenv
from .prompts import PLANNER_SYSTEM_PROMPT, AVAILABLE_AGENT_PROFILES, EXAMPLE_JSON, AVAILABLE_TOOLS

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model_id = os.getenv("MODEL_ID")
base_url = os.getenv("BASE_URL")


class SubtaskNode(BaseModel):
    """Defines a single node in the execution DAG."""
    task_description: str
    agent_profile: str
    tool_allowlist: List[str]
    dependencies: List[str] = []


class Plan(BaseModel):
    """The complete execution plan and strategic rationale."""
    planning_rationale: str
    subtasks: Dict[str, SubtaskNode]
    expected_final_output: str


class Planner:
    def __init__(self):
        self._agent = None
    
    @property
    def agent(self):
        if self._agent is None:
            self._agent = Agent(
                model=OpenAILike(
                    id=model_id,
                    base_url=base_url,
                    temperature=0.1,
                    max_tokens=10000,
                    top_p=0.9
                ),
                description=PLANNER_SYSTEM_PROMPT,
                markdown=False,
                debug_mode=False,
                add_datetime_to_instructions=True,
                exponential_backoff=True,
                delay_between_retries=2,
                use_json_mode=True,
            )
        return self._agent

    async def create_plan(
        self,
        user_query: str,
        available_profiles: List[Dict],
        available_tools: List[Dict],
        feedback: Optional[Dict] = None,
        previous_plan: Optional[Plan] = None,
        iteration: int = 1
    ) -> Plan:
        """Creates a plan and returns a validated Pydantic Plan object"""

        profiles_text = "\n".join([
            f"- **profile**: '{p['profile']}', **description**: \"{p['description']}\""
            for p in available_profiles
        ])
        tools_text = "\n".join([
            f"- **id**: '{t['id']}', **description**: \"{t['description']}\""
            for t in available_tools
        ])

        feedback_block = ""
        if feedback:
            feedback_block = f"""
            - **Output Score (Overall Strategy)**: {feedback.get('output_score', 'N/A')}
            - **Traces Score (Subtask Efficiency)**: {feedback.get('traces_score', 'N/A')}
            - **Evaluator Feedback**: {feedback.get('evaluator_feedback', 'N/A')}
            """

        previous_plan_block = ""
        if previous_plan:
            previous_plan_block = f"""
**Previous Plan to Improve:**
```json
{previous_plan.model_dump_json(indent=2)}
```

Based on the feedback above, you should modify and improve this existing plan rather than creating a completely new one. Focus on addressing the specific issues mentioned in the evaluator feedback while preserving the good aspects of the original plan.
            """
         
        prompt = f"""
---
## CURRENT TASK BRIEFING (ITERATION #{iteration}) ##

**1. User Query:**
"{user_query}"

**2. Available Resources:**
### Agent Profiles:
{profiles_text}

### Tools:
{tools_text}

**3. Feedback from Previous Iteration:**
{feedback_block}

{previous_plan_block}

**4. REQUIRED OUTPUT FORMAT**
You MUST respond with ONLY a valid JSON object that follows this exact structure:

```json
{json.dumps(EXAMPLE_JSON, indent=2)}
```

IMPORTANT RULES:
- Return ONLY the JSON object, no additional text
- All subtask IDs should be descriptive snake_case names
- Dependencies should reference actual subtask IDs from your plan
- Use only the agent profiles and tools listed above
- The planning_rationale should explain your strategy

---

Please generate the optimized JSON plan based on this briefing and your core instructions.
"""

        print("Calling planner Agent")
        response = await self.agent.arun(prompt)
        print("Planner Agent response received successfully.")

        try:
            raw_text = response.content
            json_text = raw_text.strip()
            
            if '```json' in json_text:
                start = json_text.find('```json') + 7
                end = json_text.find('```', start)
                if end != -1:
                    json_text = json_text[start:end]
            elif '```' in json_text:
                parts = json_text.split('```')
                if len(parts) >= 3:
                    json_text = parts[1]
            
            json_text = json_text.strip()
            
            if not (json_text.startswith('{') and json_text.endswith('}')):
                start_idx = json_text.find('{')
                end_idx = json_text.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_text = json_text[start_idx:end_idx + 1]
            
            plan_dict = json.loads(json_text)
            validated_plan = Plan(**plan_dict)
            print(f"Plan type: {type(validated_plan)}")
            
            return validated_plan
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Extracted text: {json_text}")
            print(f"Raw response: {raw_text}")
            raise
        except Exception as e:
            print(f"Error creating plan: {e}")
            raise


async def main():
    planner = Planner()

    print("=== Scenario 1: Basic Plan Generation ===")
    user_query_1 = "Analyze Tesla's Q4 2024 performance and provide an investment recommendation."

    plan_1 = await planner.create_plan(
        user_query=user_query_1,
        available_profiles=AVAILABLE_AGENT_PROFILES,
        available_tools=AVAILABLE_TOOLS,
    )

    print("\n✅ Generated Plan:")
    print(plan_1.model_dump_json(indent=2))

    print("\n=== Scenario 2: Plan with Feedback ===")
    mock_feedback = {
        "output_score": 0.8,
        "traces_score": 0.7,
        "evaluator_feedback": "The plan is too complex and requires too many steps. Please simplify it."
    }

    plan_2 = await planner.create_plan(
        user_query=user_query_1,
        available_profiles=AVAILABLE_AGENT_PROFILES,
        available_tools=AVAILABLE_TOOLS,
        feedback=mock_feedback,
        previous_plan=plan_1,
        iteration=2
    )

    print("\n✅ Generated Plan with Feedback:")
    print(plan_2.model_dump_json(indent=2))

    print("\n=== Validation Test ===")
    print(f"Plan 1 type: {type(plan_1)}")
    print(f"Plan 1 has {len(plan_1.subtasks)} subtasks")
    print(f"Subtask types: {[type(node) for node in plan_1.subtasks.values()]}")


if __name__ == "__main__":
    asyncio.run(main())