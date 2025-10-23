from Agent import Agent
from AgentLlama import AgentLlama
from typing import Literal, List
import json

AgentKey = Literal["llama3.2", "llama3.2:3b-instruct-fp16", "llama3.1:8b-instruct-q6_K"]
agents: list[AgentKey] = [
    "llama3.2",
    "llama3.2:3b-instruct-fp16",
    "llama3.1:8b-instruct-q6_K",
]


def getAgent(key: AgentKey) -> Agent:
    dict = {
        "llama3.2": lambda: AgentLlama(model="llama3.2"),
        "llama3.2:3b-instruct-fp16": lambda: AgentLlama(
            model="llama3.2:3b-instruct-fp16"
        ),
        "llama3.1:8b-instruct-q6_K": lambda: AgentLlama(
            model="llama3.1:8b-instruct-q6_K"
        ),
    }
    return dict[key]()


def getBest(items: list, ratings: list, max: int):
    return [
        item
        for _, item in sorted(zip(ratings, items), key=lambda x: x[0], reverse=True)
    ][:max]


def printPaths(paths: List[List[dict]]):
    for index, path in enumerate(paths):
        print(f" Path {index}:")
        for part in path:
            print(f"\t{json.dumps(part)}")
        print("")


def fixScoreArray(scores: list, relationsship_length):
    scores_length = len(scores)
    if scores_length > relationsship_length:
        return scores[:relationsship_length]
    else:
        return scores + [0.0] * (relationsship_length - scores_length)
