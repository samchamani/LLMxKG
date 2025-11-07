from typing import List
import json


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
