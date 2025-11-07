from abc import ABC, abstractmethod
from typing import List


class Graph(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def read(self, data_list: List[dict], labels: List[str] = []) -> list:
        pass

    @abstractmethod
    def find(self, data_list: List[str], labels: List[str] = []) -> list:
        pass

    @abstractmethod
    def read_link(
        self,
        from_list: List[dict] = [],
        relation: str | dict = "",
        to_list: List[dict] = [],
        ignore_direction=False,
    ) -> list:
        pass

    @abstractmethod
    def read_neighbors(
        self, data_list: List[dict], rel_type="", ignore_direction=True
    ) -> list:
        pass
