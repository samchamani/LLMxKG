import requests


class GraphWikidata:

    def __init__(
        self,
        endpoint_url="https://query.wikidata.org/sparql",
        user_agent="MyApp/1.0 (https://mydomain.example; contact@example.com)",
    ):
        self.endpoint_url = endpoint_url
        self.headers = {
            "Accept": "application/sparql-results+json",
            "User-Agent": user_agent,
        }

    def query(self, sparql: str, params: dict = None) -> dict:
        """Executes a SPARQL query string and returns JSON results."""
        response = requests.get(
            self.endpoint_url,
            params={"query": sparql, **(params or {})},
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()


# Usage:
client = GraphWikidata()
sparql = """
SELECT ?country ?countryLabel WHERE {
  ?country wdt:P31 wd:Q6256.   # instance of country
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 5
"""
result = client.query(sparql)
print("CHECK", result)
for binding in result["results"]["bindings"]:
    print(binding["countryLabel"]["value"], binding["country"]["value"])
