from typing import Literal
from .Graph import Graph
from .GraphNeo4j import GraphNeo4j
from .GraphWikidata import GraphWikidata

GraphKey = Literal["neo4j", "wikidata"]
graphs: list[GraphKey] = ["neo4j", "wikidata"]


def getGraph(key: GraphKey) -> Graph:
    return {"neo4j": GraphNeo4j, "wikidata": GraphWikidata}[key]()
