import json

system_retrieve_queries = """You are an AI assistant that extracts search terms from a user prompt. 
Your output must always be a valid JSON object with the following fields:

"queries": a list of all significant nouns, proper nouns, or concepts in the prompt. Include implied entities, different spelling and/or synonyms if they are relevant.

Rules:
1. Output only valid JSON; do not include explanations, comments, or extra text.
2. For multiple terms, include them all.
3. If a prompt is ambiguous, include all plausible terms.

Here are some examples:

User: "Who is the mother of the president of the USA?"
Output: { "queries": ["USA", "president"] }

User: "Which companies acquired Twitter and Instagram?"
Output: { "queries": ["Twitter", "Instagram"] }

User: "Who is the CEO of the company that acquired Instagram?"
Output: { "queries": ["Instagram", "company", "CEO"] }

User: "Capitals of European countries with over 5 million people"
Output: { "queries": ["Europe", "capital", "population"] }
"""


system_rate_relationships = """For a given prompt, a current entity, and its relationships, rate the contribution of each relationship to the prompt question on a scale from 0 to 1. 
The sum of the distributed scores must equal 1. 
Your output must always be a valid JSON object with the following fields:

"scores": an array of scores. There must be exactly as many scores as there are relationships and they must be at the same index of the related relationship.
"reason": Your explanation of why you chose to assign these scores.
Here are some examples:

Q: Name the country of the president who said "Yes we can".
Current entity: { "uuid": "some-id", "label": "Barack Obama", "data": "..." }
Relationships: 
[
    { "uuid": "some-id", "type": "MARRIED_TO", "properties": { "data": "..." }, "isOutgoing": true },
    { "uuid": "some-id", "type": "PRESIDENT_OF", "properties": { "data": "..." }, "isOutgoing": true },
    { "uuid": "some-id", "type": "BORN_IN", "properties": { "data": "..." }, "isOutgoing": true }
]
A: 
{
    "scores": [0.0, 1.0, 0.0].
    "reason": "Obama was the president whose slogan was "Yes we can", the "PRESIDENT_OF" relationship will yield his country."
}


Q: Who is the spouse of the author of 'Pride and Prejudice'? 
Current entity: { "uuid": "some-id", "label": "Jane Austen", "data": "..." }
Relationships:
[
    { "uuid": "some-id", "type": "MARRIED_TO", "properties": { "data": "..." }, "isOutgoing": true },
    { "uuid": "some-id", "type": "AUTHORED", "properties": { "data": "..." }, "isOutgoing": true },
    { "uuid": "some-id", "type": "BORN_IN", "properties": { "data": "..." }, "isOutgoing": true }
]
A:
{
    "scores": [1.0, 0.0, 0.0],
    "reason": "The question asks for Jane Austen's spouse. The 'MARRIED_TO' relationship provides this information."
}

Q: What are key factors in the success of the movie 'Inception'?
Current entity: { "uuid": "some-id", "label": "Inception", "data": "..." }
Relationships:
[
    { "uuid": "r1", "type": "DIRECTED_BY", "properties": { "data": "..." }, "isOutgoing": true },
    { "uuid": "r2", "type": "PRODUCED_BY", "properties": { "data": "..." }, "isOutgoing": true },
    { "uuid": "r3", "type": "STARRING", "properties": { "data": "..." }, "isOutgoing": true },
    { "uuid": "r4", "type": "RELEASED_IN", "properties": { "data": "..." }, "isOutgoing": true },
    { "uuid": "r5", "type": "GENRE", "properties": { "data": "..." }, "isOutgoing": true }
]
A:
{
    "scores": [0.4, 0.2, 0.2, 0.1, 0.1],
    "reason": "The success of a movie depends heavily on the director, so 'DIRECTED_BY' gets the highest weight (0.4). 'PRODUCED_BY' and 'STARRING' also contribute significantly to quality and audience appeal, assigned 0.2 each. 'RELEASED_IN' and 'GENRE' have minor influence on success, each receiving 0.1."
}


Q: Who is the CEO of Tesla?
Current entity: { "uuid": "some-id", "label": "Tesla", "data": "..." }
Relationships:
[
    { "uuid": "r1", "type": "CEO", "properties": { "data": "..." }, "isOutgoing": true }
]
A:
{
    "scores": [1.0],
    "reason": "There is only one relationship, 'CEO', which directly answers the question. It receives the full score of 1."
}
"""

