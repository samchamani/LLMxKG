from neo4j import GraphDatabase, Transaction
from dotenv import load_dotenv
import os
from typing import Literal, List
import queries
import re


# TODO: add db_name for performance
class GraphClient:

    def __init__(self):
        print("Loading environment variables...")
        load_dotenv()
        host = os.getenv("NEO4J_HOST", "localhost")
        user = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        bolt_port = os.getenv("NEO4J_BOLT_PORT", 7687)
        uri = f"bolt://{host}:{bolt_port}"
        try:
            print(f"Connecting to Neo4j at {uri}...")
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            print("Connected to Neo4j successfully!")
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            raise e

    def close(self):
        """Close the Neo4j driver."""
        if self.driver:
            self.driver.close()
            print("Neo4j connection closed")

    def _run_query(
        self, mode: Literal["read", "write"], query: str, key="result", **kwparameters
    ):
        try:
            with self.driver.session() as session:
                execute = (
                    session.execute_read if mode == "read" else session.execute_write
                )
                result = execute(self._run_tx, query, key, **kwparameters)
                return result
        except Exception as e:
            print(f"Failed to {mode}", e)

    @staticmethod
    def _run_tx(tx: Transaction, query: str, key: str | None, **kwparameters):
        results = tx.run(query, **kwparameters)

        return [
            record.data() if key is None else record.data()[key] for record in results
        ]

    @staticmethod
    def _format_query(
        query: str,
        labels: List[str] = [],
        rel_type: str = "RELATED_TO",
        ignore_direction=False,
    ):
        if rel_type != "" and not re.match(r"[A-Z][A-Z_]*", rel_type):
            raise ValueError("Invalid relationship label")
        return query.format(
            labels=f":{":".join(labels)}" if len(labels) > 0 else "",
            rel_type=f":{rel_type}" if rel_type else "",
            direction="" if ignore_direction else ">",
        )

    # ---------------------------------------------------------------------------- #
    #                                  OPERATIONS                                  #
    # ---------------------------------------------------------------------------- #

    def create(self, data_list: List[dict], labels: List[str] = ["node"]):
        """Create nodes given a `data_list` array of format
        ```
        [
            {
                "prop1": "value1",
                "prop2": "value2",
                ...
            }
        ]
        ```
        """
        query = self._format_query(queries.create, labels)
        return self._run_query("write", query, data_list=data_list)

    def read(self, data_list: List[dict], labels: List[str] = []):
        query = self._format_query(queries.read, labels)
        return self._run_query("read", query, data_list=data_list)

    def find(self, data_list: List[str], labels: List[str] = []):
        """find nodes that contain strings in `data_list`"""
        query = self._format_query(queries.find, labels)
        return self._run_query("read", query, data_list=data_list)

    def update(self, data_list: List[dict], new_data: dict, labels: List[str] = []):
        query = self._format_query(queries.update, labels)
        return self._run_query("write", query, data_list=data_list, new_data=new_data)

    def delete(self, data_list: List[dict], labels: List[str] = []):
        query = self._format_query(queries.delete, labels)
        return self._run_query("write", query, data_list=data_list)

    def link(
        self,
        from_list: List[dict],
        rel_type: str = "RELATED_TO",
        to_list: List[dict] = [],
        relationship_props: dict = None,
    ):
        """
        can be used to create links or update existing ones
        """
        query = self._format_query(queries.link, rel_type=rel_type)
        return self._run_query(
            "write",
            query,
            key=None,
            from_list=from_list,
            to_list=to_list,
            relationship_props=relationship_props,
        )

    def unlink(
        self,
        from_list: List[dict] = [],
        relation: str | dict = "",
        to_list: List[dict] = [],
        ignore_direction=False,
    ):
        isStr = isinstance(relation, str)
        query = self._format_query(
            queries.unlink,
            rel_type=relation if isStr else "",
            ignore_direction=ignore_direction,
        )
        return self._run_query(
            "write",
            query,
            key=None,
            from_list=from_list,
            to_list=to_list,
            relationship_props={} if isStr else relation,
        )

    def read_link(
        self,
        from_list: List[dict] = [],
        relation: str | dict = "",
        to_list: List[dict] = [],
        ignore_direction=False,
    ):
        isStr = isinstance(relation, str)
        query = self._format_query(
            queries.read_link,
            rel_type=relation if isStr else "",
            ignore_direction=ignore_direction,
        )
        return self._run_query(
            "read",
            query,
            key=None,
            from_list=from_list,
            to_list=to_list,
            relationship_props={} if isStr else relation,
        )

    def read_neighbors(self, data_list: List[dict], rel_type="", ignore_direction=True):
        query = self._format_query(
            queries.read_neighbors, rel_type=rel_type, ignore_direction=ignore_direction
        )
        return self._run_query("read", query, key=None, data_list=data_list)

    def read_path(self, data_list: List[dict | str], ignore_direction=True):
        """
        Usage:
        ```
        edges = kg.read_path(
            [sam, "CHILD_OF", afsaneh, "CHILD_OF", diana, "CHILD_OF", ilayda, "CHILD_OF", eray],
        )
        for edge in edges:
            print(f"{edge["from"]["name"]}--{edge["type"]}->{edge["to"]["name"]}")

        ```
        """
        result = []
        for i, _ in enumerate(data_list):
            if i >= len(data_list) - 2:
                break
            if i % 2 == 0:
                edge = self.read_link(
                    [data_list[i]],
                    data_list[i + 1],
                    [data_list[i + 2]],
                    ignore_direction,
                )
                if len(edge) == 0:
                    print(
                        f"Path incomplete: no relationship found for {data_list[i]} {data_list[i + 1]} {data_list[i + 2]}"
                    )
                    return []
                result.extend(edge)
        return result
