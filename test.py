from agno.agent import Agent
from agno.models.vllm import vLLM

agent = Agent(
    model=vLLM(
        id="FuseAI/FuseO1-DeepSeekR1-QwQ-SkyT1-32B-Preview",
        base_url="http://34.58.1.42:8081"  # vLLM doesn't require real auth
    )
)
agent.run("Hello, how are you?")