system_rate_relationships_label_based = """For a given prompt, a current entity, and its relationships, rate the contribution of each relationship to the prompt question on a scale from 0 to 1. 
Never pretend to know, just guess based on what makes sense.
Your output must always be a valid JSON object with the following fields:

"scores": an array of scores. There must be exactly as many scores as there are relationships. The index of the score must match the index of the relationship. The sum of the scores must equal 1
"reason": Your explanation of why you chose to assign these scores.
Here are some examples:

Q: Name the country of the president who said "Yes we can".
Current entity: "Barack Obama"
Relationships: "-[:MARRIED_TO]->", "-[:PRESIDENT_OF]->", "-[:BORN_IN]->"
A: 
{
    "scores": [0.0, 1.0, 0.0].
    "reason": "Obama was the president whose slogan was "Yes we can", the "PRESIDENT_OF" relationship will yield his country."
}


Q: Who is the spouse of the author of 'Pride and Prejudice'? 
Current entity: "Jane Austen"
Relationships: "-[:MARRIED_TO]->", "-[:AUTHORED]->", "-[:BORN_IN]->"
A:
{
    "scores": [1.0, 0.0, 0.0],
    "reason": "The question asks for Jane Austen's spouse. The 'MARRIED_TO' relationship provides this information."
}

Q: What are key factors in the success of the movie 'Inception'?
Current entity: "Inception"
Relationships: "-[:DIRECTED_BY]->", "-[:PRODUCED_BY]->", "-[:STARRING]->", "-[:RELEASED_IN]->", "-[:GENRE]->"
A:
{
    "scores": [0.4, 0.2, 0.2, 0.1, 0.1],
    "reason": "The success of a movie depends heavily on the director, so 'DIRECTED_BY' gets the highest weight (0.4). 'PRODUCED_BY' and 'STARRING' also contribute significantly to quality and audience appeal, assigned 0.2 each. 'RELEASED_IN' and 'GENRE' have minor influence on success, each receiving 0.1."
}


Q: Who is the CEO of Tesla?
Current entity: "Tesla"
Relationships: "<-[:CEO]-"
A:
{
    "scores": [1.0],
    "reason": "There is only one relationship, 'CEO', which directly answers the question. It receives the full score of 1."
}
"""


def user_rate_relationships(prompt: str, entity: dict, relationships):
    return """Q: {prompt}
Current entity: {entity}
Relationships:
[
    {relationships}
]
""".format(
        prompt=prompt,
        entity=json.dumps(entity),
        relationships=",\n".join([json.dumps(rel) for rel in relationships]),
        length=len(relationships),
    )


def user_rate_relationships_label_based(prompt: str, entity: dict, relationships):
    return """Q: {prompt}
Current entity: "{entity}"
Relationships: {relationships}
""".format(
        prompt=prompt,
        entity=entity["name"],  # change to label later on or change param
        relationships=", ".join(
            [
                f"{"<" if relationship["isOutgoing"] == False else ""}-[:{relationship["type"]}]-{">" if relationship["isOutgoing"] == True else ""}"
                for relationship in relationships
            ]
        ),
    )


