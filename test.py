from agno.agent import Agent
from agno.models.openai import OpenAILike

agent = Agent(model=OpenAILike(id="FuseAI/FuseO1-DeepSeekR1-QwQ-SkyT1-32B-Preview", base_url="http://34.58.1.42:8081/v1"), markdown=True)

agent.print_response("Share a 2 sentence horror story")