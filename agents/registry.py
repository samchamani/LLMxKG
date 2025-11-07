from .Agent import Agent
from .AgentOllama import AgentOllama, AgentKey

agents: list[AgentKey] = [
    "llama3.2",
    "llama3.2:3b-instruct-fp16",
    "llama3.1:8b-instruct-q6_K",
    "gemma3:12b",
]


def getAgent(key: AgentKey) -> Agent:
    dict = {
        "llama3.2": lambda: AgentOllama(model="llama3.2"),
        "llama3.2:3b-instruct-fp16": lambda: AgentOllama(
            model="llama3.2:3b-instruct-fp16"
        ),
        "llama3.1:8b-instruct-q6_K": lambda: AgentOllama(
            model="llama3.1:8b-instruct-q6_K"
        ),
        "gemma3:12b": lambda: AgentOllama(model="gemma3:12b"),
    }
    return dict[key]()