system_rate_entities = """Please score the entities' contribution to the question on a scale from 0 to 1 (the sum of the scores of all entities is 1).
Q: The movie featured Miley Cyrus and was produced by Tobin Armbrust?
Entites: [
    { "uuid": "some-id", "label": "The Resident", "data": "...more data..." },
    { "uuid": "some-id", "label": "So Undercover", "data": "...more data..." },
    { "uuid": "some-id", "label": "Let Me In", "data": "...more data..." },
    { "uuid": "some-id", "label": "Begin Again", "data": "...more data..." },
    { "uuid": "some-id", "label": "The Quiet Ones", "data": "...more data..." },
    { "uuid": "some-id", "label": "A Walk Among the Tombstones", "data": "...more data..." }
]

A: 
{ 
    "scores": [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
    "reason": "The movie that matches the given criteria is 'So Undercover' with Miley Cyrus and produced by Tobin Armbrust. Therefore, the score for 'So Undercover' would be 1, and the scores for all other entities would be 0."
}
"""


def user_rate_entities(prompt: str, entities: list):
    return f"""{prompt}
Entities: [
    {",\n".join([json.dumps(entity) for entity in entities])}
]
"""


system_judge_path = """Given a question and the associated retrieved knowledge graph path, you are asked to answer whether it's sufficient for you to answer the question with the path data and your knowledge. Here are some examples.
Q: Find the person who said \"Taste cannot be controlled by law\", what did this person die from?
Knowledge Graph Path: [
    { "uuid": "some-id", "label": "Media Common", "data": "...some data..." },
    { "uuid": "some-id", "type": "QUOTED", isOutgoing: true, "properties": { "data": "Taste cannot be controlled by law" } },
    { "uuid": "some-id", "label": "Thomas Jefferson", "data": "...some data..." },
]
A: 
{
    "canAnswer": false,
    "reason": "Based on the given path, it's not sufficient to answer the entire question. The path data only provides information about the person who said \"Taste cannot be controlled by law,\" which is Thomas Jefferson. To answer the second part of the question, it's necessary to have additional knowledge about Thomas Jefferson's death."
} 

Q: The artist nominated for The Long Winter lived where?
Knowledge Graph Path: [
    { "uuid": "some-id", "label": "The Long Winter", "data": "...more data..." }, 
    { "uuid": "some-id", "type": "WROTE", "isOutgoing": false, "properties": { "data": "...some data..." } },
    { "uuid": "some-id", "label": "Laura Ingalls Wilder",  "data": "...more data..." },
    { "uuid": "some-id", "type": "LIVED_IN", "isOutgoing": true, "properties": { "data": "..some data..." } },
    { "uuid": "some-id", "label": "De Smet", "data": "...some data..." }
]
A:
{
    "canAnswer": true,
    "reason": "Based on the given path, the author of 'The Long Winter' is Laura Ingalls Wilder, who lived in De Smet. Therefore, the question can be answered.",
}

Q: Who is the coach of the team owned by Steve Bisciotti?
Knowledge Graph Path: [
    { "uuid": "some-id", "label": "Steve Bisciotti", "data": "...some data..." },
    { "uuid": "some-id", "type": "OWNS", "isOutgoing": true, "properties": { "data": "...some data..." } },
    { "uuid": "some-id", "label": "Baltimore Ravens", "data": "...some data..." }
]
A:
{
    "canAnswer": false,
    "reason": "Based on the given path, the coach of the team owned by Steve Bisciotti is not explicitly mentioned. However, it can be inferred that the team owned by Steve Bisciotti is the Baltimore Ravens. To determine the coach, additional knowledge about the current coach of the Baltimore Ravens is required."
}

Q: Rift Valley Province is located in a nation that uses which form of currency?
Knowledge Graph Path: [
    { "uuid": "some-id", "label": "Rift Valley Province", "data": "...some data..." },
    { "uuid": "some-id", "type": "LOCATED_IN", "isOutgoing": true, "properties": { "data": "...some data..." } },
    { "uuid": "some-id", "label": "Kenya", "data": "...some data..." },
    { "uuid": "some-id", "type": "CURRENCY_OF", "isOutgoing": false, "properties": { "data": "...some data..." } },
    { "uuid": "some-id", "label": "Kenyan shilling", "data": "...some data..." }
]
A:
{
    "canAnswer": true,
    "reason": "Based on the given path, Rift Valley Province is located in Kenya, which uses the Kenyan shilling as its currency. Therefore, the question can be answered."
}

Q: The country with the National Anthem of Bolivia borders which nations?
Knowledge Graph Path: [
    { "uuid": "some-id", "label": "National Anthem of Bolivia", "data": "...some data..." },
    { "uuid": "some-id", "type": "NATIONAL_ANTHEM_OF", "isOutgoing": true, "properties": { "data": "...some data..." } },
    { "uuid": "some-id", "label": "Bolivia", "data": "...some data..." }
]
A:
{
    "canAnswer": false,
    "reason": "Based on the given path, it can be inferred that the National Anthem of Bolivia belongs to Bolivia. However, there is no information about which nations border Bolivia. Additional geographical knowledge would be required to answer the question."
}
"""


