from agents import AgentOllama
import os, json

current_dir = os.path.dirname(__file__)
q_path = os.path.join(current_dir, "..", "questions", "qald_10-en.json")
q_path = os.path.abspath(q_path)

with open(q_path) as f:
    questions = json.load(f)

questions = [questions[1]]
agent = AgentOllama(model="llama3.1:8b-instruct-q6_K")

for question in questions:
    prompt = question["question"]
    answer = question["answer"]
    print("Prompt:", prompt)
    print(
        "Agent:",
        agent.answer(prompt + " -- Mark the answer with like so {some answer}"),
    )
    print("Actual answer:", answer)
