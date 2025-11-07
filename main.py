import argparse
from utils import getAgent, agents, getGraph, graphs

from thinkOnGraph import tog_original, tog_variation


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, help="Question to ask the system")
    parser.add_argument(
        "--agent",
        choices=agents,
        help="Language Model to use as agent",
    )
    parser.add_argument(
        "--graph",
        choices=graphs,
        help="The knowledge graph to use",
    )
    parser.add_argument(
        "--max-paths",
        type=int,
        help="The maximum number of best paths to maintain",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        help="The maximum number of jumps allowed",
    )
    # parser.add_argument(
    #     "--forgive-score-mismatch",
    #     type=bool,
    #     help="Adjusts the score array if it has a wrong size",
    # )

    args = parser.parse_args()
    print(f"Prompt: {args.prompt}")
    print(f"Agent: {args.agent}")
    print(f"Graph: {args.graph}")
    print(f"Maximum jumps within path: {args.max_depth}")
    print(f"Maximum top paths maintained: {args.max_paths}")
    print("\n\n")

    answer = tog_original(
        prompt=args.prompt,
        agent=getAgent(args.agent),
        graph=getGraph(args.graph),
        max_paths=args.max_paths,
        max_depth=args.max_depth,
        topic_entities=[],
        forgiveScoreMismatch=True,
    )

    print("\nThink-on-Graph answer:")
    print(answer)