def user_answer(prompt: str, path: list):
    return """{prompt}
Knowledge Graph Path: [
    {paths}
]
""".format(
        prompt=prompt, paths="`\n".join([json.dumps(part) for part in path])
    )


system_answer = """Given a question and the associated retrieved knowledge graph path, you are asked to answer the question with the path data and your knowledge.
Q: Find the person who said \"Taste cannot be controlled by law\", what did this person die from?
Knowledge Graph Path: [
    { "uuid": "some-id", "label": "Media Common", "data": "...some data..." },
    { "uuid": "some-id", "type": "QUOTED", isOutgoing: true, "properties": { "data": "Taste cannot be controlled by law" } },
    { "uuid": "some-id", "label": "Thomas Jefferson", "data": "...some data..." },
]
A: 
{
    "answer": "The person who said 'Taste cannot be controlled by law' is Thomas Jefferson, but I don't have enough information to determine what he died from."
}

Q: The artist nominated for The Long Winter lived where?
Knowledge Graph Path: [
    { "uuid": "some-id", "label": "The Long Winter", "data": "...more data..." }, 
    { "uuid": "some-id", "type": "WROTE", "isOutgoing": false, "properties": { "data": "...some data..." } },
    { "uuid": "some-id", "label": "Laura Ingalls Wilder",  "data": "...more data..." },
    { "uuid": "some-id", "type": "LIVED_IN", "isOutgoing": true, "properties": { "data": "..some data..." } },
    { "uuid": "some-id", "label": "De Smet", "data": "...some data..." }
]
A:
{
    "answer": "The artist associated with 'The Long Winter' is Laura Ingalls Wilder, and she lived in De Smet."
}

Q: Who is the coach of the team owned by Steve Bisciotti?
Knowledge Graph Path: [
    { "uuid": "some-id", "label": "Steve Bisciotti", "data": "...some data..." },
    { "uuid": "some-id", "type": "OWNS", "isOutgoing": true, "properties": { "data": "...some data..." } },
    { "uuid": "some-id", "label": "Baltimore Ravens", "data": "...some data..." }
]
A:
{
    "answer": "Steve Bisciotti owns the Baltimore Ravens, but I don't have information about who the team's coach is."
}


Q: Rift Valley Province is located in a nation that uses which form of currency?
Knowledge Graph Path: [
    { "uuid": "some-id", "label": "Rift Valley Province", "data": "...some data..." },
    { "uuid": "some-id", "type": "LOCATED_IN", "isOutgoing": true, "properties": { "data": "...some data..." } },
    { "uuid": "some-id", "label": "Kenya", "data": "...some data..." },
    { "uuid": "some-id", "type": "CURRENCY_OF", "isOutgoing": false, "properties": { "data": "...some data..." } },
    { "uuid": "some-id", "label": "Kenyan shilling", "data": "...some data..." }
]
A:
{
    "answer": "Rift Valley Province is located in Kenya, which uses the Kenyan shilling as its currency."
}


Q: The country with the National Anthem of Bolivia borders which nations?
Knowledge Graph Path: [
    { "uuid": "some-id", "label": "National Anthem of Bolivia", "data": "...some data..." },
    { "uuid": "some-id", "type": "NATIONAL_ANTHEM_OF", "isOutgoing": true, "properties": { "data": "...some data..." } },
    { "uuid": "some-id", "label": "Bolivia", "data": "...some data..." }
]
A:
{
    "answer": "The National Anthem of Bolivia belongs to Bolivia, but I don’t have information about which nations border Bolivia."
}
"""


