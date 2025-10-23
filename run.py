import argparse
from utils import getAgent, agents
from GraphClient import GraphClient
from thinkOnGraph import thinkOnGraph


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, help="Question to ask the system")
    parser.add_argument(
        "--agent",
        choices=agents,
        help="Language Model to use as agent",
    )
    # parser.add_argument(
    #     "--graph",
    #     choices=[],
    #     help="The neo4j knowledge graph to use",
    # )
    # parser.add_argument(
    #     "--max-paths",
    #     type=int,
    #     help="The maximum number of best paths to maintain",
    # )
    # parser.add_argument(
    #     "--max-depth",
    #     type=int,
    #     help="The maximum number of jumps allowed",
    # )
    # parser.add_argument(
    #     "--forgive-score-mismatch",
    #     type=bool,
    #     help="Adjusts the score array if it has a wrong size",
    # )

    args = parser.parse_args()
    print(f"Prompt: {args.prompt}")
    print(f"Using {args.agent} as agent")

    answer = thinkOnGraph(
        prompt=args.prompt,
        agent=getAgent(args.agent),
        graph=GraphClient(),
        max_paths=3,
        max_depth=3,
        forgiveScoreMismatch=True,
    )

    print(answer)
