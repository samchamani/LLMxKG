from agents import Agent
from ollama import Client
import os
import json
from dotenv import load_dotenv
import agents.prompts as prompts
from typing import Literal, List
from utils import FormatError

load_dotenv()
os.environ["NO_PROXY"] = "localhost,127.0.0.1"
AgentKey = Literal[
    "llama3.2",
    "llama3.2:3b-instruct-fp16",
    "llama3.1:8b-instruct-q6_K",
    "gemma3:12b",
]


class AgentOllama(Agent):
    def __init__(
        self,
        model: AgentKey,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.model = model
        host = os.getenv("OLLAMA_HOST", "localhost")
        port = os.getenv("OLLAMA_PORT", "11434")
        self.client = Client(host=f"http://{host}:{port}")

    def retrieve_queries(self, prompt):
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": prompts.system_retrieve_queries,
                },
                {"role": "user", "content": prompt},
            ],
            format="json",
        ).message.content
        data: dict = json.loads(response)
        self._check_format(data, ["queries"])
        return data

    def rate_relationships(self, prompt, entity, relationships):
        if not len(relationships):
            return {"scores": [], "reason": "No relationships to rate"}
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": prompts.system_rate_relationships,
                },
                {
                    "role": "user",
                    "content": prompts.user_rate_relationships(
                        prompt, entity, relationships
                    ),
                },
            ],
            format="json",
        ).message.content
        data: dict = json.loads(response)
        self._check_format(data, ["scores", "reason"])
        return data

    def rate_entities(self, prompt, entities):
        if not len(entities):
            return {"scores": [], "reason": "No entities to rate"}
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": prompts.system_rate_entities,
                },
                {
                    "role": "user",
                    "content": prompts.user_rate_entities(prompt, entities),
                },
            ],
            format="json",
        ).message.content
        data: dict = json.loads(response)
        self._check_format(data, ["scores", "reason"])
        return data

    def judge_path(self, prompt, path, context: List[dict] = []):
        userMessage = {
            "role": "user",
            "content": prompts.user_answer_short_relation(prompt, path),
        }
        systemMessage = {
            "role": "system",
            "content": prompts.system_judge_path_short_relation,
        }
        messages = [systemMessage] + context + [userMessage]
        response = self.client.chat(
            model=self.model,
            messages=messages,
            format="json",
        ).message.content
        messages.append({"role": "assitant", "content": response})
        data: dict = json.loads(response)
        self._check_format(data, ["canAnswer", "reason"])
        return data, messages[1:]

    def answer(self, prompt, path=None, context: List[dict] = []):
        if path == None:
            return self.client.chat(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt},
                ],
            ).message.content
        messages = context + [
            {"role": "system", "content": prompts.system_answer_short_relation},
            {
                "role": "user",
                "content": prompts.user_answer_short_relation(prompt, path),
            },
        ]
        response = self.client.chat(
            model=self.model,
            messages=messages,
            format="json",
        ).message.content
        data: dict = json.loads(response)
        self._check_format(data, ["answer"])
        return data

    @staticmethod
    def _check_format(dict: dict, keys: List[str]):
        missing = [key for key in keys if key not in dict]
        if missing:
            print("Wrong format:")
            print(dict)
            raise FormatError(f"The following keys are missing: {missing}")