system_judge_path_short_relation = """Given a question and the associated retrieved knowledge graph path, you are asked to answer whether it's sufficient for you to answer the question with the path data and your knowledge. Here are some examples.
Q: Find the person who said \"Taste cannot be controlled by law\", what did this person die from?
Knowledge Graph Path:
    Entity: { "uuid": "some-id", "label": "Media Common", "data": "...some data..." }
    Relationship: "-QUOTED->" { "data": "Taste cannot be controlled by law" }
    Entity: { "uuid": "some-id", "label": "Thomas Jefferson", "data": "...some data..." }
A: 
{
    "canAnswer": false,
    "reason": "Based on the given path, it's not sufficient to answer the entire question. The path data only provides information about the person who said \"Taste cannot be controlled by law,\" which is Thomas Jefferson. To answer the second part of the question, it's necessary to have additional knowledge about Thomas Jefferson's death."
} 

Q: The artist nominated for The Long Winter lived where?
Knowledge Graph Path:
    Entity: { "uuid": "some-id", "label": "The Long Winter", "data": "...more data..." }
    Relationship: "<-WROTE-" { "data": "...some data..." }
    Entity: { "uuid": "some-id", "label": "Laura Ingalls Wilder",  "data": "...more data..." }
    Relationship: "-LIVED_IN->" { "data": "..some data..." }
    Entity: { "uuid": "some-id", "label": "De Smet", "data": "...some data..." }
A:
{
    "canAnswer": true,
    "reason": "Based on the given path, the author of 'The Long Winter' is Laura Ingalls Wilder, who lived in De Smet. Therefore, the question can be answered.",
}

Q: Who is the coach of the team owned by Steve Bisciotti?
Knowledge Graph Path:
    Entity: { "uuid": "some-id", "label": "Steve Bisciotti", "data": "...some data..." }
    Relationship: "-OWNS->" { "data": "...some data..." }
    Entity: { "uuid": "some-id", "label": "Baltimore Ravens", "data": "...some data..." }
A:
{
    "canAnswer": false,
    "reason": "Based on the given path, the coach of the team owned by Steve Bisciotti is not explicitly mentioned. However, it can be inferred that the team owned by Steve Bisciotti is the Baltimore Ravens. To determine the coach, additional knowledge about the current coach of the Baltimore Ravens is required."
}

Q: Rift Valley Province is located in a nation that uses which form of currency?
Knowledge Graph Path:
    Entity: { "uuid": "some-id", "label": "Rift Valley Province", "data": "...some data..." }
    Relationship: "-LOCATED_IN->" { "data": "...some data..." }
    Entity: { "uuid": "some-id", "label": "Kenya", "data": "...some data..." }
    Relationship: "<-CURRENCY_OF-" { "data": "...some data..." }
    Entity: { "uuid": "some-id", "label": "Kenyan shilling", "data": "...some data..." }
A:
{
    "canAnswer": true,
    "reason": "Based on the given path, Rift Valley Province is located in Kenya, which uses the Kenyan shilling as its currency. Therefore, the question can be answered."
}

Q: The country with the National Anthem of Bolivia borders which nations?
Knowledge Graph Path:
    Entity: { "uuid": "some-id", "label": "National Anthem of Bolivia", "data": "...some data..." }
    Relationship: "-NATIONAL_ANTHEM_OF->" { "data": "...some data..." }
    Entity: { "uuid": "some-id", "label": "Bolivia", "data": "...some data..." }
A:
{
    "canAnswer": false,
    "reason": "Based on the given path, it can be inferred that the National Anthem of Bolivia belongs to Bolivia. However, there is no information about which nations border Bolivia. Additional geographical knowledge would be required to answer the question."
}
"""


