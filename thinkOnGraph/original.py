from agents import Agent
from graphs import Graph
from utils import getBest, printPaths, fixScoreArray
import json
from utils.errors import FormatError, ToGException, InstructionError


def thinkOnGraph(
    prompt: str,
    agent: Agent,
    graph: Graph,
    max_paths: int,
    max_depth: int,
    topic_entities: list = None,
    forgiveScoreMismatch: bool = False,
) -> str:
    try:
        # ------------------------ Step 1: Find initial entities ------------------------ #
        # This part is different from ToG, as we expect no given seed entity.
        # The agent is supposed to infer keywords that potentially help
        # finding initial entities and keep the `max_paths` best entities

        # ------------------------------ INITIALIZATION ------------------------------ #
        # Trying to find initial seed entities based on topic entities if given, otherwise
        # based on search queries derived from the prompt
        seed_entities = None
        if len(topic_entities):
            print("Topic entities present. Looking for entities on graph")
            seed_entities = graph.find(topic_entities)
        else:
            print("Looking for seed entities to start")
            search_terms = agent.retrieve_queries(prompt)["queries"]
            if len(search_terms) == 0:
                raise ToGException()
            print(f"searching entities with: {search_terms}")
            seed_entities = graph.find(search_terms)
        if not len(seed_entities):
            raise ToGException()
        print(f"Found seed entities {seed_entities}")

    #     candidate_paths = [[entity] for entity in seed_entities]
    #     print("Initializing top paths based on entity rating")
    #     ratings = agent.rate_entities(prompt, seed_entities)
    #     paths = getBest(candidate_paths, ratings["scores"], max_paths)
    #     print(f"Rating: {ratings['scores']}")
    #     print(f"Rating reason: {ratings["reason"]}")
    #     print("Top paths:")
    #     printPaths(paths)

    #     for iteration in range(max_depth):
    #         print(f"\nIteration {iteration}")
    #         # --------------------- Step 2: Relationship exploration --------------------- #
    #         print("Exploring relationships")
    #         candidate_paths = []
    #         ratings = []
    #         for index, path in enumerate(paths):
    #             triplets: list = graph.read_neighbors([{"uuid": path[-1]["uuid"]}])
    #             candidate_relationships = []
    #             for triplet in triplets:
    #                 # Skipping already known relationships. Same entities are allowed.
    #                 if any(
    #                     [
    #                         part["uuid"] == triplet["relationship"]["uuid"]
    #                         for part in path
    #                     ]
    #                 ):
    #                     continue
    #                 candidate_relationships.append(triplet["relationship"])
    #                 candidate_paths.append(
    #                     path + [triplet["relationship"], triplet["to"]]
    #                 )
    #             # Keeping dead end paths as they are
    #             if len(candidate_relationships) == 0:
    #                 candidate_relationships.append(path[-2])
    #                 candidate_paths.append(path)

    #             candidate_ratings = agent.rate_relationships(
    #                 prompt,
    #                 entity=path[-1],
    #                 relationships=candidate_relationships,
    #             )
    #             print(
    #                 f"Rating reason for path {index} and {len(candidate_relationships)} relationships:"
    #             )
    #             print(candidate_ratings["scores"])
    #             print(candidate_ratings["reason"])
    #             if len(candidate_ratings["scores"]) != len(candidate_relationships):
    #                 if not forgiveScoreMismatch:
    #                     raise FormatError(
    #                         f"path {index} has a mismatch of relationship count and scores count"
    #                     )
    #                 candidate_ratings["scores"] = fixScoreArray(
    #                     candidate_ratings["scores"], len(candidate_relationships)
    #                 )
    #             ratings.extend(candidate_ratings["scores"])
    #         print(
    #             f"Found a total of {len(candidate_relationships)} candidate relationships:"
    #         )
    #         print(
    #             "\n".join(["\t" + json.dumps(rel) for rel in candidate_relationships])
    #         )
    #         paths = getBest(candidate_paths, ratings, max_paths)
    #         print("New top paths:")
    #         printPaths(paths)
    #         # ------------------------ Step 3: Entity exploration ------------------------ #
    #         # In this setup this step doesnt seem to make much difference,
    #         # it just changes the order...
    #         print("Reevaluating with connected entities")
    #         ratings = agent.rate_entities(prompt, [path[-1] for path in paths])
    #         paths = getBest(paths, ratings["scores"], max_paths)
    #         print("New sorting of top paths:")
    #         printPaths(paths)
    #         print(ratings["reason"])
    #         # ------------------------------ Step 4: Reason ------------------------------ #
    #         print("Reasoning over paths with context")
    #         context = []
    #         for i, path in enumerate(paths):
    #             judged, history = agent.judge_path(prompt, path, [])
    #             context.extend(history)
    #             print(f"{i}: {judged["reason"]}")
    #             if judged["canAnswer"]:
    #                 print("Answer found:\n")
    #                 return agent.answer(prompt, path, context)["answer"]
    #     print("Maximum depth reached")
    #     raise ToGException()

    except ToGException:
        # ----------------------------- Step X: Fallback ----------------------------- #
        # if results from ToG are insufficient to answer the prompt
        print("Using only model knowledge to answer question")
        return agent.answer(prompt)
    except FormatError as e:
        print("Format error", e)
    except InstructionError as e:
        print("Instructions were not followed!", e)
    except Exception as e:
        print("Error occured", e)
