# application generated custom id as per recommandations from docs
# https://neo4j.com/docs/cypher-manual/5/functions/scalar/#functions-elementid
create = """
UNWIND $data_list AS data
CREATE (node{labels})
SET node += data,
    node.uuid = randomUUID()
RETURN node AS result
"""


read = """
UNWIND $data_list AS data
MATCH (node{labels})
WHERE ALL(k IN keys(data) WHERE
  (lower(toString(node[k])) CONTAINS lower(toString(data[k])))
  OR node[k] = data[k]
)
RETURN node AS result
"""

find = """
UNWIND $data_list AS data
MATCH (node{labels})
WHERE ANY(k IN keys(node) WHERE lower(toString(node[k])) CONTAINS lower(data))
RETURN node AS result
"""

update = """
UNWIND $data_list AS data
MATCH (node{labels})
WHERE ALL(k IN keys(data) WHERE
  (lower(toString(node[k])) CONTAINS lower(toString(data[k])))
  OR node[k] = data[k]
)
SET node += apoc.map.removeKey($new_data, 'uuid')
RETURN node AS result
"""

delete = """
UNWIND $data_list AS data
MATCH (node{labels})
WHERE ALL(k IN keys(data) WHERE
  (lower(toString(node[k])) CONTAINS lower(toString(data[k])))
  OR node[k] = data[k]
)
DETACH DELETE node
RETURN node AS result
"""

link = """
UNWIND $from_list AS from
MATCH (a)
WHERE ALL(k IN keys(from) WHERE
  (lower(toString(a[k])) CONTAINS lower(toString(from[k])))
  OR a[k] = from[k]
)
UNWIND $to_list AS to
MATCH (b)
WHERE ALL(k IN keys(to) WHERE
  (lower(toString(b[k])) CONTAINS lower(toString(to[k])))
  OR b[k] = to[k]
)
MERGE (a)-[edge{rel_type}]->(b)
SET edge.uuid = coalesce(edge.uuid, randomUUID())
SET edge += apoc.map.removeKey(coalesce($relationship_props, {{}}), 'uuid')
RETURN 
  a AS from, 
  {{ uuid: edge.uuid, type: type(edge), properties: properties(edge), isOutgoing: startNode(edge) = a }} AS relationship,
  b AS to
"""

unlink = """
UNWIND $from_list AS from
MATCH (a)
WHERE ALL(k IN keys(from) WHERE
  (lower(toString(a[k])) CONTAINS lower(toString(from[k])))
  OR a[k] = from[k]
)
WITH a
UNWIND $to_list AS to
MATCH (b)
WHERE ALL(k IN keys(to) WHERE
  (lower(toString(b[k])) CONTAINS lower(toString(to[k])))
  OR b[k] = to[k]
)
MATCH (a)-[edge{rel_type}]-{direction}(b)
WITH a, b, edge, coalesce($relationship_props, {{}}) AS rel_props
WHERE ALL(k IN keys(rel_props) WHERE
  (lower(toString(edge[k])) CONTAINS lower(toString(rel_props[k])))
  OR edge[k] = rel_props[k]
)
DELETE edge
RETURN 
  a AS from, 
  {{ uuid: edge.uuid, type: type(edge), properties: properties(edge), isOutgoing: startNode(edge) = a }} AS relationship,
  b AS to
"""

read_link = """
UNWIND $from_list AS from
MATCH (a)
WHERE ALL(k IN keys(from) WHERE
  (lower(toString(a[k])) CONTAINS lower(toString(from[k])))
  OR a[k] = from[k]
)
WITH a
UNWIND $to_list AS to
MATCH (b)
WHERE ALL(k IN keys(to) WHERE
  (lower(toString(b[k])) CONTAINS lower(toString(to[k])))
  OR b[k] = to[k]
)
MATCH (a)-[edge{rel_type}]-{direction}(b)
WITH a, b, edge, coalesce($relationship_props, {{}}) AS rel_props
WHERE ALL(k IN keys(rel_props) WHERE
  (lower(toString(edge[k])) CONTAINS lower(toString(rel_props[k])))
  OR edge[k] = rel_props[k]
)
RETURN 
  a AS from, 
  {{ uuid: edge.uuid, type: type(edge), properties: properties(edge), isOutgoing: startNode(edge) = a }} AS relationship,
  b AS to
"""

read_neighbors = """
UNWIND $data_list AS data
MATCH path = (n)-[edge{rel_type}]-{direction}(neighbor)
WHERE ALL(k IN keys(data) WHERE
  (lower(toString(n[k])) CONTAINS lower(toString(data[k])))
  OR n[k] = data[k]
)
RETURN 
  n AS from, 
  {{ uuid: edge.uuid, type: type(edge), properties: properties(edge), isOutgoing: startNode(edge) = n }} AS relationship,
  neighbor AS to
"""