def user_answer_short_relation(prompt: str, path: list):
    paths = ""
    for i, part in enumerate(path):
        if i % 2 == 0:
            paths += f"\tEntity: {part}\n"
        else:
            rel = (
                f'"-{part["type"]}->"' if part["isOutgoing"] else f'"<-{part["type"]}-"'
            )
            paths += f"\tRelationship: {rel} {part["properties"]}\n"
    return f"""{prompt}
Knowledge Graph Path:
    {paths}
"""


system_answer_short_relation = """Given a question and the associated retrieved knowledge graph path, you are asked to answer the question with the path data and your knowledge.
Q: Find the person who said \"Taste cannot be controlled by law\", what did this person die from?
Knowledge Graph Path:
    Entity: { "uuid": "some-id", "label": "Media Common", "data": "...some data..." }
    Relationship: "-QUOTED->" { "data": "Taste cannot be controlled by law" }
    Entity: { "uuid": "some-id", "label": "Thomas Jefferson", "data": "...some data..." }
A: 
{
    "answer": "The person who said 'Taste cannot be controlled by law' is Thomas Jefferson, but I don't have enough information to determine what he died from."
}

Q: The artist nominated for The Long Winter lived where?
Knowledge Graph Path:
    Entity: { "uuid": "some-id", "label": "The Long Winter", "data": "...more data..." }
    Relationship: "<-WROTE-" { "data": "...some data..." }
    Entity: { "uuid": "some-id", "label": "Laura Ingalls Wilder",  "data": "...more data..." }
    Relationship: "-LIVED_IN->" { "data": "..some data..." }
    Entity: { "uuid": "some-id", "label": "De Smet", "data": "...some data..." }
A:
{
    "answer": "The artist associated with 'The Long Winter' is Laura Ingalls Wilder, and she lived in De Smet."
}

Q: Who is the coach of the team owned by Steve Bisciotti?
Knowledge Graph Path:
    Entity: { "uuid": "some-id", "label": "Steve Bisciotti", "data": "...some data..." }
    Relationship: "-OWNS->" { "data": "...some data..." }
    Entity: { "uuid": "some-id", "label": "Baltimore Ravens", "data": "...some data..." }
A:
{
    "answer": "Steve Bisciotti owns the Baltimore Ravens, but I don't have information about who the team's coach is."
}


Q: Rift Valley Province is located in a nation that uses which form of currency?
Knowledge Graph Path:
    Entity: { "uuid": "some-id", "label": "Rift Valley Province", "data": "...some data..." }
    Relationship: "-LOCATED_IN->" { "data": "...some data..." }
    Entity: { "uuid": "some-id", "label": "Kenya", "data": "...some data..." }
    Relationship: "<-CURRENCY_OF-" { "data": "...some data..." }
    Entity: { "uuid": "some-id", "label": "Kenyan shilling", "data": "...some data..." }
A:
{
    "answer": "Rift Valley Province is located in Kenya, which uses the Kenyan shilling as its currency."
}


Q: The country with the National Anthem of Bolivia borders which nations?
Knowledge Graph Path:
    Entity: { "uuid": "some-id", "label": "National Anthem of Bolivia", "data": "...some data..." }
    Relationship: "-NATIONAL_ANTHEM_OF->" { "data": "...some data..." }
    Entity: { "uuid": "some-id", "label": "Bolivia", "data": "...some data..." }
A:
{
    "answer": "The National Anthem of Bolivia belongs to Bolivia, but I don’t have information about which nations border Bolivia."
}
"""
