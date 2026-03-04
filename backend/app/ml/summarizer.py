import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(_env_path)
except ImportError:
    pass


class DocumentSummarizer:
    """Document auto-summarization using LLM."""
    def __init__(self):
        self.initialized = False
        self.llm = None
        self.prompt = None

    def initialize(self):
        if self.initialized:
            return

        if not os.environ.get("OPENAI_API_KEY"):
            print("OPENAI_API_KEY is not set. Summarizer cannot initialize.")
            return

        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.prompts import PromptTemplate

            self.llm = ChatOpenAI(temperature=0.2, model="gpt-3.5-turbo")

            TEMPLATE = """You are an expert technical writer.
Summarize the following document into exactly 3 concise bullet points.
Return only the 3 bullet points, no intro, no outro.
Document Content:
{content}
"""
            self.prompt = PromptTemplate(
                template=TEMPLATE,
                input_variables=["content"],
            )
            self.initialized = True
        except Exception as e:
            print(f"Error initializing Summarizer: {e}")

    def summarize(self, content: str) -> str:
        """Generate a 3-bullet-point summary."""
        if not content or len(content.strip()) < 20:
            return "• Document is too short to summarize.\n"

        if not self.initialized:
            self.initialize()

        if not self.initialized or not self.llm:
            return "• AI summarization unavailable. Please check API keys."

        try:
            chain = self.prompt | self.llm
            result = chain.invoke({"content": content[:3000]})
            return result.content
        except Exception as e:
            return f"• Error generating summary: {e}"

summarizer = DocumentSummarizer()
