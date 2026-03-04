import os
from pathlib import Path
from typing import Dict, Any, List

try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(_env_path)
except ImportError:
    pass

try:
    from ..config import settings
except Exception:
    settings = None

class GraphRAG:
    """Natural Language to Cypher engine using LangChain and OpenAI."""
    def __init__(self):
        self.initialized = False
        self.chain = None
        self.graph = None

    def initialize(self):
        if self.initialized:
            return

        # Ideally, API key should come from env or settings. Here we'll rely on env
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("⚠️ OPENAI_API_KEY is not set. GraphRAG cannot initialize.")
            return

        try:
            from langchain_community.graphs import Neo4jGraph
            from langchain.chains import GraphCypherQAChain
            from langchain_openai import ChatOpenAI
            from langchain_core.prompts import PromptTemplate

            # Read Neo4j config from env vars or settings, with correct defaults
            neo4j_uri = os.environ.get("NEO4J_URI") or (getattr(settings, 'neo4j_uri', None) if settings else None) or 'bolt://localhost:7687'
            neo4j_user = os.environ.get("NEO4J_USER") or (getattr(settings, 'neo4j_user', None) if settings else None) or 'neo4j'
            neo4j_password = os.environ.get("NEO4J_PASSWORD") or (getattr(settings, 'neo4j_password', None) if settings else None) or 'expertlink123'

            print(f"🔗 GraphRAG connecting to Neo4j at {neo4j_uri} as {neo4j_user}...")

            self.graph = Neo4jGraph(
                url=neo4j_uri,
                username=neo4j_user,
                password=neo4j_password
            )

            # Define schema explicitly or let LangChain refresh it
            self.graph.refresh_schema()

            llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", api_key=api_key)

            CYPHER_GENERATION_TEMPLATE = """Task: Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
The cypher should return the properties of the nodes, not the nodes themselves.
Question: {question}"""

            cypher_prompt = PromptTemplate(
                template=CYPHER_GENERATION_TEMPLATE,
                input_variables=["schema", "question"],
            )

            self.chain = GraphCypherQAChain.from_llm(
                llm,
                graph=self.graph,
                verbose=True,
                cypher_prompt=cypher_prompt,
                return_direct=False,
            )
            self.initialized = True
            print("✅ GraphRAG initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing GraphRAG: {e}")

    def query(self, question: str) -> Dict[str, Any]:
        """Convert natural language to Cypher and execute."""
        if not self.initialized:
            self.initialize()

        if not self.initialized or not self.chain:
            return {
                "message": "AI Assistant is currently unavailable due to missing API keys or database connection.",
                "data": None
            }

        try:
            response = self.chain.invoke({"query": question})
            return {
                "message": response.get("result", "I couldn't find an answer to that."),
                "data": None # In a full impl, we might want to attach raw cypher results here
            }
        except Exception as e:
            return {
                "message": f"Sorry, I encountered an error while processing your request: {e}",
                "data": None
            }

graph_rag = GraphRAG()
