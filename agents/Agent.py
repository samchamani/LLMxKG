from abc import ABC, abstractmethod
from typing import Dict, List, Literal


class Agent(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def retrieve_queries(self, prompt: str) -> Dict[Literal["entities"], List[str]]:
        """
        The agent extracts key words or related words from the prompt\\
        and returns them as json in the format

        ```
        {
            "entities": [str]
        }
        ```
        """
        pass

    @abstractmethod
    def rate_relationships(
        self, prompt: str, entity: dict, relationships: List[dict]
    ) -> List[float]:
        """
        The agent will rate the relationships based on the given prompt and the originating entity,\\
        by assigning a score to each relationship and return a list of scores of size `len(paths)`\\
        where each index represents the score of the relationship with the same index.
        """
        pass

    @abstractmethod
    def rate_entities(self, prompt: str, entities: List[dict]) -> List[float]:
        """
        The agent will rate the entities based on the given prompt, by assigning a score\\
        to each entity and return a list of scores of size `len(paths)` where each index\\
        represents the score of the entity with the same index.
        """
        pass

    @abstractmethod
    def judge_path(self, prompt: str, path: List[dict]) -> dict:
        """
        The agent reasons over the prompt and path and decides whether it has\\
        enough information to answer the prompt based on the path data.\\
        If the agent can answer, then this will return `True`.
        """

    @abstractmethod
    def answer(self, prompt: str, path: List[dict] | None) -> dict:
        """
        The agent answers the given prompt. If `path` is given, it will attempt\\
        to use the path data to answer the question, otherwise it will solely use\\
        its encoded knowledge.
        """
        pass
